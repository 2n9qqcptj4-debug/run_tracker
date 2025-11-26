import pandas as pd


def prepare_metrics_df(df):
    df = df.copy()
    df["date_dt"] = pd.to_datetime(df["date"], errors="coerce")
    return df