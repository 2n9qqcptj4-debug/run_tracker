import streamlit as st
from utils.database import add_run
from datetime import datetime


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def parse_time_to_seconds(time_str):
    """Parses MM:SS or HH:MM:SS into seconds."""
    try:
        parts = time_str.split(":")
        if len(parts) == 2:   # MM:SS
            m, s = parts
            return int(m) * 60 + int(s)
        elif len(parts) == 3:  # HH:MM:SS
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + int(s)
        return None
    except:
        return None


def format_pace(seconds):
    """Formats seconds -> M:SS pace string."""
    if seconds <= 0:
        return None
    m = seconds // 60
    s = seconds % 60
    return f"{m}:{s:02d}"


# ---------------------------------------------------------
# PAGE
# ---------------------------------------------------------
def render_log_run_page():
    st.title("📝 Log a Run")
    st.caption("Record your training with detailed metrics to improve insights & AI coaching.")

    # ======================================================
    # CARD — BASIC RUN DETAILS
    # ======================================================
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🏃 Run Details")

    date = st.date_input("Date", datetime.today())

    run_type = st.selectbox(
        "Run Type",
        ["Easy", "Tempo", "Interval", "Long", "Race", "Recovery"],
    )

    distance = st.number_input(
        "Distance (miles)", min_value=0.0, step=0.01, format="%.2f"
    )

    duration_input = st.text_input(
        "Duration (HH:MM:SS or MM:SS)", placeholder="00:45:00"
    )

    pace_input = st.text_input(
        "Avg Pace (MM:SS) — Optional",
        placeholder="08:30"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # CARD — HEART & BODY METRICS
    # ======================================================
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("❤️ Heart & Body Metrics")

    col1, col2, col3 = st.columns(3)

    with col1:
        avg_hr = st.number_input("Avg HR", min_value=0, max_value=250, step=1)

    with col2:
        max_hr = st.number_input("Max HR", min_value=0, max_value=250, step=1)

    with col3:
        hrv = st.number_input("HRV", min_value=0, max_value=200, step=1)

    effort = st.slider("Effort (1–10)", 1, 10, 5)

    st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # CARD — RUNNING PERFORMANCE
    # ======================================================
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📈 Performance Metrics")

    colA, colB, colC = st.columns(3)

    with colA:
        cadence = st.number_input("Cadence (spm)", min_value=0, max_value=250, step=1)

    with colB:
        elevation = st.number_input("Elevation Gain (ft)", min_value=0, step=1)

    with colC:
        training_load = st.number_input("Training Load (optional)", min_value=0, step=1)

    vo2max = st.number_input("VO2 Max (optional)", min_value=0.0, step=0.1)

    performance_condition = st.text_input("Performance Condition (optional)")

    st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # CARD — CONDITIONS
    # ======================================================
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🌦 Conditions")

    colX, colY = st.columns(2)

    with colX:
        terrain = st.text_input("Terrain (Road, Treadmill, Trail, etc.)")

    with colY:
        weather = st.text_input("Weather (65°F, windy, etc.)")

    st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # CARD — WELLNESS / RECOVERY
    # ======================================================
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("😴 Wellness & Recovery")

    colS1, colS2 = st.columns(2)

    with colS1:
        sleep = st.text_input("Sleep (hours)", placeholder="7.5")

    with colS2:
        stress = st.text_input("Stress (1–5)")

    hydration = st.text_area("Hydration Notes (optional)")

    st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # CARD — FEELINGS & NOTES
    # ======================================================
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🧠 How You Felt")

    felt = st.text_input("How you felt (optional)")
    pain = st.text_input("Any pain? (optional)")
    notes = st.text_area("Notes (optional)")

    st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # SAVE BUTTON
    # ======================================================
    if st.button("💾 Save Run", type="primary"):

        # ---- Duration Validation ----
        duration_seconds = parse_time_to_seconds(duration_input)
        if duration_seconds is None:
            st.error("❌ Invalid duration. Use HH:MM:SS or MM:SS.")
            return

        # ---- Pace Validation ----
        if pace_input.strip():
            pace_seconds = parse_time_to_seconds(pace_input)
            if pace_seconds is None:
                st.error("❌ Avg Pace must be MM:SS.")
                return
            avg_pace = pace_input.strip()
        else:
            if distance > 0:
                pace_seconds = duration_seconds / distance
                avg_pace = format_pace(int(pace_seconds))
            else:
                avg_pace = None

        # ---- Format duration string ----
        if len(duration_input.split(":")) == 3:
            duration_str = f"0 days {duration_input}"
        else:
            duration_str = f"0 days 00:{duration_input}"

        # -------------------------------------------------
        # BUILD DATA DICT EXACTLY MATCHING YOUR TABLE
        # -------------------------------------------------
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

        # Save the full dict
        add_run(run_data)

        st.success("✅ Run saved successfully!")
        st.rerun()


def main():
    render_log_run_page()


if __name__ == "__main__":
    main()
