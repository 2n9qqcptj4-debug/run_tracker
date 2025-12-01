import streamlit as st
from utils.database import add_run
from datetime import datetime
import pandas as pd


# --------------------------------------------------------------------
# Helper: Convert HH:MM:SS or MM:SS to seconds
# --------------------------------------------------------------------
def parse_time_to_seconds(time_str):
    try:
        parts = time_str.split(":")
        if len(parts) == 2:  # MM:SS
            m, s = parts
            return int(m) * 60 + int(s)
        if len(parts) == 3:  # HH:MM:SS
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + int(s)
        return None
    except:
        return None


# --------------------------------------------------------------------
# Helper: Convert seconds → MM:SS
# --------------------------------------------------------------------
def format_pace(seconds):
    if seconds <= 0:
        return None
    m = seconds // 60
    s = seconds % 60
    return f"{m}:{s:02d}"


# --------------------------------------------------------------------
# MAIN PAGE
# --------------------------------------------------------------------
def render_log_run_page():
    st.title("📝 Log a Run")

    st.markdown(
        "<div class='card'>",
        unsafe_allow_html=True
    )

    # -------------------------
    # RUN INPUT FIELDS
    # -------------------------
    date = st.date_input("Date", datetime.today())

    run_type = st.selectbox(
        "Run Type",
        ["Easy", "Tempo", "Interval", "Long", "Race", "Recovery"]
    )

    distance = st.number_input(
        "Distance (mi)",
        min_value=0.0,
        step=0.1,
        format="%.2f"
    )

    # One box duration input, user enters "HH:MM:SS" or "MM:SS"
    duration_input = st.text_input(
        "Duration (HH:MM:SS or MM:SS)",
        placeholder="00:30:00"
    )

    # NEW — Manual Avg Pace entry
    pace_input = st.text_input(
        "Avg Pace (MM:SS) — Optional",
        placeholder="10:00"
    )

    avg_hr = st.number_input("Avg HR (bpm)", min_value=0, step=1)
    effort = st.slider("Effort (1–10)", 1, 10, 5)
    notes = st.text_area("Notes (optional)")

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    # -------------------------
    # SAVE BUTTON
    # -------------------------
    if st.button("💾 Save Run", type="primary"):
        # Validate duration
        duration_seconds = parse_time_to_seconds(duration_input)
        if duration_seconds is None:
            st.error("❌ Invalid duration. Use HH:MM:SS or MM:SS format.")
            return

        # Validate pace
        if pace_input.strip():
            pace_seconds = parse_time_to_seconds(pace_input)
            if pace_seconds is None:
                st.error("❌ Avg Pace format invalid. Use MM:SS.")
                return
            avg_pace = pace_input.strip()
        else:
            # Auto calculate pace if user leaves it blank
            if distance > 0:
                pace_seconds = duration_seconds / distance
                avg_pace = format_pace(int(pace_seconds))
            else:
                avg_pace = None

        # Construct duration string for DB ("0 days HH:MM:SS")
        duration_str = (
            f"0 days {duration_input}"
            if len(duration_input.split(":")) == 3
            else f"0 days 00:{duration_input}"
        )

        # Save run
        add_run(
            str(date),
            run_type,
            distance,
            duration_str,
            avg_pace,
            avg_hr,
            effort,
            notes
        )

        st.success("✅ Run logged successfully!")
        st.rerun()


def main():
    render_log_run_page()


if __name__ == "__main__":
    main()
