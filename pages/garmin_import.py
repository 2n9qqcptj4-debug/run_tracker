import streamlit as st
import pandas as pd
from datetime import timedelta

from utils.database import add_run


def render_garmin_import_page():
    st.title("📤 Import Garmin Data")

    uploaded = st.file_uploader("Upload Garmin CSV file", type=["csv"])

    if not uploaded:
        st.info("Upload a Garmin export CSV to begin.")
        return

    df = pd.read_csv(uploaded)

    st.write("Preview:")
    st.dataframe(df.head(), use_container_width=True)

    if st.button("Import Runs"):
        imported_count = 0

        for _, row in df.iterrows():
            try:
                # Parse Garmin fields (common names)
                duration_seconds = row.get("Duration", 0)
                distance_mi = row.get("Distance", 0) / 1609.34  # meters → miles

                duration_str = str(timedelta(seconds=int(duration_seconds)))

                run_data = {
                    "date": row.get("Date", ""),
                    "run_type": row.get("Activity Type", "Run"),
                    "distance": round(distance_mi, 2),
                    "duration": duration_str,
                    "avg_pace": row.get("Avg Pace", None),
                    "avg_hr": row.get("Avg HR", None),
                    "max_hr": row.get("Max HR", None),
                    "cadence": row.get("Avg Run Cadence", None),
                    "elevation": row.get("Elevation Gain", None),
                    "effort": 5,
                    "weather": "",
                    "terrain": "",
                    "felt": "",
                    "pain": "",
                    "sleep": "",
                    "stress": "",
                    "hydration": "",
                    "vo2max": None,
                    "training_load": None,
                    "hrv": None,
                    "performance_condition": "",
                    "notes": "",
                }

                add_run(run_data)
                imported_count += 1

            except Exception as e:
                st.warning(f"Skipped a row due to error: {e}")

        st.success(f"Imported {imported_count} runs!")


def main():
    render_garmin_import_page()


if __name__ == "__main__":
    main()