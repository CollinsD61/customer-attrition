import pandas as pd


def load_kaggle(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)
