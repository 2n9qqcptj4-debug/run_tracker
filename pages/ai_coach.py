import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils.database import fetch_runs
from utils.metrics import prepare_metrics_df
from utils.prs import calculate_prs
from utils.ai_helpers import call_ai


# Local helper since you said compute_efficiency_score isn't in utils.metrics
def compute_efficiency_score(metrics: pd.DataFrame) -> pd.DataFrame:
    """
    Adds an 'efficiency_score' column based on distance, duration, and avg_hr.
    Higher is better.
    """
    if metrics.empty:
        metrics["efficiency_score"] = None
        return metrics

    m = metrics.copy()
    m["efficiency_score"] = None

    mask = (
        m["distance"].notna()
        & (m["distance"] > 0)
        & m["duration_minutes"].notna()
        & m["avg_hr"].notna()
    )

    m.loc[mask, "efficiency_score"] = (
        m.loc[mask, "distance"]
        / (m.loc[mask, "duration_minutes"] / 60.0)
        / m.loc[mask, "avg_hr"]
        * 1000.0
    )

    return m


# =========================
#  AI COACH PAGE
# =========================

st.title("🤖 AI Coach")

df = fetch_runs()
if df.empty:
    st.info("Log some runs (or import from Garmin) to use the AI Coach.")
    st.stop()

# Prepare metrics and helpers
metrics = prepare_metrics_df(df)
metrics = compute_efficiency_score(metrics)

recent = df.tail(30)
latest = df.iloc[-1].to_dict()

race_goal = st.session_state.get("race_goal", "Pittsburgh Half – Sub 1:40")
race_date_str = st.session_state.get("race_date_str", "2026-05-03")
try:
    race_date = datetime.fromisoformat(race_date_str).date()
except Exception:
    race_date = datetime.today().date()

prs_all = calculate_prs(metrics)


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

# ---------------------------------
# TAB 1: Daily & Weekly Overview
# ---------------------------------
with tab1:
    col1, col2 = st.columns(2)

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
- pacing and pacing variability
- HR response and effort level
- efficiency (pace vs HR vs distance)
- fatigue / recovery implications
- injury risk (especially shin splints)
- 3–5 concrete action items for my next few runs

Here is the run as a Python dict:
{latest}
"""
            st.write(call_ai(prompt))

    with col2:
        st.subheader("Weekly Summary")

        last7_mask = pd.to_datetime(df["date"]) >= datetime.today() - timedelta(days=7)
        last7_df = df[last7_mask]

        if last7_df.empty:
            st.info("You don't have any runs in the last 7 days yet.")
        else:
            week_metrics = prepare_metrics_df(last7_df)
            week_metrics = compute_efficiency_score(week_metrics)
            week_prs = calculate_prs(week_metrics)

            st.write("**Last 7 days runs:**")
            st.dataframe(
                last7_df[["date", "run_type", "distance", "avg_pace", "avg_hr", "effort"]],
                use_container_width=True,
            )

            if st.button("Summarize Last 7 Days", key="ai_week_summary"):
                prompt = f"""
You are a professional running coach and data analyst.

Create a detailed training summary for my LAST 7 DAYS of running.
Include:
- total mileage and how it compares to my normal
- key patterns in paces, HR, and effort
- signs of fatigue or overreaching
- what seems to be improving
- what needs attention
- recommended weekly mileage and 1–2 key workouts for next week

Last 7 days runs (as records):
{last7_df.to_dict('records')}

Weekly PR snapshot:
{week_prs}
"""
                st.write(call_ai(prompt))


# ---------------------------------
# TAB 2: Workout Generator
# ---------------------------------
with tab2:
    st.subheader("Generate Tomorrow's Workout")

    focus = st.selectbox(
        "Primary focus",
        ["Balanced", "Speed", "Endurance", "Tempo / Threshold", "Recovery"],
        index=0,
    )

    surface = st.selectbox(
        "Planned terrain",
        ["Road", "Treadmill", "Trail", "Mixed / Hilly"],
        index=0,
    )

    available_time = st.slider(
        "Available time (minutes)", min_value=20, max_value=150, value=60, step=5
    )

    if st.button("Create Tomorrow's Workout", key="ai_tomorrow_workout"):
        prompt = f"""
You are designing TOMORROW'S WORKOUT for a half-marathon-focused runner.

Constraints:
- Focus: {focus}
- Terrain: {surface}
- Available time: {available_time} minutes
- Goal: {race_goal} on {race_date}

Requirements for the workout:
- Include warm-up, main set, and cooldown
- Specify paces (in plain language) and/or HR zones
- Include recovery between reps where relevant
- Explain the purpose of the workout in 2–3 sentences
- End with 3 bullet points for execution tips and common mistakes to avoid

Recent training data (last ~30 runs):
{recent.to_dict('records')}
"""
        st.write(call_ai(prompt))


# ---------------------------------
# TAB 3: 7-Day Plan (with schedule prefs)
# ---------------------------------
with tab3:
    st.subheader("Plan the Next 7 Days")

    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    training_days_per_week = st.slider(
        "Days per week you want to run",
        min_value=2,
        max_value=7,
        value=5,
        key="7d_days_per_week",
    )

    default_training_days = ["Mon", "Tue", "Thu", "Sat", "Sun"]
    training_days = st.multiselect(
        "Which days do you want to train?",
        options=days_of_week,
        default=default_training_days[:training_days_per_week],
        key="7d_training_days",
    )

    hard_days = st.multiselect(
        "Preferred HARD workout days (tempo / intervals)",
        options=days_of_week,
        default=["Tue", "Thu"],
        key="7d_hard_days",
    )

    rest_days = st.multiselect(
        "Preferred rest days",
        options=days_of_week,
        default=["Fri"],
        key="7d_rest_days",
    )

    long_run_day = st.selectbox(
        "Primary long run day", options=days_of_week, index=6, key="7d_long_run_day"
    )

    secondary_options = ["None"] + days_of_week
    secondary_long_run = st.selectbox(
        "Optional secondary long run day (for back-to-back endurance)",
        options=secondary_options,
        index=0,
        key="7d_secondary_long_run",
    )

    allow_back_to_back = st.checkbox(
        "Allow back-to-back hard days", value=False, key="7d_allow_back_to_back"
    )

    allow_doubles = st.checkbox(
        "Allow double days (AM/PM)?", value=False, key="7d_allow_doubles"
    )

    if len(training_days) != training_days_per_week:
        st.warning(
            f"You selected {training_days_per_week} days per week but chose "
            f"{len(training_days)} training days. The AI will still try to honor both, "
            "but you may want to align them."
        )

    if st.button("Generate 7-Day Plan", key="ai_7d_plan"):
        prefs_text = f"""
Training schedule preferences:
- Days per week: {training_days_per_week}
- Training days: {", ".join(training_days) if training_days else "None specified"}
- Key workout days (hard sessions): {", ".join(hard_days) if hard_days else "None specified"}
- Rest days: {", ".join(rest_days) if rest_days else "None specified"}
- Long run day: {long_run_day}
- Secondary long run: {secondary_long_run}
- Allow back-to-back hard days: {"Yes" if allow_back_to_back else "No"}
- Allow doubles (AM/PM): {"Yes" if allow_doubles else "No"}
"""

        prompt = f"""
You are designing a **7-day training plan** for a runner targeting:
- Goal: {race_goal}
- Race date: {race_date}

Use the following training history and preferences to build the plan.

{prefs_text}

Recent runs (most recent ~30):
{recent.to_dict('records')}

Please respond with:
- A day-by-day schedule (Mon–Sun)
- For each day: run type, distance or duration, suggested pacing, and HR guidance
- At most 1 truly hard session and 1 medium session per week unless explicitly justified
- Notes on what the week is trying to accomplish in the bigger training picture
"""
        st.write(call_ai(prompt))


# ---------------------------------
# TAB 4: Race Simulator
# ---------------------------------
with tab4:
    st.subheader("Race Day Simulation")

    race_type = st.selectbox(
        "Race distance",
        ["5K", "10K", "Half Marathon", "Marathon"],
        index=2,
        key="race_sim_type",
    )

    strategy = st.selectbox(
        "Strategy emphasis",
        ["Conservative", "Even-split", "Slight Negative Split", "Aggressive"],
        index=2,
        key="race_sim_strategy",
    )

    if st.button("Simulate Race Performance", key="ai_race_sim"):
        prompt = f"""
Simulate my upcoming {race_type} race.

My main race goal:
- {race_goal}
- Race date: {race_date}
- Preferred pacing strategy: {strategy}

Using my training history below, please:
1. Estimate a realistic finish time range.
2. Provide a **mile-by-mile (or 5K-by-5K)** pacing outline.
3. Give HR zone guidance for early, middle, and late race.
4. Recommend fueling and hydration for race day.
5. Call out 3–4 common mistakes I personally am likely to make based on this training.

Training data (all runs):
{df.to_dict('records')}
"""
        st.write(call_ai(prompt))


# ---------------------------------
# TAB 5: Injury Risk AI
# ---------------------------------
with tab5:
    st.subheader("Injury Risk (with emphasis on shin splints)")

    lookback_days = st.slider(
        "Look back over how many days?",
        min_value=7,
        max_value=42,
        value=21,
        step=7,
        key="injury_lookback",
    )

    cutoff = datetime.today() - timedelta(days=lookback_days)
    window_df = df[pd.to_datetime(df["date"]) >= cutoff]

    st.write(f"Using the last **{lookback_days} days** of training.")

    if st.button("Evaluate Injury Risk", key="ai_injury_risk"):
        prompt = f"""
Evaluate my injury risk with particular focus on **shin splints**.

Look at:
- training load changes (weekly mileage, hard efforts)
- pace spikes
- elevation gain
- sleep / stress (if present)
- any pain notes
- rest days vs hard days

Then:
1. Give a risk rating (Low / Moderate / High) and explain why.
2. Identify the top 3 training patterns that increase risk.
3. Suggest **5–8 very concrete adjustments** for the next 2–3 weeks to reduce injury risk while still progressing.

Training window ({lookback_days} days):
{window_df.to_dict('records')}
"""
        st.write(call_ai(prompt))


# ---------------------------------
# TAB 6: PR Milestones
# ---------------------------------
with tab6:
    st.subheader("PR Milestone Analysis")

    st.write("Current PR snapshot (as calculated from your data):")
    if not prs_all:
        st.info("No PR information could be derived yet. Log more runs.")
    else:
        st.json(prs_all)

    if st.button("Analyze PR Progress & Next Milestones", key="ai_pr_milestones"):
        trend_data = metrics.sort_values("date_dt").to_dict("records")
        prompt = f"""
You are an elite running coach. Analyze my PR progression and likely **next milestone**.

Please:
1. Summarize my current PR profile (speed vs endurance).
2. Identify which PR was most recently improved and why.
3. Highlight which PR is most likely to fall next (e.g., 5K, 10K, half).
4. Give a **6–8 week mini-focus plan** specifically to break that PR.
5. Include 4–6 key workouts with paces or HR guidance.

Training history (metrics with dates and efficiency scores):
{trend_data}

Current PRs:
{prs_all}
"""
        st.write(call_ai(prompt))


# ---------------------------------
# TAB 7: Training Block Generator
# ---------------------------------
with tab7:
    st.subheader("Goal-Based Training Block")

    race_types = [
        "5K",
        "10K",
        "Half Marathon",
        "Marathon",
        "50K Ultra",
        "50 Mile Ultra",
        "100K Ultra",
        "100 Mile Ultra",
    ]
    race_type_block = st.selectbox(
        "What race are you training for?", race_types, index=2, key="block_race_type"
    )

    goal_mode = st.radio(
        "What is your goal?",
        ["Train to Finish", "Train for a Specific Time"],
        key="block_goal_mode",
    )

    target_time = None
    if goal_mode == "Train for a Specific Time":
        target_time = st.text_input(
            "Target finish time (HH:MM:SS)",
            placeholder="e.g., 01:39:59 for sub-1:40 half",
            key="block_target_time",
        )

    race_date_block = st.date_input(
        "Race Date", value=race_date, key="block_race_date"
    )

    block_length_weeks = st.slider(
        "Training Block Length (weeks)",
        min_value=4,
        max_value=28,
        value=12,
        key="block_length_weeks",
    )

    taper_length = st.selectbox(
        "Length of taper",
        ["1 week", "10 days", "2 weeks", "3 weeks"],
        index=2,
        key="block_taper_length",
    )

    mid_block_cutback = st.checkbox(
        "Include a mid-block cutback week (around week 6–8)",
        value=True,
        key="block_cutback",
    )

    st.markdown("### Schedule Preferences")

    days_of_week_block = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    block_training_days = st.multiselect(
        "Training Days",
        days_of_week_block,
        default=["Mon", "Tue", "Thu", "Sat", "Sun"],
        key="block_training_days",
    )

    block_days_per_week = len(block_training_days)

    block_hard_days = st.multiselect(
        "Preferred Hard Days (Tempo / Intervals)",
        days_of_week_block,
        default=["Tue", "Thu"],
        key="block_hard_days",
    )

    block_rest_days = st.multiselect(
        "Rest Days",
        days_of_week_block,
        default=["Fri"],
        key="block_rest_days",
    )

    block_long_run_day = st.selectbox(
        "Long Run Day", days_of_week_block, index=6, key="block_long_run_day"
    )

    block_secondary_long_run = st.selectbox(
        "Optional Secondary Long Run",
        ["None"] + days_of_week_block,
        index=0,
        key="block_secondary_long_run",
    )

    block_allow_back_to_back = st.checkbox(
        "Allow back-to-back hard days", False, key="block_allow_back_to_back"
    )

    block_allow_doubles = st.checkbox(
        "Allow double days (AM/PM)", False, key="block_allow_doubles"
    )

    if st.button("Generate Training Block", key="ai_training_block"):
        prefs_text = f"""
Race Type: {race_type_block}
Goal Mode: {goal_mode}
Target Time: {target_time if target_time else "None — Finish Only"}
Race Date: {race_date_block}

Block Length: {block_length_weeks} weeks
Taper Length: {taper_length}
Mid-Block Cutback Week: {"Yes" if mid_block_cutback else "No"}

Training Days Per Week: {block_days_per_week}
Training Days: {", ".join(block_training_days)}
Hard Days: {", ".join(block_hard_days)}
Rest Days: {", ".join(block_rest_days)}
Long Run Day: {block_long_run_day}
Secondary Long Run: {block_secondary_long_run}

Allow Back-to-Back Hard Days: {"Yes" if block_allow_back_to_back else "No"}
Allow Doubles: {"Yes" if block_allow_doubles else "No"}
"""

        prompt = f"""
You are a world-class running coach. Build a {block_length_weeks}-week
**training block** for this athlete.

### ATHLETE GOAL
- Race: {race_type_block}
- Goal: {goal_mode}
- Target Time: {target_time if target_time else "None — Train to finish strong"}
- Race Date: {race_date_block}

### TAPER
- Taper duration: {taper_length}
- Include mid-block cutback: {"Yes" if mid_block_cutback else "No"}

### TRAINING PREFERENCES
{prefs_text}

### REQUIREMENTS FOR THE PLAN
1. Divide training into **Base → Build → Peak → Taper**.
2. Progress weekly mileage gradually with sensible cutback weeks.
3. Integrate preferred training days and long-run placement.
4. For \"Train to Finish\", emphasize aerobic conditioning, long runs, fueling, and durability.
5. For time goals, integrate appropriate **threshold, tempo, VO2, and sharpening**.
6. For EACH WEEK, show:
   - total mileage
   - key workouts
   - long run details
   - focus of the week
7. Make it realistic based on this training history.

### Training History (all runs):
{df.to_dict('records')}

### Current PRs:
{prs_all}
"""
        st.write(call_ai(prompt))
