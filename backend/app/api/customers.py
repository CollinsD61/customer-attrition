from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from backend.app.services.data_loader import (
    get_customer_detail,
    get_customer_risk,
    query_customers,
)

router = APIRouter()


@router.get("")
def list_customers(
    risk_status: str | None = Query(None),
    contract_type: str | None = Query(None),
    tenure_min: int | None = Query(None),
    tenure_max: int | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("churn_risk_score"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    return query_customers(
        risk_status=risk_status,
        contract_type=contract_type,
        tenure_min=tenure_min,
        tenure_max=tenure_max,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )


@router.get("/{customer_id}")
def get_one(customer_id: str):
    detail = get_customer_detail(customer_id)
    if detail is None:
        raise HTTPException(404, "Customer not found")
    return detail


@router.get("/{customer_id}/risk")
def get_risk(customer_id: str):
    risk = get_customer_risk(customer_id)
    if risk is None:
        raise HTTPException(404, "Customer not found")
    return risk


@router.get("/{customer_id}/services")
def get_services(customer_id: str):
    risk = get_customer_risk(customer_id)
    if risk is None:
        raise HTTPException(404, "Customer not found")
    return risk["services"]


@router.get("/{customer_id}/kpis")
def get_kpis(customer_id: str):
    risk = get_customer_risk(customer_id)
    if risk is None:
        raise HTTPException(404, "Customer not found")
    return risk["behavioral_kpis"]


@router.post("/export")
def export_csv(
    risk_status: str | None = Query(None),
    contract_type: str | None = Query(None),
):
    import io

    from backend.app.services.data_loader import get_df

    df = get_df()
    if risk_status:
        df = df[df["risk_status"] == risk_status.upper()]
    if contract_type:
        df = df[df["contract"] == contract_type]

    export_cols = [
        "customer_id",
        "tenure",
        "contract",
        "monthlycharges",
        "churn_risk_score",
        "risk_status",
    ]
    stream = io.StringIO()
    df[export_cols].rename(
        columns={"contract": "contract_type", "monthlycharges": "monthly_spend"}
    ).to_csv(stream, index=False)
    stream.seek(0)

    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=customers.csv"},
    )
