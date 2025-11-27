import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils.database import fetch_runs
from utils.metrics import prepare_metrics_df


def render_home_page():
    st.title("🏠 Home")
    st.caption("Your running overview and quick actions.")

    df = fetch_runs()

    # If no runs yet
    if df.empty:
        st.markdown(
            """
            ### 👋 Welcome!
            Start by logging your first run or importing from Garmin.

            - ➕ Use **Log a Run**
            - 📥 Use **Garmin Import**
            """
        )
        return

    # Prepare metrics
    metrics = prepare_metrics_df(df)

    # ---------------------------------------------------
    #  LAST RUN CARD
    # ---------------------------------------------------
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

    # ---------------------------------------------------
    #  WEEKLY SUMMARY CARD
    # ---------------------------------------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📅 Weekly Summary")

    week_mask = pd.to_datetime(df["date"]) >= (datetime.today() - timedelta(days=7))
    last7 = df[week_mask]

    if last7.empty:
        st.write("No runs in the last 7 days yet.")
    else:
        total_miles = last7["distance"].sum()
        avg_effort = last7["effort"].mean() if "effort" in last7 else None

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Mileage (7 days)", f"{total_miles:.1f} mi")
        with c2:
            st.metric("Runs Logged", len(last7))
        with c3:
            if avg_effort:
                st.metric("Avg Effort", f"{avg_effort:.1f}/10")

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------
    # QUICK ACTIONS
    # ---------------------------------------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("⚡ Quick Actions")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("📝 Log a Run"):
            st.session_state["page"] = "Log a Run"
            st.switch_page("pages/log_run.py")

    with c2:
        if st.button("🤖 AI Coach"):
            st.session_state["page"] = "AI Coach"
            st.switch_page("pages/ai_coach.py")

    with c3:
        if st.button("📆 Calendar"):
            st.session_state["page"] = "Calendar"
            st.switch_page("pages/calendar.py")

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------
    # OPTIONAL FUTURE SECTION
    # ---------------------------------------------------
    # More cards can go here (PRs, charts, etc.)


def main():
    render_home_page()


if __name__ == "__main__":
    main()
