from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class InvestigateRequest(BaseModel):
    customer_id: str
    query: str


class InvestigateResponse(BaseModel):
    customer_id: str
    answer: str
