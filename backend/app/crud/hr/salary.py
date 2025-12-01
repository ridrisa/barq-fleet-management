from app.crud.base import CRUDBase
from app.models.hr.salary import Salary
from app.schemas.hr.salary import SalaryCreate, SalaryUpdate

salary = CRUDBase[Salary, SalaryCreate, SalaryUpdate](Salary)
