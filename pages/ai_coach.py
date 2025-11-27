import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils.database import fetch_runs
from utils.metrics import prepare_metrics_df
from utils.prs import calculate_prs
from utils.ai_helpers import call_ai


# ---------------------------
# SAFE EFFICIENCY SCORE
# ---------------------------
def compute_efficiency_score(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        metrics["efficiency_score"] = None
        return metrics

    m = metrics.copy()
    m["efficiency_score"] = None

    # Ensure columns exist
    if "duration_seconds" not in m.columns:
        m["duration_seconds"] = None
    if "avg_hr" not in m.columns:
        m["avg_hr"] = None

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



# ============================
#  BEAUTIFUL AI COACH PAGE
# ============================
def render_ai_coach_page():
    st.title("🤖 AI Coach")
    st.caption("Your personalized running guidance powered by advanced analytics + AI.")

    df = fetch_runs()
    if df.empty:
        st.info("Log some runs (or import from Garmin) to unlock AI Coach insights.")
        return

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

    # Smooth layout spacing
    st.markdown(" ")

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            "📅 Daily + Weekly",
            "⚡ Workout Generator",
            "🗓️ 7-Day Planner",
            "🏁 Race Simulator",
            "🩻 Injury Risk",
            "🎖️ PR Milestones",
            "📦 Training Block",
        ]
    )

    # ------------------------------------------------------------------
    # TAB 1 — DAILY + WEEKLY ANALYSIS
    # ------------------------------------------------------------------
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🏃 Last Run Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Date:** {latest.get('date')}")
            st.write(f"**Type:** {latest.get('run_type')}")
            st.write(f"**Distance:** {latest.get('distance')} mi")

        with col2:
            st.write(f"**Duration:** {latest.get('duration')}")
            st.write(f"**Avg Pace:** {latest.get('avg_pace')}")
            st.write(f"**Avg HR:** {latest.get('avg_hr') or '—'} bpm")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        if st.button("🔍 Analyze Last Run", key="ai_last_run_pretty"):
            with st.spinner("Analyzing your run..."):
                result = call_ai(f"""
Provide a polished and structured analysis of the following run:
{latest}

Include:
- pacing & HR interpretation
- biomechanical or form insights
- fatigue & recovery guidance
- injury risk notes
- 3–5 actionable improvements
""")
            st.markdown("### 🧠 AI Insights")
            st.markdown(f"<div class='card'>{result}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # WEEKLY SUMMARY
        week_mask = pd.to_datetime(df["date"]) >= (datetime.today() - timedelta(days=7))
        last7 = df[week_mask]

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📅 Weekly Summary (Last 7 Days)")

        if not last7.empty:
            total_miles = last7["distance"].sum()
            runs_count = len(last7)
            avg_effort = last7["effort"].mean() if "effort" in last7 else None

            c1, c2, c3 = st.columns(3)
            c1.metric("Mileage", f"{total_miles:.1f} mi")
            c2.metric("Runs", runs_count)
            if avg_effort:
                c3.metric("Avg Effort", f"{avg_effort:.1f}/10")

        if st.button("📊 Analyze Week", key="ai_week_pretty"):
            with st.spinner("Reviewing your week..."):
                result = call_ai(f"""
Analyze the last 7 days of training:
{last7.to_dict('records')}

Provide:
- a clean weekly summary
- load progression
- where fatigue or overreaching may appear
- readiness for intervals or long runs
- 2–3 recommended workouts next week
""")
            st.markdown("### 📘 Weekly Insights")
            st.markdown(f"<div class='card'>{result}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)



    # ------------------------------------------------------------------
    # TAB 2 — WORKOUT GENERATOR
    # ------------------------------------------------------------------
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("⚡ Generate Tomorrow's Workout")

        focus = st.selectbox("Primary Focus", ["Balanced", "Speed", "Endurance", "Tempo", "Recovery"])
        terrain = st.selectbox("Terrain", ["Road", "Trail", "Treadmill", "Hilly"])
        time_avail = st.slider("Available Time (minutes)", 20, 150, 60)

        if st.button("⚡ Create Workout", key="gen_workout"):
            with st.spinner("Designing workout..."):
                result = call_ai(f"""
Create a structured workout based on:
Focus: {focus}
Terrain: {terrain}
Time available: {time_avail} minutes

Use athlete context:
{recent.to_dict('records')}

Return:
- warm-up
- main set (intervals, pacing, HR zones)
- cooldown
- execution tips
""")
            st.markdown("### 🏋️ Workout Plan")
            st.markdown(f"<div class='card'>{result}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)



    # ------------------------------------------------------------------
    # TAB 3 — 7-DAY PLAN
    # ------------------------------------------------------------------
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🗓️ Plan the Next 7 Days")

        days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

        days_week = st.slider("Days Per Week", 2, 7, 5)
        training_days = st.multiselect("Training Days", days, default=["Mon","Tue","Thu","Sat","Sun"])
        hard_days = st.multiselect("Hard Workout Days", days, default=["Tue","Thu"])
        rest_days = st.multiselect("Rest Days", days, default=["Fri"])
        long_day = st.selectbox("Long Run Day", days, index=6)

        if st.button("🗓️ Generate 7-Day Plan"):
            with st.spinner("Generating plan..."):
                result = call_ai(f"""
Design a 7-day training plan.

Days per week: {days_week}
Training days: {training_days}
Hard days: {hard_days}
Rest days: {rest_days}
Long run day: {long_day}

Recent training:
{recent.to_dict('records')}
""")
            st.markdown("### 📅 Weekly Plan")
            st.markdown(f"<div class='card'>{result}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)



    # ------------------------------------------------------------------
    # TAB 4 — RACE SIMULATOR
    # ------------------------------------------------------------------
    with tab4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🏁 Race Day Simulator")

        race_type = st.selectbox("Race Type", ["5K","10K","Half Marathon","Marathon"], index=2)
        strategy = st.selectbox("Pacing Strategy", ["Conservative","Even","Negative Split","Aggressive"])

        if st.button("🏁 Simulate Race"):
            with st.spinner("Simulating race..."):
                result = call_ai(f"""
Simulate my {race_type} using {strategy} strategy.
Race goal: {race_goal}
Race date: {race_date}

Use full training history:
{df.to_dict('records')}

Return:
- predicted finish time
- mile splits
- HR guidance
- fueling plan
- mistakes to avoid
""")
            st.markdown("### 🏁 Race Simulation")
            st.markdown(f"<div class='card'>{result}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)



    # ------------------------------------------------------------------
    # TAB 5 — INJURY RISK
    # ------------------------------------------------------------------
    with tab5:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🩻 Injury Risk Assessment")

        lookback = st.slider("Lookback (days)", 7, 42, 21)
        window = df[pd.to_datetime(df["date"]) >= (datetime.today() - timedelta(days=lookback))]

        if st.button("🩻 Evaluate Risk"):
            with st.spinner("Evaluating injury risk..."):
                result = call_ai(f"""
Evaluate injury risk with focus on shin splints.
Lookback window: last {lookback} days.

Training data:
{window.to_dict('records')}
""")
            st.markdown("### 🩻 Risk Analysis")
            st.markdown(f"<div class='card'>{result}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)



    # ------------------------------------------------------------------
    # TAB 6 — PR MILESTONES
    # ------------------------------------------------------------------
    with tab6:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🎖️ PR Analysis")

        st.write("Your current PRs:")
        st.json(prs_all or {})

        if st.button("🎯 Analyze PR Progress"):
            with st.spinner("Analyzing PR progression..."):
                result = call_ai(f"""
Analyze current PRs and likely next breakthrough.

Training metrics:
{metrics.to_dict('records')}

Current PRs:
{prs_all}
""")
            st.markdown("### 🎯 PR Insights")
            st.markdown(f"<div class='card'>{result}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)



    # ------------------------------------------------------------------
    # TAB 7 — TRAINING BLOCK GENERATOR
    # ------------------------------------------------------------------
    with tab7:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📦 Build a Training Block")

        block_race = st.selectbox("Race Type", [
            "5K","10K","Half Marathon","Marathon","50K","50 Mile","100K","100 Mile"
        ], index=2)

        goal_mode = st.radio("Goal Type", ["Finish","Specific Time"])
        goal_time = None
        if goal_mode == "Specific Time":
            goal_time = st.text_input("Target Finish Time (HH:MM:SS)")

        block_weeks = st.slider("Block Length (weeks)", 4, 28, 12)
        taper = st.selectbox("Taper Length", ["1 week","10 days","2 weeks","3 weeks"])

        days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        train_days = st.multiselect("Training Days", days, default=["Mon","Tue","Thu","Sat","Sun"])
        hard = st.multiselect("Hard Days", days, default=["Tue","Thu"])
        rest = st.multiselect("Rest Days", days, default=["Fri"])
        long_day = st.selectbox("Long Run Day", days, index=6)

        if st.button("📦 Generate Training Block"):
            with st.spinner("Building your training block..."):
                result = call_ai(f"""
Build a {block_weeks}-week training block.

Race: {block_race}
Goal: {goal_mode}
Target time: {goal_time}

Schedule preferences:
Training days: {train_days}
Hard days: {hard}
Rest days: {rest}
Long run day: {long_day}

Training history:
{df.to_dict('records')}

Current PRs:
{prs_all}
""")
            st.markdown("### 📦 Training Block Plan")
            st.markdown(f"<div class='card'>{result}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)



# STREAMLIT WRAPPER
def main():
    render_ai_coach_page()


if __name__ == "__main__":
    main()
