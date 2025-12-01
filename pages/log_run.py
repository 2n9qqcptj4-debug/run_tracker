import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils.database import add_run  # must exist in utils/database.py


# =====================================================
# FLEXIBLE + SAFE DURATION PARSER
# =====================================================
def parse_duration_input(t: str):
    """
    Accepts flexible formats:

    - "45"        -> 45 seconds
    - "5:43"      -> 5 min, 43 sec
    - "45:10"     -> 45 min, 10 sec
    - "1:02:15"   -> 1 hr, 2 min, 15 sec
    - "HH:MM:SS"  generic
    - "MM:SS"     generic

    Returns:
        (total_seconds: int | None, pretty_str: str | None)
    """
    if not t or not isinstance(t, str):
        return None, None

    t = t.strip()

    # Case: plain integer -> seconds
    if t.isdigit():
        sec = int(t)
        return sec, str(timedelta(seconds=sec))

    # Try direct pandas to_timedelta
    try:
        parsed = pd.to_timedelta(t)
        return int(parsed.total_seconds()), str(parsed)
    except Exception:
        pass

    # Case: MM:SS → prepend 00:
    if t.count(":") == 1:
        try:
            parsed = pd.to_timedelta("00:" + t)
            return int(parsed.total_seconds()), str(parsed)
        except Exception:
            pass

    # Case: HH:MM:SS (or similar) but possibly messy
    if t.count(":") == 2:
        try:
            parsed = pd.to_timedelta(t)
            return int(parsed.total_seconds()), str(parsed)
        except Exception:
            pass

    # If all parsing failed
    return None, None


# =====================================================
# PAGE RENDER
# =====================================================
def render_log_run():
    st.title("📝 Log a Run")
    st.caption("Capture your workout details, how you felt, and key training metrics.")

    with st.form("log_run_form", clear_on_submit=True):
        # ============================================
        # RUN DETAILS CARD
        # ============================================
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🏃 Run Details")

        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("Date", datetime.today())

            run_type = st.selectbox(
                "Run Type",
                [
                    "Easy",
                    "Long Run",
                    "Tempo",
                    "Threshold",
                    "Interval",
                    "Recovery",
                    "Progression",
                    "Race",
                    "Hill Repeats",
                    "Fartlek",
                    "Walk",
                    "Other",
                ],
            )

            distance = st.number_input(
                "Distance (miles)",
                min_value=0.0,
                format="%.2f",
            )

        with col2:
            duration_input = st.text_input(
                "Duration (HH:MM:SS)",
                placeholder="e.g. 5:43, 45:10, 1:02:15",
            )

            duration_seconds, duration_str = parse_duration_input(duration_input)

            # Auto-calc pace
            avg_pace = None
            if distance > 0 and duration_seconds and duration_seconds > 0:
                pace_seconds = duration_seconds / distance
                avg_pace = str(timedelta(seconds=int(pace_seconds)))
                st.markdown(f"**Auto Pace:** `{avg_pace} / mile`")
            else:
                st.caption("Enter a valid distance + duration to auto-calc pace.")

        st.markdown("</div>", unsafe_allow_html=True)

        # ============================================
        # HR + PERFORMANCE CARD
        # ============================================
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("❤️ Heart Rate & Performance")

        col3, col4, col5, col6 = st.columns(4)

        with col3:
            avg_hr = st.number_input(
                "Average HR",
                min_value=0,
                max_value=250,
                step=1,
            )

        with col4:
            max_hr = st.number_input(
                "Max HR",
                min_value=0,
                max_value=250,
                step=1,
            )

        with col5:
            cadence = st.number_input(
                "Cadence (spm)",
                min_value=0,
                max_value=300,
                step=1,
            )

        with col6:
            elevation = st.number_input(
                "Elevation Gain (ft)",
                min_value=0,
                step=1,
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # ============================================
        # FEELING / EFFORT CARD
        # ============================================
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🧠 Effort & How You Felt")

        col7, col8 = st.columns(2)

        with col7:
            effort = st.slider("Effort (1–10)", 1, 10, value=5)
            sleep = st.text_input("Sleep (hours)", placeholder="e.g. 7.5")
            stress = st.slider("Stress (1–5)", 1, 5, value=3)

        with col8:
            weather = st.text_input(
                "Weather",
                placeholder="Cold & dry, windy, humid…",
            )
            terrain = st.text_input(
                "Terrain",
                placeholder="Road / Trail / Track / Treadmill",
            )
            felt = st.text_area(
                "How You Felt",
                placeholder="Describe how the run felt…",
            )
            pain = st.text_input(
                "Any Pain or Tightness?",
                placeholder="Shins, calves, knees, etc.",
            )
            hydration = st.text_input(
                "Nutrition / Hydration",
                placeholder="Fasted, electrolytes, gels…",
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # ============================================
        # GARMIN & EXTRA METRICS CARD
        # ============================================
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 Garmin & Additional Metrics")

        col9, col10 = st.columns(2)

        with col9:
            vo2max = st.number_input(
                "VO2 Max",
                min_value=0.0,
                step=0.1,
            )
            training_load = st.number_input(
                "Training Load",
                min_value=0,
                step=1,
            )

        with col10:
            hrv = st.number_input(
                "HRV (7-day Avg)",
                min_value=0,
                step=1,
            )
            performance_condition = st.text_input(
                "Performance Condition",
                placeholder="+2, -3, etc.",
            )

        notes = st.text_area(
            "Additional Notes",
            placeholder="Anything else to remember…",
        )

        st.markdown("</div>", unsafe_allow_html=True)

        # ============================================
        # SUBMIT BUTTON (CENTERED)
        # ============================================
        st.markdown('<div class="card" style="text-align:center;">', unsafe_allow_html=True)
        cols = st.columns(3)
        with cols[1]:
            submitted = st.form_submit_button("💾 Save Run", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # =======================================================
        # VALIDATION BEFORE WRITING TO DB
        # =======================================================
        if submitted:
            # Duration validation
            if duration_seconds is None or duration_seconds <= 0:
                st.error("❌ Please enter a valid duration like `5:43` or `1:02:15`.")
                st.stop()

            # Distance validation
            if distance <= 0:
                st.error("❌ Distance must be greater than 0 miles.")
                st.stop()

            # HR sanity hints
            if avg_hr and avg_hr < 40:
                st.warning("⚠️ Average HR below 40 is unusual — double check?")
            if max_hr and avg_hr and max_hr < avg_hr:
                st.warning("⚠️ Max HR is lower than Avg HR — double check?")

            # Clean text fields
            felt_clean = felt.strip() if felt else ""
            pain_clean = pain.strip() if pain else ""
            terrain_clean = terrain.strip() if terrain else ""
            weather_clean = weather.strip() if weather else ""
            hydration_clean = hydration.strip() if hydration else ""
            notes_clean = notes.strip() if notes else ""

            # ================================================
            # SAVE TO DATABASE
            # ================================================
            run_data = {
                "date": str(date),
                "run_type": run_type,
                "distance": float(distance),
                "duration": duration_str,
                "avg_pace": avg_pace,
                "avg_hr": avg_hr,
                "max_hr": max_hr,
                "cadence": cadence,
                "elevation": elevation,
                "effort": effort,
                "weather": weather_clean,
                "terrain": terrain_clean,
                "felt": felt_clean,
                "pain": pain_clean,
                "sleep": sleep,
                "stress": stress,
                "hydration": hydration_clean,
                "vo2max": vo2max,
                "training_load": training_load,
                "hrv": hrv,
                "performance_condition": performance_condition,
                "notes": notes_clean,
            }

            add_run(run_data)
            st.success("✅ Run saved successfully!")


def main():
    render_log_run()


if __name__ == "__main__":
    main()
