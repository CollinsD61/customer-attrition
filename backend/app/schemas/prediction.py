from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_customers: int
    churn_rate: float
    at_risk_count: int
    avg_risk_score: float


class TrendPoint(BaseModel):
    date: str
    churn_rate: float


class RiskDistribution(BaseModel):
    low: int
    medium: int
    high: int


class CustomerBase(BaseModel):
    customer_id: str
    tenure: int
    contract_type: str
    monthly_spend: float
    churn_risk_score: float
    risk_status: str


class CustomerDetail(CustomerBase):
    demographics: dict
    financials: dict
    signup_date: str
    paperless_billing: bool
    senior_citizen: bool


class BehavioralKPI(BaseModel):
    label: str
    value: float | str
    unit: str | None = None
    trend: str | None = None


class ShapDriver(BaseModel):
    feature: str
    impact: float
    direction: str


class RiskAnalysis(BaseModel):
    score: float
    status: str
    description: str
    shap_drivers: list[ShapDriver]
    behavioral_kpis: list[BehavioralKPI]
    services: list[dict]
    metadata: dict


class PaginatedResponse(BaseModel):
    items: list[dict]
    total: int
    page: int
    page_size: int
    total_pages: int
