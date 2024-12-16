
import operator
from datetime import datetime
from typing import List

from api.app.constants import SortOrderEnum
from api.app.models import model as models
from sqlalchemy import not_, select
from sqlalchemy.orm import Session


def is_sorted_with(o1, o2, attribute: str, order: SortOrderEnum) -> bool:
    # helper function to compare o1, o2 according to the sorting 'order' on attribute.

    a1 = operator.attrgetter(attribute)(o1)
    a2 = operator.attrgetter(attribute)(o2)
    if a1 is None and a2 is None:
        return True
    if a1 is None:
        return order == SortOrderEnum.DESC
    elif a2 is None:
        return order == SortOrderEnum.ASC
    else:
        return (a1 <= a2 if order == SortOrderEnum.ASC else a1 >= a2)


def contains_any_insensitive(obj, search_attributes: List[str], keyword: str) -> bool:
    # helper function to check if 'keyword' is substring of 'attribute' value, case insensitive.

    def contains_keyword_insensitive(attr: str, keyword: str):
        if attr is None:
            return False
        elif isinstance(attr, str):
            return keyword.lower() in attr.lower()
        elif isinstance(attr, datetime):
            format_string = '%Y-%m-%d %H:%M:%S'
            return keyword.lower() in attr.strftime(format_string)
        else:
            return False

    # return True as long as there is one attribute in the instance containing keyword value
    is_any = any(
        contains_keyword_insensitive(operator.attrgetter(attr_name)(obj), keyword)
        for attr_name in search_attributes)
    return is_any