"""
Sync Couriers from BigQuery master_saned_native.courier to local PostgreSQL

This script:
1. Fetches all couriers from BigQuery (with platform IDs, documents, etc.)
2. Upserts them into local PostgreSQL (insert or update on conflict)
3. Maps BigQuery fields to local schema accurately
"""

import os
import sys
from datetime import date
from typing import Optional

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import bigquery
from google.oauth2 import service_account
import psycopg2
from psycopg2.extras import execute_values

# Configuration
BQ_PROJECT = "looker-barqdata-2030"
BQ_DATASET = "master_saned_native"
BQ_TABLE = "courier"
CREDENTIALS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "credentials.json"
)

# PostgreSQL connection
PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "barq_fleet",
    "user": "postgres",
    "password": "postgres"
}

# Default organization ID
DEFAULT_ORG_ID = 1


def get_bq_client():
    """Create BigQuery client with credentials"""
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=[
            "https://www.googleapis.com/auth/bigquery",
            "https://www.googleapis.com/auth/cloud-platform"
        ]
    )
    return bigquery.Client(credentials=credentials, project=BQ_PROJECT)


def fetch_couriers_from_bq(client: bigquery.Client) -> list:
    """Fetch all couriers from BigQuery with all fields"""
    query = f"""
    SELECT
        CAST(BARQ_ID AS STRING) as barq_id,
        Name as full_name,
        CAST(id_number AS STRING) as iqama_number,
        Status as status,
        Project as project_type,
        Sponsorshipstatus as sponsorship_status,
        Supervisor as supervisor_name,
        City as city,
        plate as plate_number,
        IBAN as iban,
        Bank_Name as bank_name,
        CAST(mobile_number AS STRING) as mobile_number,
        Email as email,
        Joining_Date as joining_date,
        last_working_day,
        Nationality as nationality,
        Date_Of_Birth as date_of_birth,
        Iqama_Expiry_Date as iqama_expiry_date,
        Passport_Number as passport_number,
        Passport_Expiry_Date as passport_expiry_date,
        CAST(License_Number AS STRING) as license_number,
        License_Expiry_Date as license_expiry_date,
        CAST(Jahez_Driver_ID AS STRING) as jahez_driver_id,
        CAST(Hunger_Rider_ID AS STRING) as hunger_rider_id,
        CAST(Mrsool_icourierid AS STRING) as mrsool_courier_id,
        CAST(Keeta_Courier_Id AS STRING) as keeta_courier_id,
        WPS as wps
    FROM `{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}`
    WHERE BARQ_ID IS NOT NULL
    """

    print(f"Fetching couriers from BigQuery ({BQ_DATASET}.{BQ_TABLE})...")
    results = client.query(query).result()
    couriers = [dict(row) for row in results]
    print(f"Fetched {len(couriers)} couriers from BigQuery")
    return couriers


def map_status(bq_status: Optional[str]) -> str:
    """Map BigQuery status to PostgreSQL enum

    BigQuery values:
    - Active, Not Active, Resigned, Onboarding, Leave, Processing
    - Rejected, Failed Onboarding, RUN AWAY, Suspended, Pending Contract
    - Resignation Requested, Vacation, Inactive, Terminated, etc.

    PostgreSQL enum values (uppercase only - SQLAlchemy model):
    - ACTIVE, INACTIVE, ON_LEAVE, TERMINATED, ONBOARDING, SUSPENDED
    """
    if not bq_status:
        return "ONBOARDING"

    # Normalize to lowercase for comparison
    status_lower = bq_status.strip().lower()

    # Map to uppercase enum values
    if status_lower in ("active",):
        return "ACTIVE"
    elif status_lower in ("inactive", "not active"):
        return "INACTIVE"
    elif status_lower in ("on vacation", "vacation", "leave", "on leave"):
        return "ON_LEAVE"
    elif status_lower in ("resigned", "terminated", "transferred to hr", "run away", "runaway"):
        return "TERMINATED"
    elif status_lower in ("processing", "onboarding"):
        return "ONBOARDING"
    elif status_lower in ("suspended", "rejected", "failed onboarding", "resignation requested", "pending contract"):
        return "SUSPENDED"
    else:
        return "INACTIVE"


def map_sponsorship(bq_sponsorship: Optional[str]) -> str:
    """Map BigQuery sponsorship to PostgreSQL enum

    BigQuery values: Inhouse, Trial, Ajeer, etc.
    PostgreSQL enum: AJEER, INHOUSE, TRIAL, FREELANCER
    """
    if not bq_sponsorship:
        return "INHOUSE"

    sponsorship_map = {
        "Inhouse": "INHOUSE",
        "inhouse": "INHOUSE",
        "In-House": "INHOUSE",
        "INHOUSE": "INHOUSE",
        "In House": "INHOUSE",
        "Ajeer": "AJEER",
        "ajeer": "AJEER",
        "AJEER": "AJEER",
        "Trial": "TRIAL",
        "trial": "TRIAL",
        "TRIAL": "TRIAL",
        "Freelancer": "FREELANCER",
        "freelancer": "FREELANCER",
        "FREELANCER": "FREELANCER",
    }
    return sponsorship_map.get(bq_sponsorship, "INHOUSE")


def map_project_type(bq_project: Optional[str]) -> str:
    """Map BigQuery project to PostgreSQL enum

    BigQuery values:
    - Food In-House New, Ecommerce, Motorcycle
    - Food In-House Old, Keeta Slab Mode, Food Trial
    - Shawarmar, Hunger Station, HQ, Dedicated 10HR
    - Ecommerce WH, WH Saqlain

    PostgreSQL enum: ECOMMERCE, FOOD, WAREHOUSE, BARQ, MIXED
    """
    if not bq_project:
        return "BARQ"

    project_lower = bq_project.lower()

    # Food projects
    if "food" in project_lower or "hunger" in project_lower or "keeta" in project_lower or "shawarmar" in project_lower:
        return "FOOD"
    # Ecommerce projects (but not warehouse)
    elif "ecommerce" in project_lower and "wh" not in project_lower:
        return "ECOMMERCE"
    # Warehouse projects
    elif "warehouse" in project_lower or " wh" in project_lower or project_lower.startswith("wh ") or "ecommerce wh" in project_lower:
        return "WAREHOUSE"
    # Motorcycle is typically FOOD delivery
    elif "motorcycle" in project_lower:
        return "FOOD"
    # HQ, Dedicated are mixed/general
    elif "hq" in project_lower or "dedicated" in project_lower:
        return "MIXED"

    return "BARQ"


def clean_string(value: Optional[str], max_len: int = 255) -> Optional[str]:
    """Clean and truncate string"""
    if not value or str(value).lower() in ('none', 'null', 'nan'):
        return None
    return str(value).strip()[:max_len]


def clean_mobile(mobile: Optional[str]) -> Optional[str]:
    """Clean mobile number"""
    if not mobile:
        return None
    # Remove non-digits except +
    cleaned = ''.join(c for c in str(mobile) if c.isdigit() or c == '+')
    if cleaned and not cleaned.startswith('+') and not cleaned.startswith('966'):
        cleaned = '966' + cleaned
    return cleaned[:20] if cleaned else None


def parse_date(date_val) -> Optional[str]:
    """Parse date value to string format"""
    if not date_val:
        return None
    if hasattr(date_val, 'strftime'):
        return date_val.strftime('%Y-%m-%d')
    try:
        # Try parsing string date
        from datetime import datetime
        if '/' in str(date_val):
            return datetime.strptime(str(date_val), '%m/%d/%Y').strftime('%Y-%m-%d')
        return str(date_val)[:10]
    except:
        return None


def sync_to_postgres(couriers: list):
    """Upsert couriers to PostgreSQL"""
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    # Get existing emails to avoid duplicates
    cur.execute("SELECT email, barq_id FROM couriers WHERE email IS NOT NULL")
    existing_emails = {row[0]: row[1] for row in cur.fetchall()}

    inserted = 0
    updated = 0
    errors = 0
    error_details = []
    new_emails_used = set()

    for courier in couriers:
        try:
            barq_id = clean_string(courier.get('barq_id'), 50)
            if not barq_id:
                continue

            # Map all fields
            full_name = clean_string(courier.get('full_name'), 200) or f"Courier {barq_id}"
            iqama_number = clean_string(courier.get('iqama_number'), 50)
            status = map_status(courier.get('status'))
            sponsorship_status = map_sponsorship(courier.get('sponsorship_status'))
            project_type = map_project_type(courier.get('project_type'))
            city = clean_string(courier.get('city'), 100)
            mobile_number = clean_mobile(courier.get('mobile_number')) or f"966000{barq_id}"  # Fallback if null
            raw_email = clean_string(courier.get('email'), 254)
            # Make email null if it's a duplicate (exists for different barq_id or used in this batch)
            email = None
            if raw_email and '@' in raw_email:
                existing_barq_id = existing_emails.get(raw_email)
                if existing_barq_id is None or existing_barq_id == barq_id:
                    if raw_email not in new_emails_used:
                        email = raw_email
                        new_emails_used.add(raw_email)
            iban = clean_string(courier.get('iban'), 50)
            bank_name = clean_string(courier.get('bank_name'), 100)
            nationality = clean_string(courier.get('nationality'), 100)
            supervisor_name = clean_string(courier.get('supervisor_name'), 200)
            joining_date = parse_date(courier.get('joining_date'))
            last_working_day = parse_date(courier.get('last_working_day'))
            date_of_birth = parse_date(courier.get('date_of_birth'))
            iqama_expiry_date = parse_date(courier.get('iqama_expiry_date'))
            passport_number = clean_string(courier.get('passport_number'), 50)
            passport_expiry_date = parse_date(courier.get('passport_expiry_date'))
            license_number = clean_string(courier.get('license_number'), 50)
            license_expiry_date = parse_date(courier.get('license_expiry_date'))

            # Platform IDs
            jahez_driver_id = clean_string(courier.get('jahez_driver_id'), 50)
            hunger_rider_id = clean_string(courier.get('hunger_rider_id'), 50)
            mrsool_courier_id = clean_string(courier.get('mrsool_courier_id'), 50)

            # Upsert query with all fields
            cur.execute("""
                INSERT INTO couriers (
                    barq_id, full_name, iqama_number, status, sponsorship_status,
                    project_type, city, mobile_number, email, iban, bank_name,
                    nationality, supervisor_name, joining_date, last_working_day,
                    date_of_birth, iqama_expiry_date, passport_number, passport_expiry_date,
                    license_number, license_expiry_date, jahez_driver_id, hunger_rider_id,
                    mrsool_courier_id, organization_id, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, NOW(), NOW()
                )
                ON CONFLICT (barq_id) DO UPDATE SET
                    full_name = EXCLUDED.full_name,
                    iqama_number = COALESCE(EXCLUDED.iqama_number, couriers.iqama_number),
                    status = EXCLUDED.status,
                    sponsorship_status = EXCLUDED.sponsorship_status,
                    project_type = EXCLUDED.project_type,
                    city = COALESCE(EXCLUDED.city, couriers.city),
                    mobile_number = COALESCE(EXCLUDED.mobile_number, couriers.mobile_number),
                    email = COALESCE(EXCLUDED.email, couriers.email),
                    iban = COALESCE(EXCLUDED.iban, couriers.iban),
                    bank_name = COALESCE(EXCLUDED.bank_name, couriers.bank_name),
                    nationality = COALESCE(EXCLUDED.nationality, couriers.nationality),
                    supervisor_name = COALESCE(EXCLUDED.supervisor_name, couriers.supervisor_name),
                    joining_date = COALESCE(EXCLUDED.joining_date, couriers.joining_date),
                    last_working_day = COALESCE(EXCLUDED.last_working_day, couriers.last_working_day),
                    date_of_birth = COALESCE(EXCLUDED.date_of_birth, couriers.date_of_birth),
                    iqama_expiry_date = COALESCE(EXCLUDED.iqama_expiry_date, couriers.iqama_expiry_date),
                    passport_number = COALESCE(EXCLUDED.passport_number, couriers.passport_number),
                    passport_expiry_date = COALESCE(EXCLUDED.passport_expiry_date, couriers.passport_expiry_date),
                    license_number = COALESCE(EXCLUDED.license_number, couriers.license_number),
                    license_expiry_date = COALESCE(EXCLUDED.license_expiry_date, couriers.license_expiry_date),
                    jahez_driver_id = COALESCE(EXCLUDED.jahez_driver_id, couriers.jahez_driver_id),
                    hunger_rider_id = COALESCE(EXCLUDED.hunger_rider_id, couriers.hunger_rider_id),
                    mrsool_courier_id = COALESCE(EXCLUDED.mrsool_courier_id, couriers.mrsool_courier_id),
                    updated_at = NOW()
                RETURNING (xmax = 0) as is_insert
            """, (
                barq_id, full_name, iqama_number, status, sponsorship_status,
                project_type, city, mobile_number, email, iban, bank_name,
                nationality, supervisor_name, joining_date, last_working_day,
                date_of_birth, iqama_expiry_date, passport_number, passport_expiry_date,
                license_number, license_expiry_date, jahez_driver_id, hunger_rider_id,
                mrsool_courier_id, DEFAULT_ORG_ID
            ))

            result = cur.fetchone()
            if result and result[0]:
                inserted += 1
            else:
                updated += 1

            # Commit every 100 records
            if (inserted + updated) % 100 == 0:
                conn.commit()
                print(f"  Progress: {inserted + updated} processed...")

        except Exception as e:
            errors += 1
            error_details.append(f"barq_id={courier.get('barq_id')}: {str(e)[:100]}")
            conn.rollback()
            continue

    conn.commit()
    cur.close()
    conn.close()

    print(f"\nSync completed:")
    print(f"  Inserted: {inserted}")
    print(f"  Updated: {updated}")
    print(f"  Errors: {errors}")
    print(f"  Total processed: {inserted + updated}")

    if error_details and len(error_details) <= 10:
        print(f"\nError details:")
        for err in error_details:
            print(f"  - {err}")
    elif error_details:
        print(f"\nFirst 10 errors:")
        for err in error_details[:10]:
            print(f"  - {err}")


def verify_sync():
    """Verify sync results"""
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM couriers")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM couriers WHERE status = 'Active'")
    active = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM couriers WHERE jahez_driver_id IS NOT NULL")
    with_jahez = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM couriers WHERE iqama_number IS NOT NULL")
    with_iqama = cur.fetchone()[0]

    cur.execute("""
        SELECT barq_id, full_name, status, city, jahez_driver_id
        FROM couriers
        WHERE status = 'Active' AND barq_id ~ '^[0-9]+$'
        ORDER BY barq_id::int
        LIMIT 5
    """)
    sample = cur.fetchall()

    cur.close()
    conn.close()

    print(f"\nPostgreSQL courier stats:")
    print(f"  Total couriers: {total}")
    print(f"  Active couriers: {active}")
    print(f"  With Jahez ID: {with_jahez}")
    print(f"  With Iqama: {with_iqama}")
    print(f"\nSample active couriers:")
    for row in sample:
        print(f"  {row[0]}: {row[1]} ({row[2]}) - {row[3]} - Jahez: {row[4]}")


def main():
    print("=" * 60)
    print("BigQuery to PostgreSQL Courier Sync")
    print(f"Source: {BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}")
    print("=" * 60)

    # Check credentials
    if not os.path.exists(CREDENTIALS_PATH):
        print(f"Error: Credentials file not found at {CREDENTIALS_PATH}")
        sys.exit(1)

    # Fetch from BigQuery
    bq_client = get_bq_client()
    couriers = fetch_couriers_from_bq(bq_client)

    if not couriers:
        print("No couriers found in BigQuery")
        sys.exit(1)

    # Sync to PostgreSQL
    sync_to_postgres(couriers)

    # Verify
    verify_sync()

    print("\n" + "=" * 60)
    print("Sync completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
