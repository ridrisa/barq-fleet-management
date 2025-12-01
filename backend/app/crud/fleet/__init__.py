from app.crud.fleet.courier import courier
from app.crud.fleet.vehicle import vehicle
from app.crud.fleet.assignment import assignment
from app.crud.fleet.maintenance import maintenance
from app.crud.fleet.inspection import inspection
from app.crud.fleet.accident_log import accident_log
from app.crud.fleet.vehicle_log import vehicle_log

__all__ = [
    "courier",
    "vehicle",
    "assignment",
    "maintenance",
    "inspection",
    "accident_log",
    "vehicle_log",
]
