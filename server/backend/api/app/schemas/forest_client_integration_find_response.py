from pydantic import BaseModel


class ForestClientIntegrationFindResponseSchema(BaseModel):
    clientNumber: str
    clientName: str
    clientStatusCode: str
    clientTypeCode: str
