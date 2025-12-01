from app.crud.base import CRUDBase
from app.models.operations.route import Route
from app.schemas.operations.route import RouteCreate, RouteUpdate

route = CRUDBase[Route, RouteCreate, RouteUpdate](Route)
