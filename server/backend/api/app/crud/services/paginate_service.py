
from api.app.constants import T
from api.app.schemas.pagination import PagedResultsSchema, PageParamsSchema
from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session


class PaginateService:
    def __init__(self, db: Session, query: Select, page_param: PageParamsSchema):
        self.db = db
        self.query = query
        self.page = page_param.page_number
        self.size = page_param.page_size
        self.limit = self.size
        self.offset = (self.page - 1) * self.size

    def get_paginated_results(self, ResultSchema: BaseModel) -> PagedResultsSchema[T]:
        """
        Paginate the query for results.
        """
        paged_query = self.query.offset(self.offset).limit(self.limit)
        total_counts = self._get_total_count()
        return PagedResultsSchema[ResultSchema](
            total=total_counts,
            number_of_pages=self._get_number_of_pages(total_counts),
            page_number=self.page,
            page_size=self.size,
            results=[ResultSchema.model_validate(item) for item in paged_query.all()]  # TODO, might need mapping.
        )

    def _get_total_count(self) -> int:
        count = self.db.scalar(select(func.count()).select_from(self.query.subquery()))
        return count

    def _get_number_of_pages(self, count: int) -> int:
        rest = count % self.per_page
        quotient = count // self.per_page
        return quotient if not rest else quotient + 1
