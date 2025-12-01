import streamlit as st
import pandas as pd

from utils.database import fetch_runs
from utils.metrics import prepare_metrics_df
from utils.prs import calculate_prs


def render_dashboard_page():
    st.title("📊 Dashboard")
    st.caption("High-level view of your training volume, pacing, and PRs.")

    df = fetch_runs()
    if df.empty:
        st.info("Log some runs (or import from Garmin) to view insights here.")
        return

    metrics = prepare_metrics_df(df)
    prs = calculate_prs(metrics)

    # Ensure we have a datetime column for time windows
    if "date_dt" in metrics.columns:
        metrics_dt = metrics
    else:
        metrics_dt = metrics.copy()
        metrics_dt["date_dt"] = pd.to_datetime(metrics_dt["date"], errors="coerce")

    # -------------------------------------------------
    # SUMMARY STATS CARD
    # -------------------------------------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📈 Summary Stats")

    total_miles = metrics["distance"].sum()
    total_runs = len(metrics)

    avg_pace = metrics["pace_seconds"].mean()
    avg_pace_str = (
        str(pd.to_timedelta(avg_pace, unit="s")) if pd.notna(avg_pace) else "N/A"
    )

    # 30-day stats
    cutoff_30 = pd.Timestamp.today() - pd.Timedelta(days=30)
    last_30 = metrics_dt[metrics_dt["date_dt"] >= cutoff_30]

    miles_30 = last_30["distance"].sum() if not last_30.empty else 0.0
    runs_30 = len(last_30) if not last_30.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Miles", f"{total_miles:.1f}")
    c2.metric("Total Runs", total_runs)
    c3.metric("Avg Pace", avg_pace_str)
    c4.metric("Last 30 Days", f"{miles_30:.1f} mi in {runs_30} runs")

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # RECENT RUNS TABLE
    # -------------------------------------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🗓️ Recent Runs")

    recent_df = df.sort_values("date", ascending=False).head(10)

    st.dataframe(
        recent_df[
            [
                "date",
                "run_type",
                "distance",
                "duration",
                "avg_hr",
                "effort",
            ]
        ],
        use_container_width=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # SIMPLE TREND VIEW (WEEKLY MILEAGE)
    # -------------------------------------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📆 Weekly Mileage (Quick View)")

    metrics_dt["year_week"] = metrics_dt["date_dt"].dt.strftime("%Y-W%V")
    weekly = (
        metrics_dt.groupby("year_week", dropna=True)["distance"]
        .sum()
        .reset_index(name="miles")
    ).sort_values("year_week", ascending=True)

    if not weekly.empty:
        st.dataframe(weekly.tail(8), use_container_width=True)
    else:
        st.info("Not enough data yet to build a weekly mileage trend.")

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # PR BOARD (PRETTIER)
    # -------------------------------------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🏅 PR Board")

    if not prs:
        st.write("No PRs calculated yet. Keep running and they’ll show up here!")
    else:
        # Turn whatever structure we have into a clean table
        rows = []

        if isinstance(prs, dict):
            for key, val in prs.items():
                # Simple scalar: "Longest": 3
                if isinstance(val, (int, float, str)):
                    rows.append({"PR / Metric": key, "Value": val})
                # Nested dict: e.g. {"5K": {"time": "...", "pace": "..."}}
                elif isinstance(val, dict):
                    for subk, subv in val.items():
                        rows.append(
                            {"PR / Metric": f"{key} – {subk}", "Value": subv}
                        )
                # Anything else -> string
                else:
                    rows.append({"PR / Metric": key, "Value": str(val)})
        else:
            # Fallback – just show as string
            rows.append({"PR / Metric": "All", "Value": str(prs)})

        pr_df = pd.DataFrame(rows)

        st.dataframe(pr_df, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


def main():
    render_dashboard_page()


if __name__ == "__main__":
    main()
