from app.crud.base import CRUDBase
from app.models.accommodation.room import Room
from app.schemas.accommodation.room import RoomCreate, RoomUpdate

room = CRUDBase[Room, RoomCreate, RoomUpdate](Room)
