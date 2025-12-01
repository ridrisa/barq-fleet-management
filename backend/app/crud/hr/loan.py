from app.crud.base import CRUDBase
from app.models.hr.loan import Loan
from app.schemas.hr.loan import LoanCreate, LoanUpdate

loan = CRUDBase[Loan, LoanCreate, LoanUpdate](Loan)
