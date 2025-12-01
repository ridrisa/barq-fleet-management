from app.crud.base import CRUDBase
from app.models.hr.asset import Asset
from app.schemas.hr.asset import AssetCreate, AssetUpdate

asset = CRUDBase[Asset, AssetCreate, AssetUpdate](Asset)
