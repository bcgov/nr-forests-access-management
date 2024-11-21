
import logging
from enum import StrEnum

from api.app.constants import SortOrderEnum, T
from api.app.schemas.pagination import (PagedResultsSchema, PageParamsSchema,
                                        PageResultMetaSchema)
from pydantic import BaseModel
from sqlalchemy import ColumnElement, Select, asc, desc, func, select
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)

class PaginateService:
    """
    A simple pagination service as a helper for simple pagination, sorting and filtering.
    For each business service requires pagination it needs to provid base query, filtering construct
    and sort_by columns mapping for this PaginateService, The service uses 'page_param' for
    executing paged query and provides paged result.

    Attributes:
        db (Session): The SqlAlchemy database session.
        base_query (Select): Provided base query as SqlAlchemy 'Select' statement.
        filter_by_criteria (ColumnElement): Provided filter criteria for base query to be filtered by.
            'None' if no need to apply filter.
        sort_by_column_mapping (UnaryExpression): Provided db model columns mapping specific from the
            caller for base query to apply order by query.
        page_param: Paging parameters for performing pagination, sorting, filtering passed from external inputs.
    """
    def __init__(
            self,
            db: Session,
            base_query: Select,
            filter_by_criteria: ColumnElement[bool] | None,
            sort_by_column_mapping: dict[StrEnum, any],
            page_param: PageParamsSchema
        ):
        self.db = db  # SqlAlchemy session.
        self.base_query = base_query  # 'Select' base query.
        self.__filter_by_criteria = filter_by_criteria
        self.order_by_column_mapping = sort_by_column_mapping
        self.__page_params = page_param
        self.page = page_param.page
        self.size = page_param.size
        self.limit = self.size
        self.offset = (self.page - 1) * self.size

    def get_paginated_results(self, ResultSchema: BaseModel) -> PagedResultsSchema[T]:
        """
        Paginate the query results.
        Main function for the service, it will apply 'filter (where clause)', 'order_by clause'
        if needed and apply paging based on calculated 'offset' and 'limit'

        Arguments:
            ResultSchema: This is the return type Class and used for paged result conversion.

        Return:
            Paged result with Generic type 'PagedResultsSchema[T]'. Other than paged results,
            the pagniation metadata are also returned.
        """
        LOGGER.debug(f"Obtaining paginated results with page params: {self.__page_params}")
        paged_query = self.__apply_filter_by(self.base_query)
        paged_query = self.__apply_order_by(paged_query)
        paged_query = paged_query.offset(self.offset).limit(self.limit)
        total_counts = self.__get_total_count()
        results = PagedResultsSchema[ResultSchema](
            meta = PageResultMetaSchema(
                total=total_counts,
                number_of_pages=self.__get_number_of_pages(total_counts),
                page_number=self.page,
                page_size=self.size
            ),
            results=[ResultSchema.model_validate(item) for item in self.db.scalars(paged_query)]
        )
        return results

    def __get_total_count(self) -> int:
        total_count_q = self.__apply_filter_by(self.base_query)
        count = self.db.scalar(
            select(func.count()).select_from(total_count_q.subquery())
        )
        return count

    def __get_number_of_pages(self, count: int) -> int:
        rest = count % self.size
        quotient = count // self.size
        return quotient if not rest else quotient + 1

    def __apply_order_by(self, q: Select) -> Select:
        """
        Based on 'sort_by' and 'sort_order' page_params to build SQL "ORDER BY"
        clause, e.g., ("ORDER BY app_fam.fam_user.user_name ASC") to return
        for the query.
        """
        sort_by = self.__page_params.sort_by
        sort_order = self.__page_params.sort_order
        mapped_column = (
            list(self.order_by_column_mapping.values())[0]  # default sort_by column
            if sort_by is None
            else self.order_by_column_mapping.get(sort_by)
        )

        order_by_criteria = asc(mapped_column) if sort_order == SortOrderEnum.ASC else desc(mapped_column)

        LOGGER.debug(f"Applying order_by criteria: {order_by_criteria}")
        if order_by_criteria is not None:
            q = q.order_by(order_by_criteria)
        return q

    def __apply_filter_by(self, q: Select) -> Select:
        LOGGER.debug(f"Applying filter criteria: {self.__filter_by_criteria}")
        if self.__filter_by_criteria is not None:
              q = q.filter(self.__filter_by_criteria)
        return q