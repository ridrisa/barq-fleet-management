"""Seed data from CSV files into the database"""
import sys
import csv
from pathlib import Path
from datetime import datetime, date
from typing import Optional
import re

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.fleet.courier import Courier, CourierStatus, SponsorshipStatus, ProjectType
from app.models.fleet.vehicle import Vehicle, VehicleStatus, VehicleType, OwnershipType, FuelType
from app.models.fleet.vehicle_log import VehicleLog, LogType


# CSV file paths
COURIER_CSV = "/Users/ramiz_new/Downloads/Asset Managment  - COURIER MASTER SHEET.csv"
VEHICLES_CSV = "/Users/ramiz_new/Downloads/Inspections - Vehicles.csv"
CAR_LOGS_CSV = "/Users/ramiz_new/Downloads/Inspections - Car logs.csv"


def parse_date(date_str: str) -> Optional[date]:
    """Parse various date formats"""
    if not date_str or date_str.strip() == "" or date_str == "#N/A":
        return None

    date_str = date_str.strip()
    formats = [
        "%m/%d/%Y",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%m/%d/%y",
        "%d/%m/%y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return None


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse various datetime formats"""
    if not dt_str or dt_str.strip() == "" or dt_str == "#N/A":
        return None

    dt_str = dt_str.strip()
    formats = [
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue

    return None


def clean_string(val: str) -> Optional[str]:
    """Clean string value"""
    if not val or val.strip() == "" or val == "#N/A" or val == "N/A":
        return None
    return val.strip()


def clean_int(val: str) -> Optional[int]:
    """Clean integer value"""
    if not val or val.strip() == "":
        return None
    try:
        return int(float(val.strip()))
    except (ValueError, TypeError):
        return None


def clean_float(val: str) -> Optional[float]:
    """Clean float value"""
    if not val or val.strip() == "":
        return None
    try:
        return float(val.strip())
    except (ValueError, TypeError):
        return None


def map_courier_status(status: str) -> CourierStatus:
    """Map CSV status to CourierStatus enum"""
    if not status:
        return CourierStatus.ONBOARDING

    status_lower = status.lower().strip()

    if "active" in status_lower and "not" not in status_lower:
        return CourierStatus.ACTIVE
    elif "not active" in status_lower or "inactive" in status_lower or "not_active" in status_lower:
        return CourierStatus.INACTIVE
    elif "leave" in status_lower:
        return CourierStatus.ON_LEAVE
    elif "terminated" in status_lower or "termination" in status_lower:
        return CourierStatus.TERMINATED
    elif "onboard" in status_lower or "trial" in status_lower:
        return CourierStatus.ONBOARDING
    elif "suspend" in status_lower:
        return CourierStatus.SUSPENDED
    else:
        return CourierStatus.INACTIVE


def map_sponsorship_status(sponsorship: str) -> SponsorshipStatus:
    """Map CSV sponsorship to SponsorshipStatus enum"""
    if not sponsorship:
        return SponsorshipStatus.INHOUSE

    sponsorship_lower = sponsorship.lower().strip()

    if "ajeer" in sponsorship_lower:
        return SponsorshipStatus.AJEER
    elif "inhouse" in sponsorship_lower or "in house" in sponsorship_lower or "in-house" in sponsorship_lower:
        return SponsorshipStatus.INHOUSE
    elif "trial" in sponsorship_lower:
        return SponsorshipStatus.TRIAL
    elif "freelancer" in sponsorship_lower or "free" in sponsorship_lower:
        return SponsorshipStatus.FREELANCER
    else:
        return SponsorshipStatus.INHOUSE


def map_project_type(project: str) -> ProjectType:
    """Map CSV project to ProjectType enum"""
    if not project:
        return ProjectType.BARQ

    project_lower = project.lower().strip()

    if "ecommerce" in project_lower or "e-commerce" in project_lower:
        return ProjectType.ECOMMERCE
    elif "food" in project_lower or "shawarmar" in project_lower or "hunger" in project_lower:
        return ProjectType.FOOD
    elif "warehouse" in project_lower:
        return ProjectType.WAREHOUSE
    elif "hq" in project_lower or "barq" in project_lower:
        return ProjectType.BARQ
    else:
        return ProjectType.MIXED


def map_vehicle_status(last_action: str) -> VehicleStatus:
    """Map CSV last action to VehicleStatus enum"""
    if not last_action:
        return VehicleStatus.ACTIVE

    action_lower = last_action.lower().strip()

    if "to courier" in action_lower:
        return VehicleStatus.ACTIVE
    elif "to agency" in action_lower:
        return VehicleStatus.INACTIVE
    elif "to barq" in action_lower:
        return VehicleStatus.ACTIVE
    elif "maintenance" in action_lower:
        return VehicleStatus.MAINTENANCE
    elif "repair" in action_lower:
        return VehicleStatus.REPAIR
    elif "total loss" in action_lower or "retired" in action_lower:
        return VehicleStatus.RETIRED
    else:
        return VehicleStatus.ACTIVE


def map_ownership_type(contract_type: str) -> OwnershipType:
    """Map CSV contract type to OwnershipType enum"""
    if not contract_type:
        return OwnershipType.LEASED

    contract_lower = contract_type.lower().strip()

    if "yearly" in contract_lower or "lease" in contract_lower:
        return OwnershipType.LEASED
    elif "owned" in contract_lower or "own" in contract_lower:
        return OwnershipType.OWNED
    elif "rent" in contract_lower or "replacement" in contract_lower:
        return OwnershipType.RENTED
    else:
        return OwnershipType.LEASED


def map_vehicle_type(model: str) -> VehicleType:
    """Guess vehicle type from model name"""
    if not model:
        return VehicleType.CAR

    model_lower = model.lower().strip()

    motorcycles = ["bike", "motorcycle", "scooter", "vespa"]
    vans = ["van", "partner", "boxer", "transit", "sprinter", "hiace"]
    trucks = ["truck", "lorry", "pickup", "hilux"]

    for m in motorcycles:
        if m in model_lower:
            return VehicleType.MOTORCYCLE
    for v in vans:
        if v in model_lower:
            return VehicleType.VAN
    for t in trucks:
        if t in model_lower:
            return VehicleType.TRUCK

    return VehicleType.CAR


def seed_couriers(db: Session) -> dict:
    """Seed couriers from CSV"""
    print("\n📋 Seeding couriers from CSV...")

    courier_map = {}  # barq_id -> courier_id
    iqama_map = {}    # iqama_number -> courier_id

    try:
        with open(COURIER_CSV, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0
            skipped = 0

            for row in reader:
                barq_id = clean_string(row.get('BARQ ID'))
                if not barq_id:
                    skipped += 1
                    continue

                # Check if courier already exists
                existing = db.query(Courier).filter(Courier.barq_id == barq_id).first()
                if existing:
                    courier_map[barq_id] = existing.id
                    iqama = clean_string(row.get('id_number'))
                    if iqama:
                        iqama_map[iqama] = existing.id
                    continue

                # Create new courier
                iqama_number = clean_string(row.get('id_number'))
                email = clean_string(row.get('Email'))

                # Make email unique if needed
                if email:
                    existing_email = db.query(Courier).filter(Courier.email == email).first()
                    if existing_email:
                        email = f"{barq_id}_{email}"

                courier = Courier(
                    barq_id=barq_id,
                    full_name=clean_string(row.get('Name')) or f"Courier {barq_id}",
                    email=email,
                    mobile_number=clean_string(row.get('mobile_number')) or "000000000",
                    city=clean_string(row.get('City')),
                    status=map_courier_status(row.get('Status')),
                    sponsorship_status=map_sponsorship_status(row.get('Sponsorshipstatus')),
                    project_type=map_project_type(row.get('Project')),
                    joining_date=parse_date(row.get('Joining Date')),
                    last_working_day=parse_date(row.get('last working day')),
                    iqama_number=iqama_number,
                    iqama_expiry_date=parse_date(row.get('Iqama Expiry Date')),
                    nationality=clean_string(row.get('Nationality')),
                    date_of_birth=parse_date(row.get('Date Of Birth')),
                    passport_number=clean_string(row.get('Passport Number')),
                    passport_expiry_date=parse_date(row.get('Passport Expiry Date')),
                    license_number=clean_string(row.get('License Number')),
                    license_expiry_date=parse_date(row.get('License Expiry Date')),
                    iban=clean_string(row.get('IBAN')),
                    bank_name=clean_string(row.get('Bank Name')),
                    supervisor_name=clean_string(row.get('Supervisor')),
                    jahez_driver_id=clean_string(row.get('Jahez Driver ID')),
                    hunger_rider_id=clean_string(row.get('Hunger Rider ID')),
                    mrsool_courier_id=clean_string(row.get('Mrsool iCourierID')),
                )

                db.add(courier)
                db.flush()  # Get the ID

                courier_map[barq_id] = courier.id
                if iqama_number:
                    iqama_map[iqama_number] = courier.id

                count += 1

                if count % 100 == 0:
                    print(f"  Processed {count} couriers...")

            db.commit()
            print(f"  ✓ Imported {count} couriers (skipped {skipped})")

    except FileNotFoundError:
        print(f"  ⚠ File not found: {COURIER_CSV}")
    except Exception as e:
        print(f"  ❌ Error importing couriers: {e}")
        db.rollback()
        raise

    return {"barq_map": courier_map, "iqama_map": iqama_map}


def seed_vehicles(db: Session, courier_maps: dict) -> dict:
    """Seed vehicles from CSV"""
    print("\n🚗 Seeding vehicles from CSV...")

    vehicle_map = {}  # plate_number -> vehicle_id
    iqama_map = courier_maps.get("iqama_map", {})

    try:
        with open(VEHICLES_CSV, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0
            skipped = 0

            for row in reader:
                plate_letters = clean_string(row.get('Plate letters')) or ""
                plate_numbers = clean_string(row.get('Plate numbers')) or ""

                if not plate_letters and not plate_numbers:
                    skipped += 1
                    continue

                plate_number = f"{plate_numbers}{plate_letters}".strip()
                if not plate_number:
                    skipped += 1
                    continue

                # Check if vehicle already exists
                existing = db.query(Vehicle).filter(Vehicle.plate_number == plate_number).first()
                if existing:
                    vehicle_map[plate_number] = existing.id
                    continue

                make = clean_string(row.get('Make')) or "Unknown"
                model = clean_string(row.get('Model')) or "Unknown"
                year = clean_int(row.get('Year')) or 2020

                vehicle = Vehicle(
                    plate_number=plate_number,
                    make=make,
                    model=model,
                    year=year,
                    color=clean_string(row.get('Color')),
                    vehicle_type=map_vehicle_type(model),
                    status=map_vehicle_status(row.get('Last Action')),
                    ownership_type=map_ownership_type(row.get('Contract Type')),
                    assigned_to_city=clean_string(row.get('City')),
                    assigned_to_project=clean_string(row.get('Department')),
                    monthly_lease_cost=clean_float(row.get('Monthly Rent')),
                    fuel_type=FuelType.GASOLINE,
                )

                db.add(vehicle)
                db.flush()

                vehicle_map[plate_number] = vehicle.id

                # Link courier if available
                courier_iqama = clean_string(row.get('Courier IQAMA'))
                if courier_iqama and courier_iqama in iqama_map:
                    courier = db.query(Courier).filter(Courier.id == iqama_map[courier_iqama]).first()
                    if courier and vehicle.status == VehicleStatus.ACTIVE:
                        courier.current_vehicle_id = vehicle.id

                count += 1

                if count % 100 == 0:
                    print(f"  Processed {count} vehicles...")

            db.commit()
            print(f"  ✓ Imported {count} vehicles (skipped {skipped})")

    except FileNotFoundError:
        print(f"  ⚠ File not found: {VEHICLES_CSV}")
    except Exception as e:
        print(f"  ❌ Error importing vehicles: {e}")
        db.rollback()
        raise

    return vehicle_map


def seed_vehicle_logs(db: Session, courier_maps: dict, vehicle_map: dict) -> None:
    """Seed vehicle logs from CSV"""
    print("\n📝 Seeding vehicle logs from CSV...")

    iqama_map = courier_maps.get("iqama_map", {})
    barq_map = courier_maps.get("barq_map", {})

    try:
        with open(CAR_LOGS_CSV, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0
            skipped = 0

            for row in reader:
                plate_letters = clean_string(row.get('Cars Plate letter english')) or ""
                plate_numbers = clean_string(row.get('Car Plate numbers')) or ""
                plate_number = f"{plate_numbers}{plate_letters}".strip()

                if not plate_number or plate_number not in vehicle_map:
                    skipped += 1
                    continue

                vehicle_id = vehicle_map[plate_number]

                # Find courier
                courier_id = None
                courier_iqama = clean_string(row.get('Courier ID (IQAMA Number) رقم هوية المندوب'))
                courier_barq_id = clean_string(row.get('Courier BARQ ID'))

                if courier_iqama and courier_iqama in iqama_map:
                    courier_id = iqama_map[courier_iqama]
                elif courier_barq_id and courier_barq_id in barq_map:
                    courier_id = barq_map[courier_barq_id]

                # Parse log date
                log_date = parse_date(row.get('Date التاريخ '))
                if not log_date:
                    timestamp = parse_datetime(row.get('Timestamp'))
                    if timestamp:
                        log_date = timestamp.date()
                    else:
                        log_date = date.today()

                # Parse odometer
                odometer = clean_float(row.get('Odometer reading'))

                # Create log
                vehicle_log = VehicleLog(
                    vehicle_id=vehicle_id,
                    courier_id=courier_id,
                    log_type=LogType.TRIP,
                    log_date=log_date,
                    start_mileage=odometer,
                    end_mileage=odometer,
                    notes=clean_string(row.get('Comment التعليق')),
                    recorded_by=clean_string(row.get('Inspector')),
                    start_location=clean_string(row.get('Location')),
                    has_issues=row.get('هل يوجد ضرر في المركبة is there damage in the car?', '').upper() == 'TRUE',
                )

                db.add(vehicle_log)
                count += 1

                if count % 500 == 0:
                    db.commit()
                    print(f"  Processed {count} vehicle logs...")

            db.commit()
            print(f"  ✓ Imported {count} vehicle logs (skipped {skipped})")

    except FileNotFoundError:
        print(f"  ⚠ File not found: {CAR_LOGS_CSV}")
    except Exception as e:
        print(f"  ❌ Error importing vehicle logs: {e}")
        db.rollback()
        raise


def print_summary(db: Session):
    """Print summary of imported data"""
    print("\n" + "="*50)
    print("📊 IMPORT SUMMARY")
    print("="*50)

    courier_count = db.query(Courier).count()
    vehicle_count = db.query(Vehicle).count()
    log_count = db.query(VehicleLog).count()

    active_couriers = db.query(Courier).filter(Courier.status == CourierStatus.ACTIVE).count()
    inactive_couriers = db.query(Courier).filter(Courier.status == CourierStatus.INACTIVE).count()
    active_vehicles = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.ACTIVE).count()

    couriers_with_vehicle = db.query(Courier).filter(Courier.current_vehicle_id.isnot(None)).count()

    print(f"\n📋 Couriers: {courier_count}")
    print(f"   - Active: {active_couriers}")
    print(f"   - Inactive: {inactive_couriers}")
    print(f"   - With Vehicle: {couriers_with_vehicle}")

    print(f"\n🚗 Vehicles: {vehicle_count}")
    print(f"   - Active: {active_vehicles}")

    print(f"\n📝 Vehicle Logs: {log_count}")

    # Status breakdown
    print("\n📊 Courier Status Breakdown:")
    for status in CourierStatus:
        count = db.query(Courier).filter(Courier.status == status).count()
        if count > 0:
            print(f"   - {status.value}: {count}")

    print("\n📊 Sponsorship Breakdown:")
    for sponsorship in SponsorshipStatus:
        count = db.query(Courier).filter(Courier.sponsorship_status == sponsorship).count()
        if count > 0:
            print(f"   - {sponsorship.value}: {count}")

    print("\n📊 Project Type Breakdown:")
    for project in ProjectType:
        count = db.query(Courier).filter(Courier.project_type == project).count()
        if count > 0:
            print(f"   - {project.value}: {count}")


def main():
    """Main function to seed CSV data"""
    print("="*50)
    print("🚀 BARQ Fleet Management - CSV Data Import")
    print("="*50)

    db = SessionLocal()

    try:
        # Seed couriers first
        courier_maps = seed_couriers(db)

        # Seed vehicles and link to couriers
        vehicle_map = seed_vehicles(db, courier_maps)

        # Seed vehicle logs
        seed_vehicle_logs(db, courier_maps, vehicle_map)

        # Print summary
        print_summary(db)

        print("\n✅ CSV data import completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during import: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
