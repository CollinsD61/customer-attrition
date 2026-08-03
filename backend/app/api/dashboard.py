from fastapi import APIRouter

from backend.app.services.data_loader import (
    get_dashboard_summary,
    get_dashboard_trend,
    get_risk_distribution,
)

router = APIRouter()


@router.get("/summary")
def summary():
    return get_dashboard_summary()


@router.get("/trend")
def trend():
    return get_dashboard_trend()


@router.get("/risk-distribution")
def risk_distribution():
    return get_risk_distribution()
