import pandas as pd




def parse_garmin_csv(df):
    row = df.iloc[0]
    return {
        "date": str(row.get("Date", "")),
        "distance": float(row.get("Distance", 0)),
}