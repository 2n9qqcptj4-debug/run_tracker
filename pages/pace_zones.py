import streamlit as st
from utils.styling import inject_css
inject_css()

import pandas as pd
from datetime import timedelta

from utils.database import fetch_runs


def _pace_to_str(pace_sec: float) -> str:
    if pd.isna(pace_sec) or pace_sec <= 0:
        return "N/A"
    return str(timedelta(seconds=int(pace_sec)))


def render_pace_zones_page():
    st.title("📏 Pace Zones")

    df = fetch_runs()
    if df.empty:
        st.info("Log some runs to calculate pace zones.")
        return

    # Try to infer a "threshold" pace from faster runs (tempo/race)
    fast_types = ["Tempo", "Threshold", "Interval", "Race"]
    fast = df[df["run_type"].isin(fast_types) & df["distance"].gt(2)]

    if fast.empty:
        st.warning("Not enough tempo/threshold/race data. Using overall average pace.")
        base_df = df[df["distance"] > 0]
    else:
        base_df = fast

    # Estimate pace seconds from duration/distance if possible
    def compute_pace(row):
        try:
            if row.get("avg_pace"):
                # if you saved avg_pace as HH:MM:SS, parse it
                t = pd.to_timedelta(row["avg_pace"])
                return t.total_seconds()
            # else compute from duration + distance
            t = pd.to_timedelta(row["duration"])
            if row["distance"] > 0:
                return t.total_seconds() / row["distance"]
        except Exception:
            return None
        return None

    base_df["pace_sec"] = base_df.apply(compute_pace, axis=1)
    threshold_pace_sec = base_df["pace_sec"].median()

    if pd.isna(threshold_pace_sec):
        st.error("Could not calculate pace zones from your data yet.")
        return

    # Simple pace zone model relative to threshold pace:
    # (these ratios are rough and user-friendly, not lab-grade)
    zones = {
        "Easy / Recovery": threshold_pace_sec * 1.20,
        "Steady / Aerobic": threshold_pace_sec * 1.08,
        "Marathon Pace (approx)": threshold_pace_sec * 1.03,
        "Threshold / Tempo": threshold_pace_sec,
        "Interval": threshold_pace_sec * 0.90,
        "Repetition / Speed": threshold_pace_sec * 0.80,
    }

    st.subheader("Suggested Pace Zones")
    for name, pace_sec in zones.items():
        st.markdown(f"**{name}:** {_pace_to_str(pace_sec)} per mile")

    st.caption(
        "These zones are estimated based on your faster runs. "
        "Use them as a guide and adjust by feel and heart rate."
    )


def main():
    render_pace_zones_page()


if __name__ == "__main__":
    main()

