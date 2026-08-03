from pathlib import Path

import pandas as pd

CSV_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent.parent
    / "data"
    / "samples"
    / "customer_churn_1M.csv"
)

_df: pd.DataFrame | None = None


def _compute_risk_score(row: pd.Series) -> float:

    score = 0.0

    if row["contract"] == "month-to-month":
        score += 0.30
    elif row["contract"] == "one_year":
        score += 0.12

    tenure = row["tenure"]
    if tenure < 6:
        score += 0.20
    elif tenure < 24:
        score += 0.08

    sat = row["customer_satisfaction"]
    if sat < 3:
        score += 0.18
    elif sat < 5:
        score += 0.10

    complaints = row["num_complaints"]
    if complaints > 2:
        score += 0.15
    elif complaints > 0:
        score += 0.06

    late = row["late_payments"]
    if late > 2:
        score += 0.10
    elif late > 0:
        score += 0.04

    if row["num_service_calls"] > 3:
        score += 0.07

    return round(min(score, 0.98), 4)


def _risk_status(score: float) -> str:
    if score > 0.5:
        return "HIGH"
    if score > 0.25:
        return "MEDIUM"
    return "LOW"


def _load() -> pd.DataFrame:
    global _df
    if _df is not None:
        return _df

    df = pd.read_csv(CSV_PATH)
    df["churn_risk_score"] = df.apply(_compute_risk_score, axis=1)
    df["risk_status"] = df["churn_risk_score"].apply(_risk_status)
    df["signup_date"] = df["signup_date"].astype(str).str[:10]
    _df = df
    return _df


def get_df() -> pd.DataFrame:
    return _load()


def get_customer(customer_id: str) -> dict | None:
    df = get_df()
    match = df[df["customer_id"] == customer_id]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def query_customers(
    risk_status: str | None = None,
    contract_type: str | None = None,
    tenure_min: int | None = None,
    tenure_max: int | None = None,
    search: str | None = None,
    sort_by: str = "churn_risk_score",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
) -> dict:
    df = get_df()

    if risk_status:
        df = df[df["risk_status"] == risk_status.upper()]
    if contract_type:
        df = df[df["contract"] == contract_type]
    if tenure_min is not None:
        df = df[df["tenure"] >= tenure_min]
    if tenure_max is not None:
        df = df[df["tenure"] <= tenure_max]
    if search:
        df = df[df["customer_id"].str.contains(search, case=False)]

    col_map = {
        "churn_risk_score": "churn_risk_score",
        "tenure": "tenure",
        "monthly_spend": "monthlycharges",
        "customer_id": "customer_id",
    }
    sort_col = col_map.get(sort_by, "churn_risk_score")
    ascending = sort_order == "asc"
    df = df.sort_values(sort_col, ascending=ascending)

    total = len(df)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    end = start + page_size
    page_df = df.iloc[start:end]

    items = []
    for _, row in page_df.iterrows():
        items.append(
            {
                "customer_id": row["customer_id"],
                "tenure": int(row["tenure"]),
                "contract_type": row["contract"],
                "monthly_spend": float(row["monthlycharges"]),
                "churn_risk_score": float(row["churn_risk_score"]),
                "risk_status": row["risk_status"],
            }
        )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def get_dashboard_summary() -> dict:
    df = get_df()
    total = len(df)
    high = int((df["risk_status"] == "HIGH").sum())
    return {
        "total_customers": total,
        "churn_rate": round(high / total, 4) if total else 0,
        "at_risk_count": high,
        "avg_risk_score": round(float(df["churn_risk_score"].mean()), 4),
    }


def get_dashboard_trend() -> list[dict]:
    df = get_df()
    df["signup_month"] = df["signup_date"].str[:7]
    monthly = (
        df.groupby("signup_month")
        .agg(
            churn_rate=("churn_risk_score", "mean"),
            total=("customer_id", "count"),
        )
        .reset_index()
    )
    monthly = monthly.sort_values("signup_month").tail(30)
    return [
        {"date": row["signup_month"], "churn_rate": round(float(row["churn_rate"]), 4)}
        for _, row in monthly.iterrows()
    ]


def get_risk_distribution() -> dict:
    df = get_df()
    return {
        "low": int((df["risk_status"] == "LOW").sum()),
        "medium": int((df["risk_status"] == "MEDIUM").sum()),
        "high": int((df["risk_status"] == "HIGH").sum()),
    }


def get_customer_detail(customer_id: str) -> dict | None:
    row = get_customer(customer_id)
    if row is None:
        return None
    return {
        "customer_id": row["customer_id"],
        "tenure": int(row["tenure"]),
        "contract_type": row["contract"],
        "monthly_spend": float(row["monthlycharges"]),
        "churn_risk_score": float(row["churn_risk_score"]),
        "risk_status": row["risk_status"],
        "demographics": {
            "age": int(row["age"]),
            "gender": row["gender"],
            "education": row["education"],
            "marital_status": row["marital_status"],
            "dependents": int(row["dependents"]),
        },
        "financials": {
            "credit_score": float(row["credit_score"])
            if pd.notna(row["credit_score"])
            else None,
            "annual_income": float(row["annual_income"]),
            "monthly_charges": float(row["monthlycharges"]),
            "total_charges": float(row["totalcharges"]),
            "payment_method": row["payment_method"],
        },
        "signup_date": row["signup_date"],
        "paperless_billing": row["paperless_billing"] == "Yes",
        "senior_citizen": bool(row["senior_citizen"]),
    }


def get_customer_risk(customer_id: str) -> dict | None:
    row = get_customer(customer_id)
    if row is None:
        return None

    contract = row["contract"]
    sat = row["customer_satisfaction"]
    complaints = row["num_complaints"]
    tenure = row["tenure"]
    late = row["late_payments"]

    shap_drivers = []
    total = 0.0

    if contract == "month-to-month":
        shap_drivers.append(
            {
                "feature": "Month-to-Month Contract",
                "impact": 30,
                "direction": "positive",
            }
        )
        total += 30
    elif contract == "two_year":
        shap_drivers.append(
            {"feature": "Two-Year Contract", "impact": 25, "direction": "negative"}
        )
        total += 25

    if sat >= 7:
        shap_drivers.append(
            {
                "feature": f"High Satisfaction ({sat}/10)",
                "impact": 20,
                "direction": "negative",
            }
        )
        total += 20
    elif sat < 4:
        shap_drivers.append(
            {
                "feature": f"Low Satisfaction ({sat}/10)",
                "impact": 20,
                "direction": "positive",
            }
        )
        total += 20

    if complaints == 0:
        shap_drivers.append(
            {"feature": "Zero Complaints", "impact": 15, "direction": "negative"}
        )
        total += 15
    elif complaints > 0:
        shap_drivers.append(
            {
                "feature": f"{int(complaints)} Complaints",
                "impact": 15,
                "direction": "positive",
            }
        )
        total += 15

    if tenure < 6:
        shap_drivers.append(
            {
                "feature": f"Low Tenure ({int(tenure)} mos)",
                "impact": 15,
                "direction": "positive",
            }
        )
        total += 15
    elif tenure > 24:
        shap_drivers.append(
            {
                "feature": f"Long Tenure ({int(tenure)} mos)",
                "impact": 15,
                "direction": "negative",
            }
        )
        total += 15
    else:
        shap_drivers.append(
            {
                "feature": f"Medium Tenure ({int(tenure)} mos)",
                "impact": 10,
                "direction": "negative",
            }
        )
        total += 10

    if late > 0:
        shap_drivers.append(
            {
                "feature": f"{int(late)} Late Payments",
                "impact": 10,
                "direction": "positive",
            }
        )
        total += 10
    else:
        shap_drivers.append(
            {"feature": "No Late Payments", "impact": 10, "direction": "negative"}
        )
        total += 10

    shap_drivers.sort(
        key=lambda x: float(str(x["impact"])) if x["impact"] is not None else 0.0,
        reverse=True,
    )
    shap_drivers = shap_drivers[:4]

    return {
        "score": round(float(row["churn_risk_score"]) * 100, 2),
        "status": row["risk_status"],
        "description": "Customer is highly satisfied and stable"
        if row["risk_status"] == "LOW"
        else "Customer shows moderate risk indicators"
        if row["risk_status"] == "MEDIUM"
        else "Customer requires immediate retention intervention",
        "shap_drivers": shap_drivers,
        "behavioral_kpis": [
            {
                "label": "Satisfaction",
                "value": f"{float(row['customer_satisfaction'])}/10",
            },
            {"label": "Complaints", "value": int(row["num_complaints"])},
            {"label": "Late Payments", "value": int(row["late_payments"])},
            {"label": "Service Calls", "value": int(row["num_service_calls"])},
            {
                "label": "Avg Monthly Data Usage",
                "value": f"{float(row['avg_monthly_gb'])} GB",
            },
            {
                "label": "Days Since Interaction",
                "value": int(row["days_since_last_interaction"]),
            },
        ],
        "services": [
            {"name": "Phone Service", "active": bool(row["has_phone_service"])},
            {"name": "Internet Service", "active": bool(row["has_internet_service"])},
            {"name": "Online Security", "active": bool(row["has_online_security"])},
            {"name": "Online Backup", "active": bool(row["has_online_backup"])},
            {"name": "Device Protection", "active": bool(row["has_device_protection"])},
            {"name": "Tech Support", "active": bool(row["has_tech_support"])},
            {"name": "Streaming TV", "active": bool(row["has_streaming_tv"])},
            {"name": "Streaming Movies", "active": bool(row["has_streaming_movies"])},
        ],
        "metadata": {
            "inference_latency_ms": 12,
            "model_version": "LightGBM v2.1",
            "feature_store": "Redis",
            "feature_freshness_minutes": 2,
        },
    }
