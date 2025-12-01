import streamlit as st
from utils.styling import inject_css
inject_css()

import pandas as pd

from utils.database import fetch_runs


def render_compare_runs_page():
    st.title("📊 Compare Runs")

    df = fetch_runs()
    if df.empty:
        st.info("Log some runs to compare them.")
        return

    df = df.sort_values("date", ascending=False)
    df["label"] = df.apply(
        lambda r: f"{r['id']} — {r['date']} · {r['run_type']} · {r['distance']} mi", axis=1
    )

    ids = df["id"].tolist()
    labels = df["label"].tolist()
    options = dict(zip(labels, ids))

    col1, col2 = st.columns(2)
    with col1:
        run_a_label = st.selectbox("Run A", options=list(options.keys()), index=0)
    with col2:
        run_b_label = st.selectbox("Run B", options=list(options.keys()), index=min(1, len(options)-1))

    run_a = df[df["id"] == options[run_a_label]].iloc[0]
    run_b = df[df["id"] == options[run_b_label]].iloc[0]

    st.subheader("Side-by-Side")

    cols = st.columns(3)
    for i, (label, ra, rb) in enumerate(
        [
            ("Distance (mi)", run_a["distance"], run_b["distance"]),
            ("Duration", run_a["duration"], run_b["duration"]),
            ("Avg Pace", run_a.get("avg_pace", ""), run_b.get("avg_pace", "")),
        ]
    ):
        cols[i].markdown(f"**{label}**  \nA: {ra}  \nB: {rb}")

    cols2 = st.columns(3)
    for i, (label, ra, rb) in enumerate(
        [
            ("Avg HR", run_a.get("avg_hr", ""), run_b.get("avg_hr", "")),
            ("Max HR", run_a.get("max_hr", ""), run_b.get("max_hr", "")),
            ("Effort", run_a.get("effort", ""), run_b.get("effort", "")),
        ]
    ):
        cols2[i].markdown(f"**{label}**  \nA: {ra}  \nB: {rb}")

    st.markdown("### Notes / Feel")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Run A ({run_a['date']})**")
        st.write(run_a.get("felt", ""))
    with c2:
        st.markdown(f"**Run B ({run_b['date']})**")
        st.write(run_b.get("felt", ""))


def main():
    render_compare_runs_page()


if __name__ == "__main__":
    main()

