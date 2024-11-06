
import logging
from abc import ABC, abstractmethod
from enum import StrEnum

from api.app.constants import SortOrderEnum
from api.app.schemas.pagination import (PagedResultsSchema, PageParamsSchema,
                                        PageResultMetaSchema)
from pydantic import BaseModel
from pytest import Session
from sqlalchemy import ColumnElement, Select, asc, desc, func, select

LOGGER = logging.getLogger(__name__)

class SimplePaginateRepository(ABC):
    """
    This class is an abstract base class which provides functionality for simple pagination.
    Subclass needs to provides implementation for abstract methods.
    """
    def __init__(self, db: Session):
        self.db = db

    @abstractmethod
    def get_sort_by_column_mapping(self) -> dict[StrEnum, any]:
        """ Abstract methods, implement this. """
        pass

    @abstractmethod
    def get_filter_by_criteria(self, page_params: PageParamsSchema) -> ColumnElement[bool] | None:
        """ Abstract methods, implement this. """
        pass

    def get_paginated_results(
            self, base_query: Select, page_params: PageParamsSchema, ResultSchema: type[BaseModel]
        ) -> PagedResultsSchema[type[BaseModel]]:
        """
        Paginate the query results.
        Main implemented function for this abstract repository, it will apply 'filter (where clause)', 'order_by clause'
        if needed and apply paging based on calculated 'offset' and 'limit'

        Arguments:
            base_query (Select): A base Select query provided from subclass repository to be based on.
            page_params (PageParamsSchema): pagination parameters for query to return paged results.
            ResultSchema (type[BaseModel]): This is the return type Class and used for paged result conversion.

        Return:
            Paged result with type 'PagedResultsSchema[type[BaseModel]]'. Other than paged results,
            the pagniation metadata are also returned.
        """
        LOGGER.debug(f"Obtaining paginated results with page params: {page_params}")
        self.base_query = base_query
        self.page_params = page_params
        self.page = page_params.page
        self.size = page_params.size
        self.__limit = self.size
        self.__offset = (self.page - 1) * self.size

        paged_query = self.__apply_filter_by(self.base_query, page_params)
        paged_query = self.__apply_order_by(paged_query)
        paged_query = paged_query.offset(self.__offset).limit(self.__limit)
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
        total_count_q = self.__apply_filter_by(self.base_query, self.page_params)
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
        sort_by = self.page_params.sort_by
        sort_order = self.page_params.sort_order
        column_mapping = self.get_sort_by_column_mapping()
        mapped_column = (
            list(column_mapping.values())[0]  # default sort_by column
            if sort_by is None
            else column_mapping.get(sort_by)
        )

        order_by_criteria = asc(mapped_column) if sort_order == SortOrderEnum.ASC else desc(mapped_column)

        LOGGER.debug(f"Applying order_by criteria: {order_by_criteria}")
        if order_by_criteria is not None:
            q = q.order_by(order_by_criteria)
        return q

    def __apply_filter_by(self, q: Select, page_params: PageParamsSchema) -> Select:
        filter_by_criteria = self.get_filter_by_criteria(page_params)
        LOGGER.debug(f"Applying filter criteria: {filter_by_criteria}")
        if filter_by_criteria is not None:
              q = q.filter(filter_by_criteria)
        return q