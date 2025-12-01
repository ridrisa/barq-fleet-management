from app.crud.base import CRUDBase
from app.models.hr.bonus import Bonus
from app.schemas.hr.bonus import BonusCreate, BonusUpdate

bonus = CRUDBase[Bonus, BonusCreate, BonusUpdate](Bonus)
