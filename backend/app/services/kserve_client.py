from backend.app.core.config import settings
from backend.app.core.exceptions import ModelServerError


class KServeClient:
    def __init__(
        self, service_url: str | None = None, model_name: str | None = None
    ) -> None:
        self._service_url = service_url or settings.KSERVE_SERVICE_URL
        self._model_name = model_name or settings.KSERVE_MODEL_NAME

    def predict(self, features: dict, customer_id: str) -> dict:
        import httpx

        payload = {"instances": [{"customer_id": customer_id, **features}]}
        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(self._service_url, json=payload)
                response.raise_for_status()
                data = response.json()
                predictions = data.get("predictions", [{}])
                return predictions[0] if predictions else {}
        except httpx.HTTPError as e:
            raise ModelServerError(f"KServe inference failed: {e}") from e

    def health_check(self) -> bool:
        import httpx

        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(f"{self._service_url.rsplit(':', 1)[0]}/health")
                return response.status_code == 200
        except httpx.HTTPError:
            return False
