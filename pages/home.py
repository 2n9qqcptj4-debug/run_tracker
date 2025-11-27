import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils.database import fetch_runs
from utils.metrics import prepare_metrics_df
from utils.prs import calculate_prs


def render_home_page():
    st.title("🏃‍♂️ Run Tracker Home")

    df = fetch_runs()
    if df.empty:
        st.info("Welcome! Log your first run to start building your training history.")
        if st.button("Log a Run Now"):
            st.switch_page("pages/log_run.py")
        return

    metrics = prepare_metrics_df(df)
    prs = calculate_prs(metrics)

    # Key stats
    st.subheader("Overview")

    last_7 = pd.to_datetime(df["date"]) >= (datetime.today() - timedelta(days=7))
    last_30 = pd.to_datetime(df["date"]) >= (datetime.today() - timedelta(days=30))

    miles_7 = df[last_7]["distance"].sum()
    miles_30 = df[last_30]["distance"].sum()
    total_miles = df["distance"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Miles (Last 7 Days)", f"{miles_7:.1f}")
    col2.metric("Miles (Last 30 Days)", f"{miles_30:.1f}")
    col3.metric("Lifetime Miles", f"{total_miles:.1f}")

    # Quick actions
    st.markdown("### Quick Actions")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📝 Log a Run"):
            st.switch_page("pages/log_run.py")
    with c2:
        if st.button("📤 Garmin Import"):
            st.switch_page("pages/garmin_import.py")
    with c3:
        if st.button("🤖 Open AI Coach"):
            st.switch_page("pages/ai_coach.py")

    # Recent runs
    st.markdown("### Recent Runs")
    recent = df.sort_values("date", ascending=False).head(5)
    for _, row in recent.iterrows():
        st.markdown(
            f"""
            **{row['date']} — {row['run_type']}**  
            {row['distance']} mi · {row['duration']} · Effort {row.get('effort', '')}
            """
        )

    # PR snapshot
    st.markdown("### PR Snapshot")
    if not prs:
        st.write("No PRs yet — keep running! 🏅")
    else:
        st.json(prs)


def main():
    render_home_page()


if __name__ == "__main__":
    main()
