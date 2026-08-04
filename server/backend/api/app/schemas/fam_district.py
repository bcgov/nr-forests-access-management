from pydantic import BaseModel, ConfigDict


class FamDistrictSchema(BaseModel):
    """
    A BC natural resource district, used to scope roles that have
    role_type_district set.

    Field names mirror the org unit source data, which is why orgUnitName and
    isExpired are camelCase while org_unit_code is not.
    """

    org_unit_code: str
    orgUnitName: str
    isExpired: bool

    model_config = ConfigDict(from_attributes=True)
