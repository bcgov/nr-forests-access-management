
from sqlalchemy.orm import Session


class PaginatorService:
    def __init__(self, db: Session):
        self.db = db

    def paginate(self):
        pass