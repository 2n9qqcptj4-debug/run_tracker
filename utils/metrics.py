import pandas as pd
from datetime import timedelta


def prepare_metrics_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Produces a standardized metrics dataframe with:
    - date_dt
    - distance (float)
    - duration_seconds
    - pace_seconds
    - pace_min_per_mile (string)
    - avg_hr, max_hr (numeric)
    """

    if df.empty:
        return df

    m = df.copy()

    # ---------------------------
    # DATE
    # ---------------------------
    m["date_dt"] = pd.to_datetime(m["date"], errors="coerce")

    # ---------------------------
    # DISTANCE
    # ---------------------------
    m["distance"] = pd.to_numeric(m["distance"], errors="coerce")

    # ---------------------------
    # DURATION → SECONDS
    # ---------------------------
    def parse_duration(d):
        try:
            if isinstance(d, (int, float)):
                return float(d)
            t = pd.to_timedelta(d)
            return t.total_seconds()
        except:
            return None

    m["duration_seconds"] = m["duration"].apply(parse_duration)

    # ---------------------------
    # PACE PARSING
    # ---------------------------
    def parse_pace(p):
        try:
            if isinstance(p, (int, float)):
                return float(p)
            t = pd.to_timedelta(p)
            return t.total_seconds()
        except:
            return None

    # If avg_pace exists
    if "avg_pace" in m.columns:
        m["pace_seconds"] = m["avg_pace"].apply(parse_pace)
    else:
        m["pace_seconds"] = None

    # Compute pace if missing
    missing_mask = (
        m["pace_seconds"].isna()
        & m["duration_seconds"].notna()
        & m["distance"].gt(0)
    )
    m.loc[missing_mask, "pace_seconds"] = (
        m.loc[missing_mask, "duration_seconds"] / m.loc[missing_mask, "distance"]
    )

    # Pretty pace
    def pace_to_str(sec):
        try:
            return str(timedelta(seconds=int(sec)))
        except:
            return None

    m["pace_min_per_mile"] = m["pace_seconds"].apply(pace_to_str)

    # ---------------------------
    # HR FIELDS
    # ---------------------------
    for col in ["avg_hr", "max_hr"]:
        if col in m.columns:
            m[col] = pd.to_numeric(m[col], errors="coerce")

    # ---------------------------
    # FINISH
    # ---------------------------
    m = m.sort_values("date_dt")

    return m
