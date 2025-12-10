"""
Sync Accommodation Data from BigQuery salih table to local PostgreSQL

This script:
1. Fetches accommodation data from BigQuery (looker-barqdata-2030.salih or similar)
2. Creates/updates buildings, rooms, beds, and allocations in local PostgreSQL
3. Maps BigQuery fields to local schema

Usage:
    python scripts/sync_accommodation_from_bq.py --discover  # Show BigQuery schema
    python scripts/sync_accommodation_from_bq.py             # Run sync
"""

import argparse
import os
import sys
from datetime import date, datetime
from typing import Optional, Dict, List, Any

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import bigquery
from google.oauth2 import service_account
import psycopg2
from psycopg2.extras import execute_values

# Configuration
BQ_PROJECT = "looker-barqdata-2030"
BQ_DATASET = "salih"  # Update if different
BQ_TABLE = "accommodation"  # Update with actual table name

CREDENTIALS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "credentials.json"
)

# PostgreSQL connection
PG_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "barq_fleet"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres")
}

# Default organization ID
DEFAULT_ORG_ID = 1


def get_bq_client() -> bigquery.Client:
    """Create BigQuery client with credentials"""
    if os.path.exists(CREDENTIALS_PATH):
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_PATH,
            scopes=[
                "https://www.googleapis.com/auth/bigquery",
                "https://www.googleapis.com/auth/cloud-platform"
            ]
        )
        return bigquery.Client(credentials=credentials, project=BQ_PROJECT)
    else:
        # Try Application Default Credentials
        return bigquery.Client(project=BQ_PROJECT)


def discover_schema_for_dataset(client: bigquery.Client, dataset: str):
    """Discover and print the schema of the dataset"""
    print(f"\n{'='*60}")
    print(f"Discovering schema for {BQ_PROJECT}.{dataset}")
    print(f"{'='*60}\n")

    # List all tables in the dataset
    try:
        dataset_ref = client.dataset(dataset, project=BQ_PROJECT)
        tables = list(client.list_tables(dataset_ref))

        print(f"Tables in {dataset}:")
        for table in tables:
            print(f"  - {table.table_id}")

        # Get schema for each table
        for table in tables:
            table_ref = dataset_ref.table(table.table_id)
            table_obj = client.get_table(table_ref)

            print(f"\n{'='*40}")
            print(f"Schema for {table.table_id}:")
            print(f"{'='*40}")
            print(f"Total rows: {table_obj.num_rows}")

            for field in table_obj.schema:
                print(f"  {field.name}: {field.field_type} {'(nullable)' if field.mode == 'NULLABLE' else ''}")

            # Sample data
            query = f"""
            SELECT *
            FROM `{BQ_PROJECT}.{BQ_DATASET}.{table.table_id}`
            LIMIT 3
            """
            try:
                results = list(client.query(query).result())
                if results:
                    print(f"\nSample data (first 3 rows):")
                    for i, row in enumerate(results):
                        print(f"  Row {i+1}: {dict(row)}")
            except Exception as e:
                print(f"  Could not fetch sample: {e}")

    except Exception as e:
        print(f"Error discovering schema: {e}")

        # Try listing all datasets
        print("\nAttempting to list all datasets in project...")
        try:
            datasets = list(client.list_datasets(project=BQ_PROJECT))
            print(f"Available datasets in {BQ_PROJECT}:")
            for ds in datasets:
                print(f"  - {ds.dataset_id}")
        except Exception as e2:
            print(f"Could not list datasets: {e2}")


def fetch_accommodation_from_bq_dataset(client: bigquery.Client, dataset: str, table: str) -> Dict[str, List[Dict]]:
    """
    Fetch accommodation data from BigQuery.

    Returns dict with:
    - buildings: List of building records
    - rooms: List of room records
    - allocations: List of courier-room allocations
    """
    query = f"""
    SELECT *
    FROM `{BQ_PROJECT}.{dataset}.{table}`
    """

    print(f"Fetching accommodation data from BigQuery ({dataset}.{table})...")

    try:
        results = client.query(query).result()
        records = [dict(row) for row in results]
        print(f"Fetched {len(records)} records from BigQuery")
        return {"raw": records}
    except Exception as e:
        print(f"Error fetching data: {e}")
        return {"raw": []}


def transform_accommodation_data(raw_data: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Transform raw BigQuery salih_native data into buildings, rooms, beds, and allocations.

    BigQuery salih_native schema:
    - iqama_number, courier_id, name (courier info)
    - location, city, accommodation_code, accommodation_type
    - room_number, job_title, building_name, floor_number
    - capacity, occupancy, status
    - check_in_date, check_out_date
    """
    buildings = {}
    rooms = {}
    allocations = []

    for record in raw_data:
        # Extract location as building (location field contains building/compound name like "Rimal")
        location = record.get('location') or record.get('building_name')
        city = record.get('city') or 'Unknown'
        accommodation_code = record.get('accommodation_code') or ''
        room_number = record.get('room_number') or ''
        courier_id = record.get('courier_id') or record.get('iqama_number')
        capacity = record.get('capacity') or 4  # Default capacity
        status = record.get('status') or 'Active'

        # Use location + city as building identifier
        if location:
            building_key = f"{location}_{city}"
            if building_key not in buildings:
                buildings[building_key] = {
                    'name': location,
                    'address': f'{location}, {city}',
                    'city': city,
                    'accommodation_code': accommodation_code,
                }

            # Create room entry
            if room_number:
                room_key = f"{building_key}_{room_number}"
                if room_key not in rooms:
                    rooms[room_key] = {
                        'building_key': building_key,
                        'building_name': location,
                        'room_number': str(room_number),
                        'capacity': capacity if capacity else 4,
                        'floor_number': record.get('floor_number'),
                        'accommodation_type': record.get('accommodation_type'),
                    }

            # Create allocation if courier is assigned
            if courier_id and room_number and status == 'Active':
                allocations.append({
                    'courier_id': str(courier_id),  # This is iqama_number in salih_native
                    'iqama_number': record.get('iqama_number'),
                    'courier_name': record.get('name'),
                    'building_key': building_key,
                    'building_name': location,
                    'room_number': str(room_number),
                    'check_in_date': record.get('check_in_date'),
                    'check_out_date': record.get('check_out_date'),
                })

    print(f"  Transformed: {len(buildings)} buildings, {len(rooms)} rooms, {len(allocations)} allocations")

    return {
        'buildings': list(buildings.values()),
        'rooms': list(rooms.values()),
        'allocations': allocations,
    }


def sync_buildings(conn, buildings: List[Dict]) -> Dict[str, int]:
    """Sync buildings to PostgreSQL, return building_key->id mapping"""
    cur = conn.cursor()
    building_ids = {}

    for building in buildings:
        # Use name + city as unique key
        building_key = f"{building['name']}_{building.get('city', 'Unknown')}"

        cur.execute("""
            INSERT INTO buildings (name, address, organization_id, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW())
            ON CONFLICT (name) DO UPDATE SET
                address = EXCLUDED.address,
                updated_at = NOW()
            RETURNING id
        """, (building['name'], building['address'], DEFAULT_ORG_ID))

        result = cur.fetchone()
        if result:
            building_ids[building_key] = result[0]

    conn.commit()
    print(f"  Synced {len(building_ids)} buildings")
    return building_ids


def sync_rooms(conn, rooms: List[Dict], building_ids: Dict[str, int]) -> Dict[str, int]:
    """Sync rooms to PostgreSQL, return room_key->id mapping"""
    cur = conn.cursor()
    room_ids = {}

    for room in rooms:
        # Use building_key for lookup
        building_key = room.get('building_key')
        building_id = building_ids.get(building_key)
        if not building_id:
            print(f"  Warning: Building '{building_key}' not found for room {room['room_number']}")
            continue

        # Room key uses building_key + room_number
        room_key = f"{building_key}_{room['room_number']}"

        cur.execute("""
            INSERT INTO rooms (building_id, room_number, capacity, occupied, status, organization_id, created_at, updated_at)
            VALUES (%s, %s, %s, 0, 'available'::roomstatus, %s, NOW(), NOW())
            ON CONFLICT (building_id, room_number) DO UPDATE SET
                capacity = EXCLUDED.capacity,
                updated_at = NOW()
            RETURNING id
        """, (building_id, room['room_number'], room['capacity'], DEFAULT_ORG_ID))

        result = cur.fetchone()
        if result:
            room_ids[room_key] = result[0]

    conn.commit()
    print(f"  Synced {len(room_ids)} rooms")
    return room_ids


def sync_beds_and_allocations(conn, allocations: List[Dict], room_ids: Dict[str, int]):
    """Sync beds and allocations to PostgreSQL"""
    cur = conn.cursor()

    # Get courier id mapping - try both barq_id and iqama_number
    # salih_native uses iqama_number as courier_id
    cur.execute("SELECT barq_id, id FROM couriers WHERE barq_id IS NOT NULL")
    courier_by_barq = {row[0]: row[1] for row in cur.fetchall()}

    cur.execute("SELECT iqama_number, id FROM couriers WHERE iqama_number IS NOT NULL")
    courier_by_iqama = {row[0]: row[1] for row in cur.fetchall()}

    print(f"  Found {len(courier_by_barq)} couriers by barq_id, {len(courier_by_iqama)} by iqama_number")

    beds_created = 0
    allocations_created = 0
    not_found_couriers = set()

    for alloc in allocations:
        # Room key uses building_key + room_number
        room_key = f"{alloc['building_key']}_{alloc['room_number']}"
        room_id = room_ids.get(room_key)

        # Try to find courier by iqama_number first (salih_native uses iqama as courier_id)
        iqama = alloc.get('iqama_number') or alloc.get('courier_id')
        courier_id = courier_by_iqama.get(iqama) or courier_by_barq.get(iqama)

        if not courier_id and iqama:
            not_found_couriers.add(iqama)

        if not room_id:
            continue

        # Create bed if bed_number specified
        bed_id = None
        bed_number = alloc.get('bed_number') or 1

        bed_status = 'occupied' if courier_id else 'available'
        cur.execute("""
            INSERT INTO beds (room_id, bed_number, status, organization_id, created_at, updated_at)
            VALUES (%s, %s, %s::bedstatus, %s, NOW(), NOW())
            ON CONFLICT (room_id, bed_number) DO UPDATE SET
                status = EXCLUDED.status,
                updated_at = NOW()
            RETURNING id
        """, (room_id, bed_number, bed_status, DEFAULT_ORG_ID))

        result = cur.fetchone()
        if result:
            bed_id = result[0]
            beds_created += 1

        # Create allocation if courier exists
        if courier_id and bed_id:
            alloc_date = alloc.get('check_in_date')
            if isinstance(alloc_date, str):
                try:
                    alloc_date = datetime.strptime(alloc_date[:10], '%Y-%m-%d').date()
                except:
                    alloc_date = date.today()
            elif not alloc_date:
                alloc_date = date.today()

            # Check if allocation already exists for this courier
            cur.execute("""
                SELECT id FROM allocations WHERE courier_id = %s AND release_date IS NULL
            """, (courier_id,))
            existing = cur.fetchone()

            if existing:
                # Update existing allocation
                cur.execute("""
                    UPDATE allocations SET
                        bed_id = %s,
                        allocation_date = %s,
                        updated_at = NOW()
                    WHERE id = %s
                """, (bed_id, alloc_date, existing[0]))
            else:
                # Insert new allocation
                cur.execute("""
                    INSERT INTO allocations (courier_id, bed_id, allocation_date, organization_id, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, NOW(), NOW())
                """, (courier_id, bed_id, alloc_date, DEFAULT_ORG_ID))
            allocations_created += 1

        # Commit every 100 records
        if (beds_created + allocations_created) % 100 == 0:
            conn.commit()

    conn.commit()

    # Update room occupied counts
    cur.execute("""
        UPDATE rooms SET occupied = (
            SELECT COUNT(*) FROM beds b
            JOIN allocations a ON a.bed_id = b.id
            WHERE b.room_id = rooms.id AND a.release_date IS NULL
        )
    """)

    # Update room status based on occupancy (cast to enum type)
    cur.execute("""
        UPDATE rooms SET status = CASE
            WHEN occupied >= capacity THEN 'occupied'::roomstatus
            ELSE 'available'::roomstatus
        END
    """)

    conn.commit()
    cur.close()

    print(f"  Synced {beds_created} beds")
    print(f"  Synced {allocations_created} allocations")
    if not_found_couriers:
        print(f"  Warning: {len(not_found_couriers)} couriers not found in DB (sample: {list(not_found_couriers)[:5]})")


def sync_to_postgres(data: Dict[str, List[Dict]]):
    """Main sync function"""
    conn = psycopg2.connect(**PG_CONFIG)

    try:
        # If raw data, transform it first
        if 'raw' in data and data['raw']:
            print("\nTransforming raw data...")
            data = transform_accommodation_data(data['raw'])

        print("\nSyncing to PostgreSQL...")

        # Sync in order: buildings -> rooms -> beds/allocations
        building_ids = sync_buildings(conn, data.get('buildings', []))
        room_ids = sync_rooms(conn, data.get('rooms', []), building_ids)
        sync_beds_and_allocations(conn, data.get('allocations', []), room_ids)

        print("\nSync completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\nError during sync: {e}")
        raise
    finally:
        conn.close()


def verify_sync():
    """Verify sync results"""
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM buildings")
    buildings = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM rooms")
    rooms = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM beds")
    beds = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM allocations WHERE release_date IS NULL")
    active_allocations = cur.fetchone()[0]

    cur.execute("""
        SELECT b.name, COUNT(r.id) as room_count, SUM(r.occupied) as occupied
        FROM buildings b
        LEFT JOIN rooms r ON r.building_id = b.id
        GROUP BY b.id, b.name
        ORDER BY b.name
        LIMIT 10
    """)
    building_stats = cur.fetchall()

    cur.close()
    conn.close()

    print(f"\n{'='*60}")
    print("PostgreSQL Accommodation Stats:")
    print(f"{'='*60}")
    print(f"  Buildings: {buildings}")
    print(f"  Rooms: {rooms}")
    print(f"  Beds: {beds}")
    print(f"  Active Allocations: {active_allocations}")

    if building_stats:
        print(f"\nBuilding breakdown:")
        for name, room_count, occupied in building_stats:
            print(f"  {name}: {room_count} rooms, {occupied or 0} occupied beds")


def main():
    parser = argparse.ArgumentParser(description='Sync accommodation data from BigQuery to PostgreSQL')
    parser.add_argument('--discover', action='store_true', help='Discover BigQuery schema only')
    parser.add_argument('--verify', action='store_true', help='Verify current sync status')
    parser.add_argument('--dataset', type=str, default='salih', help='BigQuery dataset name')
    parser.add_argument('--table', type=str, default='accommodation', help='BigQuery table name')
    args = parser.parse_args()

    dataset = args.dataset
    table = args.table

    print("="*60)
    print("BigQuery to PostgreSQL Accommodation Sync")
    print(f"Source: {BQ_PROJECT}.{dataset}")
    print("="*60)

    if args.verify:
        verify_sync()
        return

    # Check credentials
    if not os.path.exists(CREDENTIALS_PATH):
        print(f"Warning: Credentials file not found at {CREDENTIALS_PATH}")
        print("Attempting to use Application Default Credentials...")

    bq_client = get_bq_client()

    if args.discover:
        discover_schema_for_dataset(bq_client, dataset)
        return

    # Fetch and sync
    data = fetch_accommodation_from_bq_dataset(bq_client, dataset, table)

    if not data.get('raw'):
        print("No data found in BigQuery")
        sys.exit(1)

    sync_to_postgres(data)
    verify_sync()

    print("\n" + "="*60)
    print("Sync completed!")
    print("="*60)


if __name__ == "__main__":
    main()
