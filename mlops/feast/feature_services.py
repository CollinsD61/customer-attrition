from feast import FeatureService
from feature_views import churn_feature_view

churn_feature_service = FeatureService(
    name="churn_feature_service",
    features=[churn_feature_view],
)
