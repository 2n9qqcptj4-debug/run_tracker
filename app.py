import streamlit as st
from utils.styling import inject_css
from utils.database import init_db, fetch_runs
from utils.metrics import prepare_metrics_df
import pandas as pd
from datetime import datetime, timedelta


# ------------------------------------------------------
# Load Pages (ONLY needed if you manually control nav)
# ------------------------------------------------------
def load_pages():
    # These imports register the pages so Streamlit knows they exist
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
# Home Page
# ------------------------------------------------------
def render_home():
    st.title("🏃‍♂️ Run Tracker")
    st.caption("Your running summary, insights, and quick actions — all in one place.")

    df = fetch_runs()

    # ---------------- Empty State ----------------
    if df.empty:
        st.markdown(
            """
            ### 👋 Welcome!
            Let's get your training journey started.

            **Next steps:**
            - 📝 Log your first run  
            - 📥 Import Garmin history  
            - 🤖 Try the AI Coach  

            This homepage will automatically update with your stats.
            """
        )
        return

    metrics = prepare_metrics_df(df)

    # ---------------- Last Run Card ----------------
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

    # ---------------- Weekly Summary ----------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📅 Weekly Summary")

    week_mask = pd.to_datetime(df["date"]) >= (datetime.today() - timedelta(days=7))
    last7 = df[week_mask]

    if last7.empty:
        st.info("No runs logged in the last week.")
    else:
        miles = last7["distance"].sum()
        count = len(last7)
        avg_effort = last7["effort"].mean() if "effort" in last7 else None

        c1, c2, c3 = st.columns(3)
        c1.metric("Mileage (7 days)", f"{miles:.1f} mi")
        c2.metric("Runs Logged", count)
        if avg_effort:
            c3.metric("Avg Effort", f"{avg_effort:.1f}/10")

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- Quick Actions ----------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("⚡ Quick Actions")

    a1, a2, a3 = st.columns(3)

    # These only work if we add custom nav later
    with a1:
        if st.button("📝 Log a Run"):
            st.session_state["page"] = "Log Run"

    with a2:
        if st.button("🤖 AI Coach"):
            st.session_state["page"] = "AI Coach"

    with a3:
        if st.button("📆 Calendar"):
            st.session_state["page"] = "Calendar"

    st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------------------------------
# Main App
# ------------------------------------------------------
def main():
    st.set_page_config(page_title="Run Tracker", layout="wide")
    inject_css()
    init_db()
    load_pages()  # Keep this for multipage stability

    # ---------------- HOME AUTOMATICALLY RENDERS ----------------
    render_home()


if __name__ == "__main__":
    main()
