import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils.database import fetch_runs
from utils.metrics import prepare_metrics_df
from utils.prs import calculate_prs
from utils.ai_helpers import call_ai


# --- FIXED efficiency-score helper (Option 1: uses duration_seconds) ---
def compute_efficiency_score(metrics: pd.DataFrame) -> pd.DataFrame:
    """
    Adds an 'efficiency_score' based on distance, duration_seconds, and avg_hr.
    Higher score = more efficient.
    """

    if metrics.empty:
        metrics["efficiency_score"] = None
        return metrics

    m = metrics.copy()
    m["efficiency_score"] = None

    mask = (
        m["distance"].notna()
        & (m["distance"] > 0)
        & m["duration_seconds"].notna()
        & m["avg_hr"].notna()
    )

    m.loc[mask, "efficiency_score"] = (
        m.loc[mask, "distance"]
        / (m.loc[mask, "duration_seconds"] / 60.0)
        / m.loc[mask, "avg_hr"]
        * 1000.0
    )

    return m


# ============================
#  AI COACH PAGE
# ============================

def render_ai_coach_page():
    st.title("🤖 AI Coach")

    # Load full run log
    df = fetch_runs()
    if df.empty:
        st.info("Log some runs (or import from Garmin) to use the AI Coach.")
        st.stop()

    # Prepare metrics
    metrics = prepare_metrics_df(df)
    metrics = compute_efficiency_score(metrics)

    # data windows
    recent = df.tail(30)
    latest = df.iloc[-1].to_dict()

    # Race goal stored in session
    race_goal = st.session_state.get("race_goal", "Pittsburgh Half – Sub 1:40")
    race_date_str = st.session_state.get("race_date_str", "2026-05-03")
    try:
        race_date = datetime.fromisoformat(race_date_str).date()
    except Exception:
        race_date = datetime.today().date()

    prs_all = calculate_prs(metrics)

    # 7 Tabs
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

    # ================================================================
    # TAB 1 — DAILY + WEEKLY
    # ================================================================
    with tab1:

        col1, col2 = st.columns(2)

        # ---- Last Run Review ----
        with col1:
            st.subheader("Last Run Analysis")
            st.write(
                f"**Most recent run:** {latest.get('date', 'N/A')} — "
                f"{latest.get('run_type', 'Unknown')} — "
                f"{latest.get('distance', 'N/A')} mi"
            )

            if st.button("Analyze Last Run", key="ai_last_run"):
                prompt = f"""
You are a professional running coach and data analyst.

Please analyze my most recent run in detail. Cover:
- pacing consistency
- HR response & efficiency
- fatigue and recovery needs
- injury risk (shin splint focus)
- 3–5 actionable takeaways

Run data:
{latest}
"""
                st.write(call_ai(prompt))

        # ---- Weekly Review ----
        with col2:
            st.subheader("Weekly Summary")

            last7_mask = pd.to_datetime(df["date"]) >= datetime.today() - timedelta(days=7)
            last7_df = df[last7_mask]

            if last7_df.empty:
                st.info("No runs in last 7 days.")
            else:
                week_metrics = prepare_metrics_df(last7_df)
                week_metrics = compute_efficiency_score(week_metrics)
                week_prs = calculate_prs(week_metrics)

                st.write("**Last 7 days:**")
                st.dataframe(
                    last7_df[
                        ["date", "run_type", "distance", "duration", "avg_hr", "effort"]
                    ],
                    use_container_width=True,
                )

                if st.button("Summarize Last 7 Days", key="ai_week_summary"):
                    prompt = f"""
Create a detailed summary of my last 7 days of training.
Cover mileage, HR, pace trends, fatigue, recovery, and suggested next steps.

Last 7 runs:
{last7_df.to_dict('records')}

Weekly PR snapshot:
{week_prs}
"""
                    st.write(call_ai(prompt))

    # ================================================================
    # TAB 2 — WORKOUT GENERATOR
    # ================================================================
    with tab2:
        st.subheader("Generate Tomorrow’s Workout")

        focus = st.selectbox(
            "Primary focus",
            ["Balanced", "Speed", "Endurance", "Tempo / Threshold", "Recovery"],
        )

        terrain = st.selectbox(
            "Terrain",
            ["Road", "Treadmill", "Trail", "Mixed/Hills"],
        )

        available_time = st.slider(
            "Available time (minutes)",
            min_value=20, max_value=150, value=60, step=5
        )

        if st.button("Create Workout", key="ai_tomorrow"):
            prompt = f"""
Design TOMORROW'S WORKOUT.

Focus: {focus}
Terrain: {terrain}
Available Time: {available_time} minutes
Race Goal: {race_goal} on {race_date}

Requirements:
- warm-up + main set + cooldown
- clear pacing instructions
- HR guidance
- execution tips

Recent training (~30 runs):
{recent.to_dict('records')}
"""
            st.write(call_ai(prompt))

    # ================================================================
    # TAB 3 — 7-DAY PLAN
    # ================================================================
    with tab3:
        st.subheader("Plan Next 7 Days")

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        days_per_week = st.slider(
            "Days per week",
            min_value=2, max_value=7, value=5
        )

        training_days = st.multiselect(
            "Training Days", options=days,
            default=["Mon", "Tue", "Thu", "Sat", "Sun"]
        )

        hard_days = st.multiselect(
            "Hard Days (Tempo/Intervals)", options=days,
            default=["Tue", "Thu"]
        )

        rest_days = st.multiselect(
            "Rest Days", options=days,
            default=["Fri"]
        )

        long_run_day = st.selectbox("Long Run Day", options=days, index=6)

        secondary_long = st.selectbox(
            "Optional Second Long Run",
            ["None"] + days
        )

        allow_back_to_back = st.checkbox("Allow back-to-back hard days?")
        allow_doubles = st.checkbox("Allow double days (AM/PM)?")

        if st.button("Generate 7-Day Plan", key="ai_week_plan"):
            prefs = f"""
Days/week: {days_per_week}
Training Days: {training_days}
Hard Days: {hard_days}
Rest Days: {rest_days}
Long Run Day: {long_run_day}
Secondary Long Run: {secondary_long}
Back-to-back: {allow_back_to_back}
Doubles: {allow_doubles}
"""

            prompt = f"""
Design a **7-day training plan** for a half-marathon-focused runner.

Training preferences:
{prefs}

Recent training (~30 runs):
{recent.to_dict('records')}

Return Mon-Sun schedule with run type, distance, pacing/HR, and weekly goals.
"""
            st.write(call_ai(prompt))

    # ================================================================
    # TAB 4 — RACE SIMULATOR
    # ================================================================
    with tab4:
        st.subheader("Race Day Simulator")

        race_type = st.selectbox(
            "Race Distance",
            ["5K", "10K", "Half Marathon", "Marathon"],
            index=2
        )

        strategy = st.selectbox(
            "Strategy",
            ["Conservative", "Even Split", "Slight Negative Split", "Aggressive"],
            index=2
        )

        if st.button("Simulate Race", key="ai_race"):
            prompt = f"""
Simulate my upcoming {race_type} race.

Race Goal: {race_goal}
Race Date: {race_date}
Strategy: {strategy}

Provide:
- realistic finish time
- mile-by-mile pacing
- HR guidance
- fueling plan
- mistakes to avoid

Full training history:
{df.to_dict('records')}
"""
            st.write(call_ai(prompt))

    # ================================================================
    # TAB 5 — INJURY RISK
    # ================================================================
    with tab5:
        st.subheader("Injury Risk Assessment")

        lookback = st.slider(
            "Look back (days)",
            min_value=7, max_value=42, value=21, step=7
        )

        cutoff = datetime.today() - timedelta(days=lookback)
        window_df = df[pd.to_datetime(df["date"]) >= cutoff]

        st.write(f"Using last **{lookback} days** of training.")

        if st.button("Evaluate Injury Risk", key="ai_injury"):
            prompt = f"""
Evaluate my injury risk (shin splint focus).

Look at:
- mileage changes
- HR stress
- elevation load
- effort levels
- pain notes
- rest day spacing

Return risk level + actionable adjustments.

Training window:
{window_df.to_dict('records')}
"""
            st.write(call_ai(prompt))

    # ================================================================
    # TAB 6 — PR MILESTONES
    # ================================================================
    with tab6:
        st.subheader("PR Milestone Analysis")

        st.write("Current PRs:")
        st.json(prs_all or {})

        if st.button("Analyze PRs", key="ai_prs"):
            trend = metrics.sort_values("date_dt").to_dict("records")
            prompt = f"""
Analyze my PR profile, progression, and likely next breakthrough.

Training data:
{trend}

Current PRs:
{prs_all}

Provide:
- strongest/weakest PRs
- next likely improvement
- 6–8 week PR mini-plan
- 4–6 key workouts
"""
            st.write(call_ai(prompt))

    # ================================================================
    # TAB 7 — TRAINING BLOCK
    # ================================================================
    with tab7:
        st.subheader("Build a Training Block")

        race_types = [
            "5K", "10K", "Half Marathon", "Marathon",
            "50K Ultra", "50 Mile Ultra", "100K Ultra", "100 Mile Ultra"
        ]

        block_race = st.selectbox("Race Type", race_types, index=2)

        goal_mode = st.radio(
            "Goal Type",
            ["Train to Finish", "Train for a Specific Time"]
        )

        target_time = None
        if goal_mode == "Train for a Specific Time":
            target_time = st.text_input(
                "Target Finish Time (HH:MM:SS)",
                placeholder="e.g., 01:40:00"
            )

        block_race_date = st.date_input("Race Date", value=race_date)

        block_length = st.slider(
            "Block Length (weeks)",
            min_value=4, max_value=28, value=12
        )

        taper = st.selectbox(
            "Taper Length",
            ["1 week", "10 days", "2 weeks", "3 weeks"],
            index=2
        )

        cutback = st.checkbox(
            "Include mid-block cutback (week 6–8)?", value=True
        )

        st.markdown("### Schedule Preferences")

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        block_days = st.multiselect(
            "Training Days",
            days,
            default=["Mon", "Tue", "Thu", "Sat", "Sun"]
        )
        block_days_per_week = len(block_days)

        block_hard = st.multiselect(
            "Hard Days (tempo/interval)",
            days,
            default=["Tue", "Thu"]
        )

        block_rest = st.multiselect(
            "Rest Days",
            days,
            default=["Fri"]
        )

        block_long = st.selectbox(
            "Long Run Day",
            days,
            index=6
        )

        block_secondary = st.selectbox(
            "Optional Secondary Long Run",
            ["None"] + days
        )

        allow_b2b = st.checkbox("Allow back-to-back hard days?")
        allow_doubles = st.checkbox("Allow double days (AM/PM)?")

        if st.button("Generate Training Block", key="ai_block"):
            prefs = f"""
Block Length: {block_length} weeks
Taper: {taper}
Cutback: {cutback}

Training Days: {block_days}
Days/Week: {block_days_per_week}
Hard Days: {block_hard}
Rest Days: {block_rest}
Long Run Day: {block_long}
Secondary Long Run: {block_secondary}
Back-to-back: {allow_b2b}
Doubles: {allow_doubles}
"""

            prompt = f"""
Build a {block_length}-week training block for the athlete.

Race: {block_race}
Goal Mode: {goal_mode}
Target Time: {target_time}
Race Date: {block_race_date}

Preferences:
{prefs}

Requirements:
- Base → Build → Peak → Taper
- Progressive mileage
- Cutback if chosen
- Realistic workouts
- Weekly breakdowns (key workouts + long run)
- Paces + HR guidance
- Summary for each phase

Training History:
{df.to_dict('records')}

Current PRs:
{prs_all}
"""
            st.write(call_ai(prompt))


# Streamlit wrapper
def main():
    render_ai_coach_page()


if __name__ == "__main__":
    main()
