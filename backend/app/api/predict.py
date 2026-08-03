from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.core.exceptions import (
    CustomerNotFoundError,
    FeatureLookupError,
    ModelServerError,
    PredictionError,
)
from backend.app.services.feast_client import FeastClient
from backend.app.services.kserve_client import KServeClient
from backend.app.services.prediction_service import PredictionService

router = APIRouter()


class PredictRequest(BaseModel):
    customer_id: str


class BatchPredictRequest(BaseModel):
    customer_ids: list[str]


def _service() -> PredictionService:
    return PredictionService(FeastClient(), KServeClient())


@router.post("/single")
def predict_single(req: PredictRequest):
    try:
        return _service().predict(req.customer_id)
    except CustomerNotFoundError:
        raise HTTPException(404, "Customer not found")
    except (FeatureLookupError, ModelServerError, PredictionError) as e:
        raise HTTPException(502, str(e))


@router.post("/batch")
def predict_batch(req: BatchPredictRequest):
    return {"items": _service().batch_predict(req.customer_ids)}
