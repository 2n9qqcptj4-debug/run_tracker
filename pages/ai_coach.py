import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_lottie import st_lottie
import requests

from utils.database import fetch_runs
from utils.metrics import prepare_metrics_df
from utils.prs import calculate_prs
from utils.ai_helpers import call_ai


# ------------------------------------------------------
# Load Lottie Animation
# ------------------------------------------------------
def load_lottie(url: str):
    try:
        return requests.get(url).json()
    except:
        return None


# ------------------------------------------------------
# Efficiency Score (Safe version)
# ------------------------------------------------------
def compute_efficiency_score(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        metrics["efficiency_score"] = None
        return metrics

    m = metrics.copy()
    m["efficiency_score"] = None

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
    except:
        pass

    return m


# ------------------------------------------------------
# MAIN AI COACH PAGE
# ------------------------------------------------------
def render_ai_coach_page():
    st.title("🤖 AI Coach")
    st.caption("Your personalized running insights powered by data + AI.")

    # Lottie animation header
    lottie = load_lottie("https://assets5.lottiefiles.com/packages/lf20_tk1bdz9z.json")
    if lottie:
        st_lottie(lottie, height=180, key="lottie_header")

    df = fetch_runs()
    if df.empty:
        st.info("Log your first run to unlock AI analysis.")
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

    # ------------------------------------------------------
    # Highlight Stats
    # ------------------------------------------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Training Snapshot (Last 7 Days)")

    colA, colB, colC = st.columns(3)
    colA.metric("Last Run", f"{latest.get('distance')} mi", latest.get("duration"))
    colB.metric("Mileage (7d)", f"{df.tail(7)['distance'].sum():.1f} mi")
    colC.metric("VO2 Max", latest.get("vo2max", "—"))

    st.markdown("</div>", unsafe_allow_html=True)
    st.write("")

    # ------------------------------------------------------
    # Tabs with fade-in content
    # ------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📅 Daily + Weekly",
        "⚡ Workout Generator",
        "🗓️ 7-Day Planner",
        "🏁 Race Simulator",
        "🩻 Injury Risk",
        "🎖️ PR Milestones",
        "📦 Training Block",
    ])

    # ======================================================
    # TAB 1
    # ======================================================
    with tab1:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)

        st.markdown('<div class="section-header">🏃 Last Run Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Date:** {latest.get('date')}")
            st.write(f"**Type:** {latest.get('run_type')}")
            st.write(f"**Distance:** {latest.get('distance')} mi")

        with col2:
            st.write(f"**Duration:** {latest.get('duration')}")
            st.write(f"**Avg Pace:** {latest.get('avg_pace')}")
            st.write(f"**Avg HR:** {latest.get('avg_hr') or '—'} bpm")

        if st.button("🔍 Analyze Last Run", key="btn_last_run"):
            with st.spinner("Analyzing your run…"):
                result = call_ai(f"""
Analyze this run:
{latest}

Return:
- pacing overview
- HR interpretation
- biomechanics or form observations
- fatigue / recovery indicators
- injury risk
- 3–5 concise next steps
""")

            with st.expander("📘 AI Insights", expanded=True):
                st.markdown(
                    f"""
                    <div style='padding:18px;background:rgba(255,255,255,0.04);
                    border-left:4px solid #4a90e2;border-radius:10px;line-height:1.6;'>
                    {result}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown('</div>', unsafe_allow_html=True)

        # WEEKLY SUMMARY
        st.markdown('<div class="section-header">📅 Weekly Summary</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)

        week_mask = pd.to_datetime(df["date"]) >= (datetime.today() - timedelta(days=7))
        last7 = df[week_mask]

        if not last7.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Mileage", f"{last7['distance'].sum():.1f} mi")
            c2.metric("Runs", len(last7))
            if "effort" in last7:
                c3.metric("Avg Effort", f"{last7['effort'].mean():.1f}/10")

        if st.button("📊 Analyze Week", key="btn_week"):
            with st.spinner("Generating weekly insights…"):
                result = call_ai(f"Weekly summary for: {last7.to_dict('records')}")

            with st.expander("📘 Weekly Insights", expanded=True):
                st.markdown(
                    f"""
                    <div style='padding:18px;background:rgba(255,255,255,0.04);
                    border-left:4px solid #4a90e2;border-radius:10px;line-height:1.6;'>
                    {result}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ======================================================
    # TAB 2 — WORKOUT GENERATOR
    # ======================================================
    with tab2:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)

        st.markdown('<div class="section-header">⚡ Generate Tomorrow\'s Workout</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)

        focus = st.selectbox("Primary Focus", ["Balanced","Speed","Endurance","Tempo","Recovery"], key="wg_focus")
        terrain = st.selectbox("Terrain", ["Road","Trail","Treadmill","Hilly"], key="wg_terrain")
        time_avail = st.slider("Available Time (minutes)", 20, 150, 60, key="wg_time")

        if st.button("⚡ Generate Workout", key="btn_wg"):
            with st.spinner("Designing workout…"):
                result = call_ai(f"""
Create a structured workout.

Focus: {focus}
Terrain: {terrain}
Time available: {time_avail}

Recent training:
{recent.to_dict('records')}
""")

            with st.expander("🏋️ Workout Plan", expanded=True):
                st.markdown(
                    f"""
                    <div style='padding:18px;background:rgba(255,255,255,0.04);
                    border-left:4px solid #f39c12;border-radius:10px;line-height:1.6;'>
                    {result}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ======================================================
    # TAB 3 — 7-DAY PLANNER
    # ======================================================
    with tab3:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)

        st.markdown('<div class="section-header">🗓️ Plan Your Next 7 Days</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)

        days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

        days_week = st.slider("Days per Week", 2, 7, 5, key="planner_days_week")
        training_days = st.multiselect("Training Days", days, default=["Mon","Tue","Thu","Sat","Sun"], key="planner_training")
        hard_days = st.multiselect("Hard Days", days, default=["Tue","Thu"], key="planner_hard")
        rest_days = st.multiselect("Rest Days", days, default=["Fri"], key="planner_rest")
        long_day = st.selectbox("Long Run Day", days, index=6, key="planner_long")

        if st.button("🗓️ Generate Weekly Plan", key="btn_7day"):
            with st.spinner("Creating your training week…"):
                result = call_ai(f"""
Generate a 7-day plan.

Training days: {training_days}
Hard days: {hard_days}
Rest days: {rest_days}
Long run: {long_day}

Recent training:
{recent.to_dict('records')}
""")

            with st.expander("📅 Weekly Plan", expanded=True):
                st.markdown(
                    f"""
                    <div style='padding:18px;background:rgba(255,255,255,0.04);
                    border-left:4px solid #2ecc71;border-radius:10px;line-height:1.6;'>
                    {result}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ======================================================
    # TAB 4 — RACE SIMULATION
    # ======================================================
    with tab4:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)

        st.markdown('<div class="section-header">🏁 Race Simulation</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)

        race_type = st.selectbox("Race", ["5K","10K","Half Marathon","Marathon"], index=2, key="race_type")
        strategy = st.selectbox("Strategy", ["Conservative","Even","Negative Split","Aggressive"], key="race_strategy")

        if st.button("🏁 Simulate Race", key="btn_race"):
            with st.spinner("Simulating race…"):
                result = call_ai(f"""
Simulate my {race_type} with:
Strategy: {strategy}
Goal: {race_goal}
Race date: {race_date}

Using my entire training history:
{df.to_dict('records')}
""")

            with st.expander("🏁 Race Simulation Results", expanded=True):
                st.markdown(
                    f"""
                    <div style='padding:18px;background:rgba(255,255,255,0.04);
                    border-left:4px solid #e74c3c;border-radius:10px;line-height:1.6;'>
                    {result}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ======================================================
    # TAB 5 — INJURY RISK
    # ======================================================
    with tab5:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)

        st.markdown('<div class="section-header">🩻 Injury Risk Evaluation</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)

        lookback = st.slider("Lookback (days)", 7, 42, 21, key="injury_lookback")
        window = df[pd.to_datetime(df["date"]) >= (datetime.today() - timedelta(days=lookback))]

        if st.button("🩻 Evaluate Injury Risk", key="btn_injury"):
            with st.spinner("Analyzing injury risk…"):
                result = call_ai(f"""
Evaluate my injury risk with focus on shin splints.
Lookback: {lookback} days

Runs:
{window.to_dict('records')}
""")

            with st.expander("🩻 Injury Insights", expanded=True):
                st.markdown(
                    f"""
                    <div style='padding:18px;background:rgba(255,255,255,0.04);
                    border-left:4px solid #9b59b6;border-radius:10px;line-height:1.6;'>
                    {result}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ======================================================
    # TAB 6 — PR MILESTONES
    # ======================================================
    with tab6:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)

        st.markdown('<div class="section-header">🎖️ PR Milestones</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.write("Your current PRs:")
        st.json(prs_all or {})

        if st.button("🎯 Analyze PR Progress", key="btn_pr"):
            with st.spinner("Analyzing PR progression…"):
                result = call_ai(f"""
Analyze my PR progression and improvement trends.

Metrics:
{metrics.to_dict('records')}

PRs:
{prs_all}
""")

            with st.expander("🎯 PR Insights", expanded=True):
                st.markdown(
                    f"""
                    <div style='padding:18px;background:rgba(255,255,255,0.04);
                    border-left:4px solid #3498db;border-radius:10px;line-height:1.6;'>
                    {result}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ======================================================
    # TAB 7 — TRAINING BLOCK
    # ======================================================
    with tab7:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)

        st.markdown('<div class="section-header">📦 Training Block Generator</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)

        # Race Type
        block_race = st.selectbox(
            "Race Type",
            ["5K","10K","Half Marathon","Marathon","50K","50 Mile","100K","100 Mile"],
            index=2,
            key="tb_race"
        )

        # Goal Mode
        goal_mode = st.radio("Goal Mode", ["Finish","Specific Time"], key="tb_goal_mode")
        goal_time = st.text_input("Target Time (HH:MM:SS)", key="tb_goal_time") \
            if goal_mode == "Specific Time" else None

        # 🗓️ Race Date Input (NEW)
        st.markdown("### 🗓️ Race Date")
        race_date_block = st.date_input(
            "Select your race date:",
            value=datetime.today().date() + timedelta(weeks=12),
            key="tb_race_date"
        )

        # Calculate weeks automatically (NEW)
        today = datetime.today().date()
        weeks_until_race = max(1, (race_date_block - today).days // 7)

        st.markdown(
            f"**Time until race:** `{weeks_until_race}` weeks (automatically calculated)"
        )

        # Optional override (NEW)
        auto_override = st.checkbox(
            "Override training block length?",
            value=False,
            key="tb_override"
        )

        if auto_override:
            block_weeks = st.slider(
                "Training Block Length (weeks)",
                min_value=4,
                max_value=28,
                value=weeks_until_race,
                key="tb_weeks"
            )
        else:
            block_weeks = weeks_until_race

        # Taper
        taper = st.selectbox(
            "Taper Length",
            ["1 week","10 days","2 weeks","3 weeks"],
            key="tb_taper"
        )

        # Schedule prefs
        days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        train_days = st.multiselect("Training Days", days, default=["Mon","Tue","Thu","Sat","Sun"], key="tb_days")
        hard_days = st.multiselect("Hard Days", days, default=["Tue","Thu"], key="tb_hard")
        rest_days = st.multiselect("Rest Days", days, default=["Fri"], key="tb_rest")
        long_day = st.selectbox("Long Run Day", days, index=6, key="tb_long")

        # Generate training block
        if st.button("📦 Generate Training Block", key="btn_tb"):
            with st.spinner("Building your custom training block…"):
                result = call_ai(f"""
Build a structured {block_weeks}-week training block.

Race: {block_race}
Race date: {race_date_block}
Weeks until race: {block_weeks}

Goal: {goal_mode}
Target time: {goal_time}

Training schedule:
Days: {train_days}
Hard days: {hard_days}
Rest days: {rest_days}
Long run day: {long_day}

Training history:
{df.to_dict('records')}

PRs:
{prs_all}
""")

            with st.expander("📦 Training Block Plan", expanded=True):
                st.markdown(
                    f"""
                    <div style='padding:18px;background:rgba(255,255,255,0.04);
                    border-left:4px solid #1abc9c;border-radius:10px;line-height:1.6;'>
                    {result}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)



def main():
    render_ai_coach_page()


if __name__ == "__main__":
    main()
