import streamlit as st
from utils.styling import inject_css
inject_css()

import pandas as pd

from utils.database import fetch_runs


def render_feed_page():
    st.title("📜 Training Feed")

    df = fetch_runs()
    if df.empty:
        st.info("No runs logged yet. Log a run to see your feed.")
        return

    df = df.sort_values("date", ascending=False)

    st.sidebar.markdown("### Filters")
    run_types = sorted(df["run_type"].dropna().unique().tolist())
    selected_types = st.sidebar.multiselect(
        "Run Types", options=run_types, default=run_types
    )
    min_distance = st.sidebar.number_input(
        "Min Distance (mi)", min_value=0.0, value=0.0, step=0.5
    )
    max_distance = st.sidebar.number_input(
        "Max Distance (mi)", min_value=0.0, value=float(df["distance"].max() or 0) or 0.0, step=0.5
    )

    filtered = df[
        df["run_type"].isin(selected_types)
        & (df["distance"] >= min_distance)
        & (df["distance"] <= max_distance)
    ]

    if filtered.empty:
        st.info("No runs match your filters.")
        return

    for _, row in filtered.iterrows():
        with st.container():
            st.markdown(
                f"### {row['date']} — {row['run_type']} ({row['distance']} mi)"
            )
            st.write(
                f"Duration: {row['duration']} · Effort: {row.get('effort', '')} · Avg HR: {row.get('avg_hr', '')}"
            )
            if row.get("felt"):
                st.write(f"**How it felt:** {row['felt']}")
            if row.get("pain"):
                st.write(f"**Pain / Tightness:** {row['pain']}")
            st.divider()


def main():
    render_feed_page()


if __name__ == "__main__":
    main()

