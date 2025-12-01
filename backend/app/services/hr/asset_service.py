"""Asset Service"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date

from app.services.base import CRUDBase
from app.models.hr.asset import Asset, AssetType, AssetStatus
from app.schemas.hr.asset import AssetCreate, AssetUpdate


class AssetService(CRUDBase[Asset, AssetCreate, AssetUpdate]):
    """Service for asset management operations"""

    def get_by_courier(
        self,
        db: Session,
        *,
        courier_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Asset]:
        """
        Get all assets assigned to a courier

        Args:
            db: Database session
            courier_id: ID of the courier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of asset records
        """
        return (
            db.query(self.model)
            .filter(self.model.courier_id == courier_id)
            .order_by(self.model.issue_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        *,
        status: AssetStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Asset]:
        """
        Get assets by status

        Args:
            db: Database session
            status: Asset status to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of asset records
        """
        return (
            db.query(self.model)
            .filter(self.model.status == status)
            .order_by(self.model.issue_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_type(
        self,
        db: Session,
        *,
        asset_type: AssetType,
        skip: int = 0,
        limit: int = 100
    ) -> List[Asset]:
        """
        Get assets by type

        Args:
            db: Database session
            asset_type: Asset type to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of asset records
        """
        return (
            db.query(self.model)
            .filter(self.model.asset_type == asset_type)
            .order_by(self.model.issue_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def assign_asset(
        self,
        db: Session,
        *,
        courier_id: int,
        asset_data: AssetCreate
    ) -> Asset:
        """
        Assign a new asset to a courier

        Args:
            db: Database session
            courier_id: ID of the courier
            asset_data: Asset creation data

        Returns:
            Created asset record
        """
        # Ensure courier_id in asset_data matches the provided courier_id
        asset_dict = asset_data.model_dump()
        asset_dict['courier_id'] = courier_id

        # Create asset with ASSIGNED status
        asset = self.model(**asset_dict)
        asset.status = AssetStatus.ASSIGNED

        db.add(asset)
        db.commit()
        db.refresh(asset)
        return asset

    def return_asset(
        self,
        db: Session,
        *,
        asset_id: int,
        return_date: Optional[date] = None,
        condition: Optional[str] = None
    ) -> Optional[Asset]:
        """
        Mark an asset as returned

        Args:
            db: Database session
            asset_id: ID of the asset
            return_date: Date of return (defaults to today)
            condition: Optional condition description

        Returns:
            Updated asset record or None if not found
        """
        asset = db.query(self.model).filter(self.model.id == asset_id).first()
        if not asset:
            return None

        asset.return_date = return_date or date.today()
        asset.status = AssetStatus.RETURNED

        if condition:
            asset.condition = condition

        db.commit()
        db.refresh(asset)
        return asset

    def mark_as_damaged(
        self,
        db: Session,
        *,
        asset_id: int,
        notes: Optional[str] = None
    ) -> Optional[Asset]:
        """
        Mark an asset as damaged

        Args:
            db: Database session
            asset_id: ID of the asset
            notes: Optional notes about the damage

        Returns:
            Updated asset record or None if not found
        """
        asset = db.query(self.model).filter(self.model.id == asset_id).first()
        if not asset:
            return None

        asset.status = AssetStatus.DAMAGED
        asset.condition = "damaged"

        if notes:
            asset.notes = notes

        db.commit()
        db.refresh(asset)
        return asset

    def mark_as_lost(
        self,
        db: Session,
        *,
        asset_id: int,
        notes: Optional[str] = None
    ) -> Optional[Asset]:
        """
        Mark an asset as lost

        Args:
            db: Database session
            asset_id: ID of the asset
            notes: Optional notes about the loss

        Returns:
            Updated asset record or None if not found
        """
        asset = db.query(self.model).filter(self.model.id == asset_id).first()
        if not asset:
            return None

        asset.status = AssetStatus.LOST
        asset.condition = "lost"

        if notes:
            asset.notes = notes

        db.commit()
        db.refresh(asset)
        return asset

    def get_active_assets(
        self,
        db: Session,
        *,
        courier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Asset]:
        """
        Get currently assigned (active) assets

        Args:
            db: Database session
            courier_id: Optional courier ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active asset records
        """
        query = db.query(self.model).filter(self.model.status == AssetStatus.ASSIGNED)

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)

        return (
            query.order_by(self.model.issue_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_statistics(
        self,
        db: Session,
        *,
        courier_id: Optional[int] = None
    ) -> Dict:
        """
        Get asset statistics

        Args:
            db: Database session
            courier_id: Optional courier ID to filter by

        Returns:
            Dictionary with asset statistics
        """
        query = db.query(self.model)

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)

        # Get all assets for calculations
        all_assets = query.all()

        # Count by status
        assigned_count = sum(1 for asset in all_assets if asset.status == AssetStatus.ASSIGNED)
        returned_count = sum(1 for asset in all_assets if asset.status == AssetStatus.RETURNED)
        damaged_count = sum(1 for asset in all_assets if asset.status == AssetStatus.DAMAGED)
        lost_count = sum(1 for asset in all_assets if asset.status == AssetStatus.LOST)

        # Count by type
        uniform_count = sum(1 for asset in all_assets if asset.asset_type == AssetType.UNIFORM)
        mobile_device_count = sum(1 for asset in all_assets if asset.asset_type == AssetType.MOBILE_DEVICE)
        equipment_count = sum(1 for asset in all_assets if asset.asset_type == AssetType.EQUIPMENT)
        tools_count = sum(1 for asset in all_assets if asset.asset_type == AssetType.TOOLS)

        return {
            "total_assets": len(all_assets),
            "by_status": {
                "assigned": assigned_count,
                "returned": returned_count,
                "damaged": damaged_count,
                "lost": lost_count
            },
            "by_type": {
                "uniform": uniform_count,
                "mobile_device": mobile_device_count,
                "equipment": equipment_count,
                "tools": tools_count
            },
            "active_assets": assigned_count,
            "inactive_assets": returned_count + damaged_count + lost_count
        }

    def get_courier_assets_summary(
        self,
        db: Session,
        *,
        courier_id: int
    ) -> Dict:
        """
        Get a summary of all assets for a specific courier

        Args:
            db: Database session
            courier_id: ID of the courier

        Returns:
            Dictionary with courier asset summary
        """
        assets = self.get_by_courier(db, courier_id=courier_id, skip=0, limit=1000)

        active_assets = [asset for asset in assets if asset.status == AssetStatus.ASSIGNED]
        returned_assets = [asset for asset in assets if asset.status == AssetStatus.RETURNED]
        damaged_assets = [asset for asset in assets if asset.status == AssetStatus.DAMAGED]
        lost_assets = [asset for asset in assets if asset.status == AssetStatus.LOST]

        return {
            "courier_id": courier_id,
            "total_assets_issued": len(assets),
            "active_assets": len(active_assets),
            "returned_assets": len(returned_assets),
            "damaged_assets": len(damaged_assets),
            "lost_assets": len(lost_assets),
            "active_asset_details": [
                {
                    "id": asset.id,
                    "type": asset.asset_type,
                    "issue_date": asset.issue_date.isoformat() if asset.issue_date else None,
                    "condition": asset.condition
                }
                for asset in active_assets
            ]
        }


asset_service = AssetService(Asset)
