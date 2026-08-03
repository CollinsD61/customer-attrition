import pandas as pd

from customer_attrition.features.build_features import build_features
from customer_attrition.preprocessing.clean import clean_data
from customer_attrition.preprocessing.encode import encode_features


def preprocess_for_inference(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = clean_data(df)
    encoded = encode_features(cleaned)
    return build_features(encoded)
