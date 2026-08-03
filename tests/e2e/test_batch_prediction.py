import os

import pytest

pytest.importorskip("httpx")

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_E2E") != "1",
    reason="requires live backend + KServe; set RUN_E2E=1",
)

import httpx


def test_batch_prediction_end_to_end():
    base = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
    resp = httpx.post(
        f"{base}/api/predict/batch",
        json={"customer_ids": ["CUST0000000001", "CUST0000000002"]},
        timeout=60,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) == 2
    for item in body["items"]:
        assert "model_version" in item
