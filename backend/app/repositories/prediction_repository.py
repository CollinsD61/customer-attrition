from sqlalchemy.orm import Session

from backend.app.models.prediction import Prediction


class PredictionRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def save_prediction(
        self,
        customer_id: str,
        churn_probability: float,
        prediction: int,
        model_version: str,
    ) -> Prediction:
        pred = Prediction(
            customer_id=customer_id,
            churn_probability=churn_probability,
            prediction=prediction,
            model_version=model_version,
        )
        self._db.add(pred)
        self._db.commit()
        self._db.refresh(pred)
        return pred

    def get_history_for_customer(
        self, customer_id: str, limit: int = 50
    ) -> list[Prediction]:
        return (
            self._db.query(Prediction)
            .filter(Prediction.customer_id == customer_id)
            .order_by(Prediction.created_at.desc())
            .limit(limit)
            .all()
        )
