import logging
from typing import List

from api.app.constants import District
from api.app.schemas.fam_district import FamDistrictSchema
from fastapi import APIRouter

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[FamDistrictSchema])
def get_districts():
    """
    List the BC natural resource districts available for scoping roles that
    have role_type_district set.

    Districts are a fixed reference set held in the District enum, not database
    records, so this returns the full list and expects the caller to filter.
    """
    districts = [
        FamDistrictSchema(
            org_unit_code=district.org_unit_code,
            orgUnitName=district.orgUnitName,
            isExpired=district.isExpired,
        )
        for district in District
    ]
    LOGGER.debug(f"Returning {len(districts)} districts.")
    return districts
