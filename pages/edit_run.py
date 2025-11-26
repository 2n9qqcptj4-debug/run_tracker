import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils.database import fetch_runs, update_run, delete_run


def render_edit_run_page(run_id: int):
    st.title("✏️ Edit Run")

    df = fetch_runs()
    run = df[df["id"] == run_id]

    if run.empty:
        st.error("Run not found.")
        return

    run = run.iloc[0]

    with st.form("edit_run_form"):
        st.subheader("Run Details")

        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", value=datetime.fromisoformat(run["date"]))
            run_type = st.selectbox(
                "Run Type",
                [
                    "Easy", "Long Run", "Tempo", "Threshold", "Interval",
                    "Recovery", "Progression", "Race", "Hill Repeats",
                    "Fartlek", "Walk", "Other",
                ],
                index=[
                    "Easy", "Long Run", "Tempo", "Threshold", "Interval",
                    "Recovery", "Progression", "Race", "Hill Repeats",
                    "Fartlek", "Walk", "Other",
                ].index(run["run_type"]),
            )
            distance = st.number_input(
                "Distance (miles)", min_value=0.0, step=0.01, value=float(run["distance"])
            )
        with col2:
            # Parse duration HH:MM:SS
            try:
                h, m, s = map(int, run["duration"].split(":"))
            except:
                h, m, s = 0, 0, 0

            hours = st.number_input("Hours", min_value=0, value=h)
            minutes = st.number_input("Minutes", min_value=0, value=m)
            seconds = st.number_input("Seconds", min_value=0, value=s)

        duration_seconds = hours * 3600 + minutes * 60 + seconds
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        avg_pace = None
        if distance > 0 and duration_seconds > 0:
            pace_seconds = duration_seconds / distance
            avg_pace = str(timedelta(seconds=int(pace_seconds)))

        st.write(f"Auto Pace: `{avg_pace}`" if avg_pace else "Pace will calculate automatically")

        st.subheader("Heart Rate & Performance")

        col3, col4, col5 = st.columns(3)
        with col3:
            avg_hr = st.number_input("Average HR", min_value=0, value=int(run["avg_hr"] or 0))
        with col4:
            max_hr = st.number_input("Max HR", min_value=0, value=int(run["max_hr"] or 0))
        with col5:
            cadence = st.number_input("Cadence (spm)", min_value=0, value=int(run["cadence"] or 0))

        elevation = st.number_input(
            "Elevation Gain (ft)", min_value=0, value=int(run["elevation"] or 0)
        )

        st.subheader("Effort & Feel")

        col6, col7 = st.columns(2)
        with col6:
            effort = st.slider("Effort (1–10)", 1, 10, value=int(run["effort"] or 5))
            sleep = st.text_input("Sleep (hours)", value=run["sleep"] or "")
            stress = st.slider("Stress Level (1–5)", 1, 5, value=int(run["stress"] or 3))

        with col7:
            weather = st.text_input("Weather", value=run["weather"] or "")
            terrain = st.text_input("Terrain", value=run["terrain"] or "")
            felt = st.text_area("How You Felt", value=run["felt"] or "")

        pain = st.text_input("Any Pain or Tightness?", value=run["pain"] or "")
        hydration = st.text_input("Nutrition/Hydration Notes", value=run["hydration"] or "")

        st.subheader("Garmin Metrics")
        col8, col9 = st.columns(2)
        with col8:
            vo2max = st.number_input("VO2 Max", min_value=0.0, step=0.1, value=float(run["vo2max"] or 0))
            training_load = st.number_input("Training Load", min_value=0, value=int(run["training_load"] or 0))
        with col9:
            hrv = st.number_input("HRV (7d Avg)", min_value=0, value=int(run["hrv"] or 0))
            performance_condition = st.text_input(
                "Performance Condition",
                value=run["performance_condition"] or "",
            )

        notes = st.text_area("Additional Notes", value=run["notes"] or "")

        submitted = st.form_submit_button("Save Changes")

        if submitted:
            updated_data = {
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

            update_run(run_id, updated_data)
            st.success("Run updated successfully!")

        if st.button("Delete Run", type="primary"):
            delete_run(run_id)
            st.error("Run deleted.")
            st.stop()


def main():
    rid = st.session_state.get("edit_run_id")
    if rid is None:
        st.error("No run selected to edit.")
    else:
        render_edit_run_page(int(rid))


if __name__ == "__main__":
    main()