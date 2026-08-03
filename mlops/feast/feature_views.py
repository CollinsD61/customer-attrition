from datetime import timedelta

from data_sources import churn_features_source
from entities import customer
from feast import FeatureView, Field
from feast.types import Bool, Float32, Int32, String

churn_feature_view = FeatureView(
    name="churn_feature_view",
    entities=[customer],
    ttl=timedelta(days=5 * 365),
    source=churn_features_source,
    schema=[
        Field(name="age", dtype=Int32),
        Field(name="annual_income", dtype=Float32),
        Field(name="dependents", dtype=Int32),
        Field(name="tenure", dtype=Int32),
        Field(name="paperless_billing", dtype=Bool),
        Field(name="senior_citizen", dtype=Bool),
        Field(name="monthlycharges", dtype=Float32),
        Field(name="totalcharges", dtype=Float32),
        Field(name="num_services", dtype=Int32),
        Field(name="has_phone_service", dtype=Bool),
        Field(name="has_internet_service", dtype=Bool),
        Field(name="has_online_security", dtype=Bool),
        Field(name="has_online_backup", dtype=Bool),
        Field(name="has_device_protection", dtype=Bool),
        Field(name="has_tech_support", dtype=Bool),
        Field(name="has_streaming_tv", dtype=Bool),
        Field(name="has_streaming_movies", dtype=Bool),
        Field(name="customer_satisfaction", dtype=Int32),
        Field(name="num_complaints", dtype=Int32),
        Field(name="num_service_calls", dtype=Int32),
        Field(name="late_payments", dtype=Int32),
        Field(name="avg_monthly_gb", dtype=Float32),
        Field(name="days_since_last_interaction", dtype=Int32),
        Field(name="credit_score", dtype=Float32),
        Field(name="tenure_risk", dtype=String),
        Field(name="engagement_score", dtype=Float32),
        Field(name="complaint_ratio", dtype=Float32),
        Field(name="spend_to_income_ratio", dtype=Float32),
    ],
    tags={"team": "mlops", "domain": "churn"},
)
