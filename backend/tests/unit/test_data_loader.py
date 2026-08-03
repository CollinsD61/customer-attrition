import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

SAMPLE_CSV = REPO_ROOT / "tests" / "fixtures" / "sample_churn.csv"

from backend.app.services import data_loader


@pytest.fixture(autouse=True)
def _use_sample_csv(monkeypatch):
    monkeypatch.setattr(data_loader, "CSV_PATH", SAMPLE_CSV)
    monkeypatch.setattr(data_loader, "_df", None)


def test_get_customer_returns_dict():
    customer = data_loader.get_customer("CUST0000000001")

    assert isinstance(customer, dict)
    assert customer["customer_id"] == "CUST0000000001"


def test_get_customer_none_for_missing():
    assert data_loader.get_customer("CUST9999999999") is None


def test_query_customers_pagination():
    result = data_loader.query_customers(page=1, page_size=5)

    assert len(result["items"]) == 5
    assert result["total"] == 10
    assert result["page"] == 1
    assert result["total_pages"] == 2


def test_risk_status_high_exists():
    high = data_loader.query_customers(risk_status="HIGH")

    assert len(high["items"]) >= 1
    assert all(item["risk_status"] == "HIGH" for item in high["items"])
