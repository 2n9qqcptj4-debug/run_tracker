import streamlit as st
import pandas as pd

from utils.database import fetch_runs
from utils.metrics import prepare_metrics_df
from utils.prs import calculate_prs


def render_dashboard_page():
    st.title("📊 Dashboard")

    df = fetch_runs()
    if df.empty:
        st.info("Log some runs to view insights.")
        return

    metrics = prepare_metrics_df(df)
    prs = calculate_prs(metrics)

    st.subheader("Summary Stats")
    total_miles = metrics["distance"].sum()
    total_runs = len(metrics)
    avg_pace = metrics["pace_seconds"].mean()
    avg_pace_str = str(pd.to_timedelta(avg_pace, unit="s")) if pd.notna(avg_pace) else "N/A"

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Miles", f"{total_miles:.1f}")
    col2.metric("Total Runs", total_runs)
    col3.metric("Avg Pace", avg_pace_str)

    st.subheader("Recent Runs")
    st.dataframe(
        df[["date", "run_type", "distance", "duration", "avg_hr", "effort"]],
        use_container_width=True,
    )

    st.subheader("PR Board")
    if not prs:
        st.write("No PRs calculated yet.")
    else:
        st.json(prs)


def main():
    render_dashboard_page()


if __name__ == "__main__":
    main()