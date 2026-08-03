from datetime import datetime

from pydantic import BaseModel


class CustomerCreate(BaseModel):
    customer_id: str
    tenure: int = 0
    contract_type: str = ""
    monthly_spend: float = 0.0


class CustomerUpdate(BaseModel):
    tenure: int | None = None
    contract_type: str | None = None
    monthly_spend: float | None = None
    churn_risk_score: float | None = None
    risk_status: str | None = None


class CustomerResponse(BaseModel):
    id: int
    customer_id: str
    tenure: int
    contract_type: str
    monthly_spend: float
    churn_risk_score: float
    risk_status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
