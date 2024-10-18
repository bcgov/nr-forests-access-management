
import logging

from api.app.constants import T
from api.app.schemas.pagination import PagedResultsSchema, PageParamsSchema
from pydantic import BaseModel
from sqlalchemy import Select, UnaryExpression, func, select
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)

class PaginateService:
    def __init__(
            self,
            db: Session,
            base_query: Select,
            order_by_criteria: UnaryExpression | None,
            page_param: PageParamsSchema
        ):
        self.db = db  # SqlAlchemy session.
        self.base_query = base_query  # Select query statement.
        self.__order_by_criteria = order_by_criteria
        self.__page_params__ = page_param
        self.page = page_param.page
        self.size = page_param.size
        self.limit = self.size
        self.offset = (self.page - 1) * self.size

    def get_paginated_results(self, ResultSchema: BaseModel) -> PagedResultsSchema[T]:
        """
        Paginate the query results.
        """
        LOGGER.debug(f"Obtaining paginated results with page params: {self.__page_params__}")
        paged_query = self.__apply_order_by(self.base_query)
        paged_query = paged_query.offset(self.offset).limit(self.limit)
        total_counts = self.__get_total_count()
        results = PagedResultsSchema[ResultSchema](
            total=total_counts,
            number_of_pages=self.__get_number_of_pages(total_counts),
            page_number=self.page,
            page_size=self.size,
            results=[ResultSchema.model_validate(item) for item in self.db.scalars(paged_query)]
        )
        return results

    def __get_total_count(self) -> int:
        count = self.db.scalar(select(func.count()).select_from(self.base_query.subquery()))
        return count

    def __get_number_of_pages(self, count: int) -> int:
        rest = count % self.size
        quotient = count // self.size
        return quotient if not rest else quotient + 1

    def __apply_order_by(self, q: Select) -> Select:
        LOGGER.debug(f"Applying order_by criteria: {self.__order_by_criteria}")
        if self.__order_by_criteria is not None:
              q = q.order_by(self.__order_by_criteria)
        return q
