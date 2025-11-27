import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils.database import fetch_runs
from utils.metrics import prepare_metrics_df
from utils.prs import calculate_prs
from utils.ai_helpers import call_ai


# ---------------------------
# SAFE efficiency score
# ---------------------------

def compute_efficiency_score(metrics: pd.DataFrame) -> pd.DataFrame:
    """
    Safe calculation of efficiency_score that will NOT error
    even if duration_seconds or avg_hr are missing.
    """

    if metrics.empty:
        metrics["efficiency_score"] = None
        return metrics

    m = metrics.copy()
    m["efficiency_score"] = None

    # Ensure required columns exist
    if "duration_seconds" not in m.columns:
        m["duration_seconds"] = None

    if "avg_hr" not in m.columns:
        m["avg_hr"] = None

    # Boolean mask
    mask = (
        m["distance"].notna()
        & (m["distance"] > 0)
        & m["duration_seconds"].notna()
        & (m["duration_seconds"] > 0)
        & m["avg_hr"].notna()
        & (m["avg_hr"] > 0)
    )

    try:
        m.loc[mask, "efficiency_score"] = (
            m.loc[mask, "distance"]
            / (m.loc[mask, "duration_seconds"] / 60.0)
            / m.loc[mask, "avg_hr"]
            * 1000.0
        )
    except Exception:
        pass

    return m


# ================================================================
#    MAIN AI COACH PAGE
# ================================================================

def render_ai_coach_page():
    st.title("🤖 AI Coach")

    df = fetch_runs()
    if df.empty:
        st.info("Log some runs to unlock the AI Coach.")
        st.stop()

    # Metrics
    metrics = prepare_metrics_df(df)
    metrics = compute_efficiency_score(metrics)

    recent = df.tail(30)
    latest = df.iloc[-1].to_dict()

    race_goal = st.session_state.get("race_goal", "Pittsburgh Half – Sub 1:40")
    race_date_str = st.session_state.get("race_date_str", "2026-05-03")

    try:
        race_date = datetime.fromisoformat(race_date_str).date()
    except:
        race_date = datetime.today().date()

    prs_all = calculate_prs(metrics)

    # ---------------------------
    # Tabs
    # ---------------------------
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            "Daily & Weekly",
            "Workout Generator",
            "7-Day Plan",
            "Race Simulator",
            "Injury Risk AI",
            "PR Milestones",
            "Training Block",
        ]
    )

    # ------------------------------------------------------------------
    # TAB 1 — DAILY + WEEKLY
    # ------------------------------------------------------------------
    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Last Run Analysis")

            st.write(
                f"**{latest.get('date')} — {latest.get('run_type')} — {latest.get('distance')} mi**"
            )

            if st.button("Analyze Last Run"):
                prompt = f"""
Analyze my most recent run. Review pacing, HR, fatigue, efficiency, 
and give 3–5 action items.

Run data:
{latest}
"""
                st.write(call_ai(prompt))

        with col2:
            st.subheader("Weekly Summary")

            last7 = df[pd.to_datetime(df["date"]) >= (datetime.today() - timedelta(days=7))]

            if last7.empty:
                st.info("No runs in the last week.")
            else:
                if st.button("Summarize Last 7 Days"):
                    prompt = f"""
Create a weekly training summary.

Last 7 days:
{last7.to_dict('records')}

PR snapshot:
{prs_all}
"""
                    st.write(call_ai(prompt))

    # ------------------------------------------------------------------
    # TAB 2 — WORKOUT GENERATOR
    # ------------------------------------------------------------------
    with tab2:
        st.subheader("Generate Tomorrow's Workout")

        focus = st.selectbox("Focus", ["Balanced", "Speed", "Tempo", "Endurance", "Recovery"])
        terrain = st.selectbox("Terrain", ["Road", "Treadmill", "Trail", "Hilly"])
        time_avail = st.slider("Available time (min)", 20, 150, 60)

        if st.button("Generate Workout"):
            prompt = f"""
Create tomorrow's workout.

Focus: {focus}
Terrain: {terrain}
Available Time: {time_avail} minutes

Recent training:
{recent.to_dict('records')}
"""
            st.write(call_ai(prompt))

    # ------------------------------------------------------------------
    # TAB 3 — 7-DAY PLAN
    # ------------------------------------------------------------------
    with tab3:
        st.subheader("Plan Next 7 Days")

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        d_per_week = st.slider("Days per week", 2, 7, 5)
        train_days = st.multiselect("Training days", days, default=["Mon", "Tue", "Thu", "Sat", "Sun"])
        hard_days = st.multiselect("Hard days", days, default=["Tue", "Thu"])
        rest_days = st.multiselect("Rest days", days, default=["Fri"])
        long_day = st.selectbox("Long run day", days, index=6)

        if st.button("Generate 7-Day Plan"):
            prompt = f"""
Design a 7-day running plan.

Days/week: {d_per_week}
Training Days: {train_days}
Hard Days: {hard_days}
Rest Days: {rest_days}
Long Run Day: {long_day}

Recent runs:
{recent.to_dict('records')}
"""
            st.write(call_ai(prompt))

    # ------------------------------------------------------------------
    # TAB 4 — RACE SIMULATOR
    # ------------------------------------------------------------------
    with tab4:
        st.subheader("Race Day Simulator")

        race_type = st.selectbox("Race Type", ["5K", "10K", "Half Marathon", "Marathon"], index=2)
        strategy = st.selectbox("Strategy", ["Conservative", "Even Split", "Negative Split", "Aggressive"])

        if st.button("Simulate Race"):
            prompt = f"""
Simulate my {race_type} race on {race_date}.

Strategy: {strategy}
Goal: {race_goal}

Full training history:
{df.to_dict('records')}
"""
            st.write(call_ai(prompt))

    # ------------------------------------------------------------------
    # TAB 5 — INJURY RISK
    # ------------------------------------------------------------------
    with tab5:
        st.subheader("Injury Risk (Shin Splint Focus)")

        lookback = st.slider("Look back days", 7, 42, 21)
        window = df[pd.to_datetime(df["date"]) >= (datetime.today() - timedelta(days=lookback))]

        if st.button("Evaluate Injury Risk"):
            prompt = f"""
Evaluate injury risk (shin splints focus).

Training window ({lookback} days):
{window.to_dict('records')}
"""
            st.write(call_ai(prompt))

    # ------------------------------------------------------------------
    # TAB 6 — PR MILESTONES
    # ------------------------------------------------------------------
    with tab6:
        st.subheader("PR Milestone Analysis")

        st.json(prs_all)

        if st.button("Analyze PR Progress"):
            prompt = f"""
Analyze my PR trends and next likely PR breakthrough.

Full metrics:
{metrics.to_dict('records')}

Current PRs:
{prs_all}
"""
            st.write(call_ai(prompt))

    # ------------------------------------------------------------------
    # TAB 7 — TRAINING BLOCK GENERATOR
    # ------------------------------------------------------------------
    with tab7:
        st.subheader("Training Block Builder")

        block_distance = st.selectbox(
            "Race Type",
            ["5K", "10K", "Half Marathon", "Marathon", "50K", "50 Mile", "100K", "100 Mile"],
            index=2
        )

        goal_mode = st.radio("Goal Mode", ["Finish", "Specific Time"])
        target_time = st.text_input("Goal Time (HH:MM:SS)", "") if goal_mode == "Specific Time" else None

        block_weeks = st.slider("Block length (weeks)", 4, 28, 12)
        taper = st.selectbox("Taper length", ["1 week", "10 days", "2 weeks", "3 weeks"])
        cutback = st.checkbox("Mid-block cutback?", True)

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        train_days = st.multiselect("Training Days", days, default=["Mon", "Tue", "Thu", "Sat", "Sun"])
        hard = st.multiselect("Hard Days", days, default=["Tue", "Thu"])
        rest = st.multiselect("Rest Days", days, default=["Fri"])
        long_day = st.selectbox("Long Run Day", days, index=6)
        secondary = st.selectbox("Secondary Long Run", ["None"] + days)

        b2b = st.checkbox("Allow back-to-back hard days?")
        doubles = st.checkbox("Allow doubles (AM/PM)?")

        if st.button("Generate Training Block"):
            prefs = {
                "training_days": train_days,
                "hard_days": hard,
                "rest_days": rest,
                "long_day": long_day,
                "secondary_long": secondary,
                "back_to_back": b2b,
                "doubles": doubles,
            }

            prompt = f"""
Build a {block_weeks}-week training block.

Race: {block_distance}
Goal Mode: {goal_mode}
Target Time: {target_time}

Block Length: {block_weeks}
Taper: {taper}
Cutback: {cutback}

Schedule:
{prefs}

Full training history:
{df.to_dict('records')}

PRs:
{prs_all}
"""
            st.write(call_ai(prompt))


# wrapper
def main():
    render_ai_coach_page()


if __name__ == "__main__":
    main()
