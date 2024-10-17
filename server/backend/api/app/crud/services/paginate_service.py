
import logging

from api.app.constants import T
from api.app.schemas.pagination import PagedResultsSchema, PageParamsSchema
from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)

class PaginateService:
    def __init__(self, db: Session, q: Select, page_param: PageParamsSchema):
        self.db = db  # SqlAlchemy session.
        self.q = q  # Select query statement.
        self.page = page_param.page_number
        self.size = page_param.page_size
        self.limit = self.size
        self.offset = (self.page - 1) * self.size

    def get_paginated_results(self, ResultSchema: BaseModel) -> PagedResultsSchema[T]:
        """
        Paginate the query for results.
        """
        paged_query = self.q.offset(self.offset).limit(self.limit)
        total_counts = self._get_total_count()
        results = PagedResultsSchema[ResultSchema](
            total=total_counts,
            number_of_pages=self._get_number_of_pages(total_counts),
            page_number=self.page,
            page_size=self.size,
            results=[ResultSchema.model_validate(item) for item in self.db.scalars(paged_query)]
        )
        return results

    def _get_total_count(self) -> int:
        count = self.db.scalar(select(func.count()).select_from(self.q.subquery()))
        return count

    def _get_number_of_pages(self, count: int) -> int:
        rest = count % self.size
        quotient = count // self.size
        return quotient if not rest else quotient + 1
