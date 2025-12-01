from app.crud.base import CRUDBase
from app.models.fleet.document import Document
from app.schemas.fleet.document import DocumentCreate, DocumentUpdate

document = CRUDBase[Document, DocumentCreate, DocumentUpdate](Document)
