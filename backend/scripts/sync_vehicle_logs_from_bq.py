"""
Sync Vehicle Logs (Car Assignments) from BigQuery to local PostgreSQL

This script:
1. Fetches vehicle movement logs from BigQuery master_saned.vehicle_logs
2. Creates/updates vehicles in local DB if they don't exist
3. Creates assignment records in courier_vehicle_assignments
4. Creates vehicle_logs records for tracking

Movement Types mapping:
- "To Courier" -> ASSIGN (courier gets car)
- "To BARQ" -> RETURN (courier returns car)
- "Maintenance" -> MAINTENANCE
- "To Agency" -> AGENCY_RETURN
- "To BARQ Staff" -> STAFF_ASSIGN
- "Total Loss" / "Stolen" -> TERMINATED
"""

import os
import sys
from datetime import datetime, date
from typing import Optional, Tuple
import re

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import bigquery
from google.oauth2 import service_account
import psycopg2
from psycopg2.extras import execute_values

# Configuration
BQ_PROJECT = "looker-barqdata-2030"
BQ_DATASET = "master_saned"
BQ_TABLE = "vehicle_logs"
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


def fetch_vehicle_logs_from_bq(client: bigquery.Client) -> list:
    """Fetch all vehicle logs from BigQuery"""
    query = f"""
    SELECT
        Car_Plate,
        Car_Model,
        Rent_Type,
        CAST(Courier_BARQ_ID AS STRING) as courier_barq_id,
        CAST(Courier_ID_IQAMA_Number AS STRING) as courier_iqama,
        Movement_Type,
        Date as log_date,
        Timestamp as log_timestamp,
        Odometer_Reading as mileage,
        Location,
        Comment,
        Inspector,
        Is_There_Damage_In_The_Car as has_damage,
        Description as damage_description,
        Create_Inspection,
        Front_Image,
        Back_Image,
        Drivers_Side_Image,
        Passenger_Side_Image
    FROM `{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}`
    WHERE Car_Plate IS NOT NULL
      AND Movement_Type IS NOT NULL
    ORDER BY Date ASC
    """

    print(f"Fetching vehicle logs from BigQuery ({BQ_DATASET}.{BQ_TABLE})...")
    results = client.query(query).result()
    logs = [dict(row) for row in results]
    print(f"Fetched {len(logs)} vehicle logs from BigQuery")
    return logs


def clean_string(value, max_len: int = 255) -> Optional[str]:
    """Clean and truncate string"""
    if not value or str(value).lower() in ('none', 'null', 'nan', ''):
        return None
    return str(value).strip()[:max_len]


def clean_plate(plate: str) -> Optional[str]:
    """Normalize plate number"""
    if not plate:
        return None
    # Remove spaces and convert to uppercase
    cleaned = re.sub(r'\s+', '', str(plate).upper().strip())
    return cleaned[:20] if cleaned else None


def parse_mileage(mileage_str) -> Optional[int]:
    """Parse mileage string to integer"""
    if not mileage_str:
        return None
    try:
        # Remove commas and non-numeric characters
        cleaned = re.sub(r'[^\d.]', '', str(mileage_str))
        return int(float(cleaned)) if cleaned else None
    except:
        return None


def parse_datetime(dt_val) -> Tuple[Optional[date], Optional[datetime]]:
    """Parse datetime value"""
    if not dt_val:
        return None, None

    if hasattr(dt_val, 'date'):
        return dt_val.date(), dt_val

    try:
        if isinstance(dt_val, str):
            # Try various formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y']:
                try:
                    parsed = datetime.strptime(dt_val[:19], fmt)
                    return parsed.date(), parsed
                except:
                    continue
        return None, None
    except:
        return None, None


def map_movement_to_assignment_type(movement_type: str) -> str:
    """Map BQ movement type to PG assignment type

    PostgreSQL expects (lowercase - matches Python enum values):
    - permanent, temporary, trial
    """
    # All assignments from BQ are treated as permanent
    # since they represent actual vehicle assignments
    return "permanent"


def map_movement_to_status(movement_type: str) -> str:
    """Map BQ movement type to assignment status

    PostgreSQL expects (lowercase - matches Python AssignmentStatus enum):
    - active, completed, cancelled
    """
    if movement_type == "To Courier":
        return "active"
    elif movement_type in ("To BARQ", "To Agency"):
        return "completed"
    elif movement_type == "Maintenance":
        return "cancelled"  # Maintenance ends assignment
    elif movement_type in ("Total Loss", "Stolen"):
        return "cancelled"  # Loss/theft ends assignment
    return "completed"


def extract_model_make(car_model: str) -> Tuple[str, str]:
    """Extract make and model from car_model string"""
    if not car_model:
        return "Unknown", "Unknown"

    # Common car makes
    makes = {
        "Dzire": ("Suzuki", "Dzire"),
        "Accent": ("Hyundai", "Accent"),
        "Boxer": ("Peugeot", "Boxer"),
        "Elantra": ("Hyundai", "Elantra"),
        "Sunny": ("Nissan", "Sunny"),
        "Camry": ("Toyota", "Camry"),
        "Corolla": ("Toyota", "Corolla"),
        "Hilux": ("Toyota", "Hilux"),
        "Fortuner": ("Toyota", "Fortuner"),
        "Patrol": ("Nissan", "Patrol"),
        "Sentra": ("Nissan", "Sentra"),
        "Creta": ("Hyundai", "Creta"),
        "Tucson": ("Hyundai", "Tucson"),
        "Duster": ("Renault", "Duster"),
        "Symbol": ("Renault", "Symbol"),
    }

    car_model_clean = car_model.strip()
    if car_model_clean in makes:
        return makes[car_model_clean]

    return "Unknown", car_model_clean


def get_or_create_vehicle(cur, plate_number: str, car_model: str, rent_type: str) -> Optional[int]:
    """Get existing vehicle or create new one, return vehicle_id"""
    if not plate_number:
        return None

    # Try to find existing vehicle
    cur.execute(
        "SELECT id FROM vehicles WHERE plate_number = %s",
        (plate_number,)
    )
    result = cur.fetchone()
    if result:
        return result[0]

    # Create new vehicle
    make, model = extract_model_make(car_model)
    ownership = "RENTED" if rent_type and "rent" in rent_type.lower() else "OWNED"

    cur.execute("""
        INSERT INTO vehicles (
            plate_number, vehicle_type, make, model, year, status,
            ownership_type, organization_id, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
        )
        RETURNING id
    """, (
        plate_number, "CAR", make, model, 2023, "ACTIVE",
        ownership, DEFAULT_ORG_ID
    ))
    return cur.fetchone()[0]


def get_courier_id(cur, barq_id: str) -> Optional[int]:
    """Get courier database ID from barq_id"""
    if not barq_id:
        return None

    cur.execute(
        "SELECT id FROM couriers WHERE barq_id = %s",
        (str(barq_id),)
    )
    result = cur.fetchone()
    return result[0] if result else None


def sync_to_postgres(logs: list):
    """Sync vehicle logs to PostgreSQL"""
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    # Cache for vehicles and couriers
    vehicle_cache = {}
    courier_cache = {}

    # Track active assignments per vehicle
    active_assignments = {}

    assignments_created = 0
    assignments_closed = 0
    vehicles_created = 0
    logs_created = 0
    errors = 0
    error_details = []

    for i, log in enumerate(logs):
        try:
            plate_number = clean_plate(log.get('Car_Plate'))
            if not plate_number:
                continue

            car_model = clean_string(log.get('Car_Model'))
            rent_type = clean_string(log.get('Rent_Type'))
            courier_barq_id = clean_string(log.get('courier_barq_id'))
            movement_type = clean_string(log.get('Movement_Type'))
            log_date, log_datetime = parse_datetime(log.get('log_date'))
            mileage = parse_mileage(log.get('mileage'))
            location = clean_string(log.get('Location'), 300)
            comment = clean_string(log.get('Comment'), 500)
            inspector = clean_string(log.get('Inspector'), 200)
            has_damage = log.get('has_damage') == 'TRUE'

            if not log_date:
                continue

            # Get or create vehicle
            if plate_number not in vehicle_cache:
                vehicle_id = get_or_create_vehicle(cur, plate_number, car_model, rent_type)
                vehicle_cache[plate_number] = vehicle_id
                if vehicle_id:
                    # Check if this was a new vehicle
                    cur.execute("SELECT created_at FROM vehicles WHERE id = %s", (vehicle_id,))
                    created = cur.fetchone()
                    if created and (datetime.now(created[0].tzinfo) - created[0]).total_seconds() < 5:
                        vehicles_created += 1
            else:
                vehicle_id = vehicle_cache[plate_number]

            if not vehicle_id:
                continue

            # Get courier ID if available
            courier_id = None
            if courier_barq_id:
                if courier_barq_id not in courier_cache:
                    courier_cache[courier_barq_id] = get_courier_id(cur, courier_barq_id)
                courier_id = courier_cache[courier_barq_id]

            # Handle assignments based on movement type
            assignment_type = map_movement_to_assignment_type(movement_type)
            status = map_movement_to_status(movement_type)

            if movement_type == "To Courier" and courier_id:
                # Close any existing active assignment for this vehicle
                if vehicle_id in active_assignments:
                    old_assignment_id = active_assignments[vehicle_id]
                    cur.execute("""
                        UPDATE courier_vehicle_assignments
                        SET status = 'completed', end_date = %s, end_mileage = %s,
                            termination_reason = 'Reassigned', updated_at = NOW()
                        WHERE id = %s AND status = 'active'
                    """, (log_date, mileage, old_assignment_id))
                    if cur.rowcount > 0:
                        assignments_closed += 1

                # Create new assignment
                cur.execute("""
                    INSERT INTO courier_vehicle_assignments (
                        courier_id, vehicle_id, assignment_type, status,
                        start_date, start_mileage, assigned_by, notes,
                        organization_id, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                    )
                    RETURNING id
                """, (
                    courier_id, vehicle_id, assignment_type, status,
                    log_date, mileage, inspector, comment, DEFAULT_ORG_ID
                ))
                assignment_id = cur.fetchone()[0]
                active_assignments[vehicle_id] = assignment_id
                assignments_created += 1

                # Update courier's current_vehicle_id
                cur.execute("""
                    UPDATE couriers SET current_vehicle_id = %s, updated_at = NOW()
                    WHERE id = %s
                """, (vehicle_id, courier_id))

            elif movement_type in ("To BARQ", "To Agency", "Maintenance"):
                # Close active assignment
                if vehicle_id in active_assignments:
                    old_assignment_id = active_assignments[vehicle_id]
                    cur.execute("""
                        UPDATE courier_vehicle_assignments
                        SET status = %s, end_date = %s, end_mileage = %s,
                            termination_reason = %s, updated_at = NOW()
                        WHERE id = %s AND status = 'active'
                    """, (status, log_date, mileage, movement_type, old_assignment_id))
                    if cur.rowcount > 0:
                        assignments_closed += 1
                        del active_assignments[vehicle_id]

                # Clear courier's current_vehicle_id if we know the courier
                if courier_id:
                    cur.execute("""
                        UPDATE couriers SET current_vehicle_id = NULL, updated_at = NOW()
                        WHERE id = %s AND current_vehicle_id = %s
                    """, (courier_id, vehicle_id))

            # Create vehicle_log entry
            log_type_map = {
                "To Courier": "assignment",
                "To BARQ": "return",
                "Maintenance": "maintenance",
                "To Agency": "agency_return",
                "To BARQ Staff": "staff_use",
                "Total Loss": "incident",
                "Stolen": "incident"
            }
            log_type = log_type_map.get(movement_type, "other")

            cur.execute("""
                INSERT INTO vehicle_logs (
                    vehicle_id, courier_id, log_type, log_date, log_time,
                    start_mileage, start_location, notes, recorded_by,
                    has_issues, issues_reported,
                    organization_id, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s,
                    %s, NOW(), NOW()
                )
            """, (
                vehicle_id, courier_id, log_type, log_date,
                log_datetime.time() if log_datetime else None,
                mileage, location, comment, inspector,
                has_damage, log.get('damage_description') if has_damage else None,
                DEFAULT_ORG_ID
            ))
            logs_created += 1

            # Commit every 500 records
            if (i + 1) % 500 == 0:
                conn.commit()
                print(f"  Progress: {i + 1} processed...")

        except Exception as e:
            errors += 1
            error_details.append(f"plate={log.get('Car_Plate')}, date={log.get('log_date')}: {str(e)[:80]}")
            conn.rollback()
            continue

    conn.commit()
    cur.close()
    conn.close()

    print(f"\nSync completed:")
    print(f"  Vehicles created: {vehicles_created}")
    print(f"  Assignments created: {assignments_created}")
    print(f"  Assignments closed: {assignments_closed}")
    print(f"  Vehicle logs created: {logs_created}")
    print(f"  Errors: {errors}")

    if error_details:
        print(f"\nFirst 10 errors:")
        for err in error_details[:10]:
            print(f"  - {err}")


def verify_sync():
    """Verify sync results"""
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM vehicles")
    total_vehicles = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM courier_vehicle_assignments")
    total_assignments = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM courier_vehicle_assignments WHERE status = 'active'")
    active_assignments = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM vehicle_logs")
    total_logs = cur.fetchone()[0]

    cur.execute("""
        SELECT v.plate_number, c.full_name, cva.status, cva.start_date
        FROM courier_vehicle_assignments cva
        JOIN vehicles v ON v.id = cva.vehicle_id
        JOIN couriers c ON c.id = cva.courier_id
        WHERE cva.status = 'active'
        ORDER BY cva.start_date DESC
        LIMIT 5
    """)
    recent = cur.fetchall()

    cur.close()
    conn.close()

    print(f"\nPostgreSQL stats after sync:")
    print(f"  Total vehicles: {total_vehicles}")
    print(f"  Total assignments: {total_assignments}")
    print(f"  Active assignments: {active_assignments}")
    print(f"  Total vehicle logs: {total_logs}")
    print(f"\nRecent active assignments:")
    for row in recent:
        print(f"  {row[0]} -> {row[1]} ({row[2]}) since {row[3]}")


def main():
    print("=" * 60)
    print("BigQuery to PostgreSQL Vehicle Logs Sync")
    print(f"Source: {BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}")
    print("=" * 60)

    # Check credentials
    if not os.path.exists(CREDENTIALS_PATH):
        print(f"Error: Credentials file not found at {CREDENTIALS_PATH}")
        sys.exit(1)

    # Fetch from BigQuery
    bq_client = get_bq_client()
    logs = fetch_vehicle_logs_from_bq(bq_client)

    if not logs:
        print("No vehicle logs found in BigQuery")
        sys.exit(1)

    # Sync to PostgreSQL
    sync_to_postgres(logs)

    # Verify
    verify_sync()

    print("\n" + "=" * 60)
    print("Sync completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
