import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils.database import add_run  # uses your existing DB helper


def render_log_run():
    st.title("📝 Log a Run")
    st.caption("Capture how you trained, how you felt, and what your body is telling you.")

    with st.form("log_run_form", clear_on_submit=True):

        # -----------------------------
        # RUN DETAILS CARD
        # -----------------------------
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Run Details")

        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", value=datetime.today())
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
            distance = st.number_input("Distance (miles)", min_value=0.0, step=0.01)
        with col2:
            st.markdown("**Duration**")
            hc1, hc2, hc3 = st.columns(3)
            with hc1:
                hours = st.number_input("Hours", min_value=0, step=1, value=0)
            with hc2:
                minutes = st.number_input("Minutes", min_value=0, step=1, value=0)
            with hc3:
                seconds = st.number_input("Seconds", min_value=0, step=1, value=0)

        duration_seconds = hours * 3600 + minutes * 60 + seconds
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        avg_pace = None
        if distance > 0 and duration_seconds > 0:
            pace_seconds = duration_seconds / distance
            avg_pace = str(timedelta(seconds=int(pace_seconds)))

        if avg_pace:
            st.markdown(f"**Auto Pace:** `{avg_pace} per mile`")
        else:
            st.markdown(
                "<span style='opacity:0.7;'>Enter distance and duration to auto-calc pace.</span>",
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)  # end card

        # -----------------------------
        # HR & PERFORMANCE CARD
        # -----------------------------
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Heart Rate & Performance")

        col3, col4, col5, col6 = st.columns(4)
        with col3:
            avg_hr = st.number_input("Average HR", min_value=0, step=1)
        with col4:
            max_hr = st.number_input("Max HR", min_value=0, step=1)
        with col5:
            cadence = st.number_input("Cadence (spm)", min_value=0, step=1)
        with col6:
            elevation = st.number_input("Elevation Gain (ft)", min_value=0, step=1)

        st.markdown("</div>", unsafe_allow_html=True)

        # -----------------------------
        # EFFORT & FEEL CARD
        # -----------------------------
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Effort & How You Felt")

        col6, col7 = st.columns(2)
        with col6:
            effort = st.slider("Effort (1–10)", min_value=1, max_value=10, value=5)
            sleep = st.text_input("Sleep (hours)", placeholder="e.g., 7:30")
            stress = st.slider("Stress Level (1–5)", min_value=1, max_value=5, value=3)
        with col7:
            weather = st.text_input("Weather", placeholder="e.g., Cold & dry, windy, humid")
            terrain = st.text_input("Terrain", placeholder="Road / Trail / Treadmill")
            felt = st.text_area("How You Felt", placeholder="Describe how the run felt today...")

        pain = st.text_input(
            "Any Pain or Tightness?",
            placeholder="Shins, knees, calves, Achilles, etc.",
        )

        hydration = st.text_input(
            "Nutrition / Hydration Notes",
            placeholder="Fasted, electrolytes, gels, water only...",
        )

        st.markdown("</div>", unsafe_allow_html=True)

        # -----------------------------
        # GARMIN / METRICS CARD
        # -----------------------------
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Garmin & Metrics (optional)")

        col8, col9 = st.columns(2)
        with col8:
            vo2max = st.number_input("VO2 Max", min_value=0.0, step=0.1)
            training_load = st.number_input("Training Load", min_value=0, step=1)
        with col9:
            hrv = st.number_input("HRV (7d Avg)", min_value=0, step=1)
            performance_condition = st.text_input(
                "Performance Condition", placeholder="+2, -3, etc."
            )

        notes = st.text_area("Additional Notes", placeholder="Anything else you want future-you to remember.")

        st.markdown("</div>", unsafe_allow_html=True)

        # -----------------------------
        # SUBMIT BUTTON ROW
        # -----------------------------
        submit_col = st.columns(3)[1]  # center button
        with submit_col:
            submitted = st.form_submit_button("💾 Save Run")

        if submitted:
            run_data = {
                "date": str(date),
                "run_type": run_type,
                "distance": distance,
                "duration": duration_str,
                "avg_pace": avg_pace,
                "avg_hr": avg_hr,
                "max_hr": max_hr,
                "cadence": cadence,
                "elevation": elevation,
                "effort": effort,
                "weather": weather,
                "terrain": terrain,
                "felt": felt,
                "pain": pain,
                "sleep": sleep,
                "stress": stress,
                "hydration": hydration,
                "vo2max": vo2max,
                "training_load": training_load,
                "hrv": hrv,
                "performance_condition": performance_condition,
                "notes": notes,
            }

            add_run(run_data)
            st.success("Run saved successfully ✅")


def main():
    render_log_run()


if __name__ == "__main__":
    main()
