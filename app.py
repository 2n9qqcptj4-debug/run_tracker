# ======================================================
# DEBUG OPENAI IMPORT — MUST BE AT TOP OF FILE
# ======================================================
import sys
print(">>> PYTHON PATH:", sys.path)

# Import openai safely for debug
try:
    import openai
    print(">>> OPENAI MODULE:", openai)
    print(">>> OPENAI FILE:", openai.__file__)
    print(">>> OPENAI VERSION:", getattr(openai, "__version__", "NO VERSION FOUND"))
    print(">>> OPENAI ATTRIBUTES SAMPLE:", dir(openai)[:25])
except Exception as e:
    print(">>> FAILED TO IMPORT OPENAI:", e)

# ======================================================
# END DEBUG BLOCK
# ======================================================


import streamlit as st
from utils.styling import inject_css
from utils.database import init_db, fetch_runs
from utils.metrics import prepare_metrics_df
import pandas as pd
from datetime import datetime, timedelta


# ------------------------------------------------------
# MANUALLY LOAD PAGES
# ------------------------------------------------------
def load_pages():
    import pages.feed
    import pages.calendar
    import pages.log_run
    import pages.dashboard
    import pages.garmin_import
    import pages.ai_coach
    import pages.compare_runs
    import pages.pace_zones
    import pages.settings
    import pages.edit_run


# ------------------------------------------------------
# BEAUTIFUL HOME PAGE
# ------------------------------------------------------
def render_home():
    st.title("🏃‍♂️ Run Tracker")
    st.caption("Your running summary, insights, and quick actions — all in one place.")

    df = fetch_runs()

    # ================ EMPTY STATE ================
    if df.empty:
        st.markdown(
            """
            ### 👋 Welcome!
            Start your running journey.

            **Next steps:**
            - 📝 Log your first run  
            - 📥 Import Garmin history  
            - 🤖 Ask AI Coach for training guidance  

            Your dashboard will populate automatically once runs are logged.
            """
        )
        return

    metrics = prepare_metrics_df(df)

    # ================= LAST RUN CARD =================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🏃 Last Run")

    last = df.iloc[-1]

    c1, c2 = st.columns(2)

    with c1:
        st.write(f"**Date:** {last['date']}")
        st.write(f"**Type:** {last['run_type']}")
        st.write(f"**Distance:** {last['distance']} mi")

    with c2:
        st.write(f"**Duration:** {last['duration']}")
        if last.get("avg_pace"):
            st.write(f"**Pace:** {last['avg_pace']} /mi")
        if last.get("avg_hr"):
            st.write(f"**Avg HR:** {last['avg_hr']} bpm")

    st.markdown('</div>', unsafe_allow_html=True)

    # ================= WEEKLY SUMMARY =================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📅 Weekly Summary")

    week_mask = pd.to_datetime(df["date"]) >= (datetime.today() - timedelta(days=7))
    last7 = df[week_mask]

    if last7.empty:
        st.info("No runs logged in the last 7 days.")
    else:
        total_miles = last7["distance"].sum()
        runs_count = len(last7)
        avg_effort = last7["effort"].mean() if "effort" in last7 else None

        c1, c2, c3 = st.columns(3)
        c1.metric("Mileage (7 days)", f"{total_miles:.1f} mi")
        c2.metric("Runs Logged", runs_count)
        if avg_effort:
            c3.metric("Avg Effort", f"{avg_effort:.1f}/10")

    st.markdown('</div>', unsafe_allow_html=True)

    # ================= QUICK ACTIONS =================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("⚡ Quick Actions")

    q1, q2, q3 = st.columns(3)

    with q1:
        if st.button("📝 Log a Run"):
            st.switch_page("pages/log_run.py")

    with q2:
        if st.button("🤖 AI Coach"):
            st.switch_page("pages/ai_coach.py")

    with q3:
        if st.button("📆 Calendar"):
            st.switch_page("pages/calendar.py")

    st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------------------------------
# MAIN ENTRY POINT
# ------------------------------------------------------
def main():
    st.set_page_config(page_title="Run Tracker", layout="wide")
    inject_css()
    init_db()
    load_pages()

    # Always land on the Home page
    render_home()


if __name__ == "__main__":
    main()
