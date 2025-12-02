"""
FMS Sync Service
Synchronizes FMS asset data with BARQ couriers and vehicles.
Matches by barq_id (FMS PlateNumber) or iqama_number (FMS IDNumber).
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.fms.client import get_fms_client
from app.models.fleet.courier import Courier
from app.models.fleet.vehicle import Vehicle

logger = logging.getLogger(__name__)


class FMSSyncService:
    """Service for syncing FMS data with BARQ database."""

    def __init__(self, db: Session):
        self.db = db
        self.fms_client = get_fms_client()

    def get_all_fms_assets(self, max_pages: int = 10) -> List[Dict[str, Any]]:
        """Fetch all FMS assets with pagination."""
        all_assets = []
        page = 1

        while page <= max_pages:
            result = self.fms_client.get_assets(page_size=100, page_index=page)

            if result.get("error"):
                logger.error(f"FMS fetch error on page {page}: {result.get('message')}")
                break

            assets = result.get("result") or []
            if not assets:
                break

            all_assets.extend(assets)
            page += 1

            # Check if we've fetched all
            total_count = result.get("totalCount", 0)
            if len(all_assets) >= total_count:
                break

        logger.info(f"Fetched {len(all_assets)} FMS assets")
        return all_assets

    def match_courier_by_barq_id(self, barq_id: str) -> Optional[Courier]:
        """Find courier by BARQ ID (FMS PlateNumber)."""
        return self.db.query(Courier).filter(Courier.barq_id == barq_id).first()

    def match_courier_by_iqama(self, iqama_number: str) -> Optional[Courier]:
        """Find courier by iqama number (FMS IDNumber)."""
        if not iqama_number:
            return None
        return self.db.query(Courier).filter(Courier.iqama_number == iqama_number).first()

    def match_vehicle_by_plate(self, plate_number: str) -> Optional[Vehicle]:
        """Find vehicle by plate number (FMS AssetName)."""
        if not plate_number:
            return None
        # Try exact match first
        vehicle = self.db.query(Vehicle).filter(Vehicle.plate_number == plate_number).first()
        if vehicle:
            return vehicle
        # Try partial match (plate might have different format)
        return self.db.query(Vehicle).filter(
            Vehicle.plate_number.ilike(f"%{plate_number}%")
        ).first()

    def sync_single_asset(self, asset: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync a single FMS asset to BARQ database.

        Mapping:
        - FMS PlateNumber -> Courier.barq_id
        - FMS IDNumber -> Courier.iqama_number
        - FMS AssetName -> Vehicle.plate_number
        """
        result = {
            "fms_asset_id": asset.get("Id"),
            "asset_name": asset.get("AssetName"),
            "plate_number": asset.get("PlateNumber"),
            "courier_matched": False,
            "vehicle_matched": False,
            "courier_id": None,
            "vehicle_id": None,
        }

        fms_asset_id = asset.get("Id")
        fms_plate_number = asset.get("PlateNumber")  # This is BARQ ID
        fms_asset_name = asset.get("AssetName")  # This is vehicle plate

        tracking_unit = asset.get("Trackingunit", {})
        driver = tracking_unit.get("Driver", {})
        fms_id_number = driver.get("IDNumber")  # This is iqama
        fms_driver_id = driver.get("Id")

        # Try to match courier by BARQ ID first, then by iqama
        courier = self.match_courier_by_barq_id(fms_plate_number)
        if not courier and fms_id_number:
            courier = self.match_courier_by_iqama(fms_id_number)

        if courier:
            # Update courier with FMS data
            courier.fms_asset_id = fms_asset_id
            courier.fms_driver_id = fms_driver_id
            courier.fms_last_sync = datetime.utcnow().isoformat()
            result["courier_matched"] = True
            result["courier_id"] = courier.id
            result["courier_name"] = courier.full_name

        # Try to match vehicle by plate number (AssetName)
        vehicle = self.match_vehicle_by_plate(fms_asset_name)
        if vehicle:
            device_log = tracking_unit.get("DeviceLog", {})
            vehicle.fms_asset_id = fms_asset_id
            vehicle.fms_tracking_unit_id = tracking_unit.get("Id")
            vehicle.fms_last_sync = datetime.utcnow().isoformat()

            # Update mileage from FMS
            fms_mileage = device_log.get("Mileage")
            if fms_mileage:
                try:
                    vehicle.current_mileage = float(fms_mileage)
                except (ValueError, TypeError):
                    pass

            # Update GPS device info
            vehicle.gps_device_imei = tracking_unit.get("IMEI")
            vehicle.is_gps_active = True

            result["vehicle_matched"] = True
            result["vehicle_id"] = vehicle.id
            result["vehicle_plate"] = vehicle.plate_number

        return result

    def sync_all_assets(self) -> Dict[str, Any]:
        """Sync all FMS assets with BARQ database."""
        assets = self.get_all_fms_assets()

        stats = {
            "total_fms_assets": len(assets),
            "couriers_matched": 0,
            "vehicles_matched": 0,
            "unmatched_assets": [],
            "sync_time": datetime.utcnow().isoformat(),
        }

        for asset in assets:
            result = self.sync_single_asset(asset)

            if result["courier_matched"]:
                stats["couriers_matched"] += 1
            if result["vehicle_matched"]:
                stats["vehicles_matched"] += 1

            if not result["courier_matched"] and not result["vehicle_matched"]:
                stats["unmatched_assets"].append({
                    "fms_asset_id": result["fms_asset_id"],
                    "asset_name": result["asset_name"],
                    "barq_id": result["plate_number"],
                })

        # Commit all changes
        self.db.commit()

        logger.info(
            f"FMS Sync complete: {stats['couriers_matched']} couriers, "
            f"{stats['vehicles_matched']} vehicles matched out of {stats['total_fms_assets']} assets"
        )

        return stats

    def get_courier_live_location(self, courier_id: int) -> Optional[Dict[str, Any]]:
        """Get real-time location for a courier from FMS."""
        courier = self.db.query(Courier).filter(Courier.id == courier_id).first()
        if not courier or not courier.fms_asset_id:
            return None

        result = self.fms_client.get_asset_by_id(courier.fms_asset_id)
        if result.get("error"):
            return None

        tracking = result.get("Trackingunit", {})
        device_log = tracking.get("DeviceLog", {})
        driver = tracking.get("Driver", {})

        return {
            "courier_id": courier.id,
            "courier_name": courier.full_name,
            "barq_id": courier.barq_id,
            "fms_asset_id": courier.fms_asset_id,
            "position": {
                "latitude": float(device_log.get("Latitude", 0) or 0),
                "longitude": float(device_log.get("Longitude", 0) or 0),
                "altitude": float(device_log.get("Altitude", 0) or 0),
                "direction": int(device_log.get("Direction", 0) or 0),
            },
            "speed_kmh": float(device_log.get("Speed", 0) or 0),
            "mileage_km": float(device_log.get("Mileage", 0) or 0),
            "signal_strength": int(device_log.get("SignalStrength", 0) or 0),
            "gps_timestamp": device_log.get("GPSDate"),
            "vehicle": {
                "asset_name": result.get("AssetName"),
                "asset_type": result.get("AssetType"),
            },
            "driver_info": {
                "name": driver.get("DriverName"),
                "mobile": driver.get("MobileNumber"),
                "badge": driver.get("BadgeNumber"),
            }
        }

    def get_all_couriers_live_locations(self) -> List[Dict[str, Any]]:
        """Get real-time locations for all couriers with FMS links."""
        # Get all couriers with FMS asset IDs
        couriers = self.db.query(Courier).filter(
            Courier.fms_asset_id.isnot(None)
        ).all()

        if not couriers:
            # If no couriers linked, fetch all FMS assets and return their locations
            assets = self.get_all_fms_assets()
            locations = []

            for asset in assets:
                tracking = asset.get("Trackingunit", {})
                device_log = tracking.get("DeviceLog", {})
                driver = tracking.get("Driver", {})

                lat = device_log.get("Latitude")
                lon = device_log.get("Longitude")
                if not lat or not lon:
                    continue

                locations.append({
                    "fms_asset_id": asset.get("Id"),
                    "barq_id": asset.get("PlateNumber"),
                    "asset_name": asset.get("AssetName"),
                    "driver_name": driver.get("DriverName"),
                    "position": {
                        "latitude": float(lat),
                        "longitude": float(lon),
                    },
                    "speed_kmh": float(device_log.get("Speed", 0) or 0),
                    "gps_timestamp": device_log.get("GPSDate"),
                    "status": "active" if float(device_log.get("Speed", 0) or 0) > 0 else "idle",
                })

            return locations

        # Fetch live data for linked couriers
        locations = []
        for courier in couriers:
            location = self.get_courier_live_location(courier.id)
            if location:
                locations.append(location)

        return locations


def get_sync_service(db: Session) -> FMSSyncService:
    """Factory function to create FMSSyncService."""
    return FMSSyncService(db)
