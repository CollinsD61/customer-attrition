import os

import pytest

pytest.importorskip("httpx")

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION") != "1",
    reason="requires live KServe endpoint; set RUN_INTEGRATION=1",
)

import httpx


@pytest.fixture
def base_url() -> str:
    return __import__("os").getenv(
        "KSERVE_BASE_URL", "http://localhost:8080/v1/models/churn-predictor"
    )


def test_backend_predicts_via_kserve(base_url: str) -> None:
    resp = httpx.post(
        f"{base_url}:predict",
        json={"customer_id": "CUST0000000001"},
        timeout=30,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "churn_probability" in body
    assert "model_version" in body
