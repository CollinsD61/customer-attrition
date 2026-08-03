import os

import pytest

pytest.importorskip("httpx")

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_E2E") != "1",
    reason="requires live backend + KServe; set RUN_E2E=1",
)

import httpx


def test_single_prediction_end_to_end():
    base = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
    resp = httpx.post(
        f"{base}/api/predict/single",
        json={"customer_id": "CUST0000000001"},
        timeout=30,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "churn_risk_score" in body
    assert "model_version" in body
