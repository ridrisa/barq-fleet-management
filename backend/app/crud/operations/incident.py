from app.crud.base import CRUDBase
from app.models.operations.incident import Incident
from app.schemas.operations.incident import IncidentCreate, IncidentUpdate

incident = CRUDBase[Incident, IncidentCreate, IncidentUpdate](Incident)
