from datetime import datetime

from pydantic import BaseModel


class PredictionHistoryItem(BaseModel):
    customer_id: str
    churn_probability: float
    prediction: int
    model_version: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PredictionHistoryResponse(BaseModel):
    items: list[PredictionHistoryItem]
    total: int
