import pandas as pd
from datetime import timedelta


def prepare_metrics_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes and computes all metrics needed across the app:
    - date_dt
    - duration_seconds
    - pace_seconds
    - pace_min_per_mile
    - avg_hr / max_hr as numeric
    - distance as numeric
    """

    if df.empty:
        return df

    m = df.copy()

    # ---------------------------
    # DATE PARSING
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
    # PACE → SECONDS PER MILE
    # ---------------------------
    def parse_pace(p):
        """
        pace may be stored as 'MM:SS', 'HH:MM:SS', or None.
        """
        try:
            if isinstance(p, (int, float)):
                return float(p)
            t = pd.to_timedelta(p)
            return t.total_seconds()
        except:
            return None

    # If avg_pace exists, parse it
    if "avg_pace" in m.columns:
        m["pace_seconds"] = m["avg_pace"].apply(parse_pace)
    else:
        m["pace_seconds"] = None

    # Compute pace if missing but duration+distance exist
    missing_pace = m["pace_seconds"].isna() & m["duration_seconds"].notna() & m["distance"].gt(0)
    m.loc[missing_pace, "pace_seconds"] = (
        m.loc[missing_pace, "duration_seconds"] / m.loc[missing_pace, "distance"]
    )

    # For display-friendly pace
    def pace_to_str(sec):
        try:
            return str(timedelta(seconds=int(sec)))
        except:
            return None

    m["pace_min_per_mile"] = m["pace_seconds"].apply(pace_to_str)

    # ---------------------------
    # HR METRICS CLEANUP
    # ---------------------------
    for col in ["avg_hr", "max_hr"]:
        if col in m.columns:
            m[col] = pd.to_numeric(m[col], errors="coerce")

    # ---------------------------
    # EFFORT
    # ---------------------------
    if "effort" in m.columns:
        m["effort"] = pd.to_numeric(m["effort"], errors="coerce")

    # ---------------------------
    # SORT BY DATE
    # ---------------------------
    m = m.sort_values("date_dt")

    return m