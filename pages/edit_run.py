import streamlit as st
from utils.styling import inject_css
inject_css()
import pandas as pd
from utils.database import fetch_runs, update_run, delete_run
from datetime import datetime, timedelta


# ---------------------------------------------------------
# Utility — parse "0 days 00:30:00"
# ---------------------------------------------------------
def parse_duration_to_seconds(duration_str):
    """
    Accepts either:
    - "0 days 00:30:00"
    - "00:30:00"
    - "HH:MM:SS"
    Returns seconds (int)
    """
    try:
        if "days" in duration_str:
            days, time = duration_str.split(" days ")
            days = int(days)
        else:
            days = 0
            time = duration_str

        h, m, s = time.split(":")
        return days * 86400 + int(h) * 3600 + int(m) * 60 + int(s)
    except:
        return None


# ---------------------------------------------------------
# Edit Run Page
# ---------------------------------------------------------
def render_edit_run_page():
    st.title("✏️ Edit Run")
    st.caption("Modify your saved run or delete it permanently.")

    df = fetch_runs()

    if df.empty:
        st.error("No runs available to edit.")
        return

    df = df.sort_values(by="date", ascending=False).reset_index(drop=True)

    # ----------------------------
    # Dropdown to select run
    # ----------------------------
    run_labels = [
        f"{row['id']} — {row['date']} · {row['run_type']} · {row['distance']} mi"
        for _, row in df.iterrows()
    ]

    selected_label = st.selectbox("Select a run to edit:", run_labels)

    selected_id = int(selected_label.split("—")[0].strip())
    selected_row = df[df["id"] == selected_id].iloc[0]

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.subheader("Run Details")

    # ----------------------------
    # Editable fields
    # ----------------------------
    new_date = st.date_input("Date", datetime.fromisoformat(selected_row["date"]))

    new_type = st.selectbox(
        "Run Type",
        ["Easy", "Tempo", "Interval", "Long", "Race", "Recovery"],
        index=["Easy", "Tempo", "Interval", "Long", "Race", "Recovery"].index(selected_row["run_type"])
    )

    new_distance = st.number_input("Distance (mi)", value=float(selected_row["distance"]), min_value=0.0, step=0.1)

    # Duration (accepts HH:MM:SS)
    duration_str = selected_row["duration"]
    if "days" in duration_str:
        _, t = duration_str.split(" days ")
    else:
        t = duration_str

    new_duration_str = st.text_input("Duration (HH:MM:SS)", value=t)

    # Pace
    new_pace = st.text_input("Avg Pace (MM:SS)", value=selected_row.get("avg_pace", ""))

    # HR
    new_hr = st.number_input("Avg HR (bpm)", value=int(selected_row.get("avg_hr", 0)), min_value=0, step=1)

    # Effort
    new_effort = st.slider("Effort (1–10)", 1, 10, int(selected_row.get("effort", 5)))

    # Notes
    new_notes = st.text_area("Notes", value=selected_row.get("notes", ""))


    # ----------------------------
    # Save button
    # ----------------------------
    if st.button("💾 Save Changes", type="primary"):
        try:
            seconds = parse_duration_to_seconds(new_duration_str)
            if seconds is None:
                st.error("Invalid duration format. Use HH:MM:SS.")
                return

            update_run(
                selected_id,
                {
                    "date": str(new_date),
                    "run_type": new_type,
                    "distance": new_distance,
                    "duration": f"0 days {new_duration_str}",
                    "avg_pace": new_pace,
                    "avg_hr": new_hr,
                    "effort": new_effort,
                    "notes": new_notes,
                },
            )

            st.success("Run updated successfully!")
            st.rerun()

        except Exception as e:
            st.error(f"Failed to update run: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    # ----------------------------
    # Delete Run
    # ----------------------------
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🗑 Delete This Run")

    if st.button("❌ Delete Run", type="secondary"):
        delete_run(selected_id)
        st.success("Run deleted.")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def main():
    render_edit_run_page()


if __name__ == "__main__":
    main()
