from fastapi import APIRouter, Depends, Query

from backend.app.api.auth import get_current_user
from backend.app.db.session import get_db
from backend.app.repositories.prediction_repository import PredictionRepository
from backend.app.schemas.history import PredictionHistoryItem, PredictionHistoryResponse

router = APIRouter()


@router.get("/{customer_id}/history", response_model=PredictionHistoryResponse)
def get_history(
    customer_id: str,
    limit: int = Query(50, ge=1, le=200),
    db=Depends(get_db),  # noqa: B008
    _current_user: dict = Depends(get_current_user),  # noqa: B008
):
    repo = PredictionRepository(db)
    items = repo.get_history_for_customer(customer_id, limit=limit)
    history_items = [
        PredictionHistoryItem(
            customer_id=item.customer_id,
            churn_probability=item.churn_probability,
            prediction=item.prediction,
            model_version=item.model_version,
            created_at=item.created_at,
        )
        for item in items
    ]
    return PredictionHistoryResponse(items=history_items, total=len(history_items))
