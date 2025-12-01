import streamlit as st
from utils.styling import inject_css
from utils.database import init_db, fetch_runs
from utils.metrics import prepare_metrics_df
from datetime import datetime, timedelta
import pandas as pd


# -------------------------------------------------------------------
# PAGE ICONS — SOLID STYLE (Bootstrap Icons)
# -------------------------------------------------------------------
PAGE_ICONS = {
    "Home": "🏠",
    "Feed": "📰",
    "Calendar": "📆",
    "Log a Run": "📝",
    "Dashboard": "📊",
    "Garmin Import": "📥",
    "AI Coach": "🤖",
    "Compare Runs": "📈",
    "Pace Zones": "⏱️",
    "Settings": "⚙️",
}


# -------------------------------------------------------------------
# Load Pages
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# HOME PAGE (GORGEOUS)
# -------------------------------------------------------------------
def render_home():
    st.title("🏠 Home")
    st.caption("Your key running metrics at a glance — powered by your data.")

    df = fetch_runs()

    # ================ Empty State ================
    if df.empty:
        st.markdown(
            """
            ### 👋 Welcome!
            Start your training journey.

            **Next actions:**
            - 📝 Log your first run  
            - 📥 Import Garmin history  
            - 🤖 Use AI Coach  

            Your dashboard will automatically populate as you add data.
            """
        )
        return

    metrics = prepare_metrics_df(df)

    # ================= Last Run =================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🏃 Last Run")

    last = df.iloc[-1]

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Date:** {last['date']}")
        st.write(f"**Type:** {last['run_type']}")
        st.write(f"**Distance:** {last['distance']} mi")

    with col2:
        st.write(f"**Duration:** {last['duration']}")
        if last.get("avg_pace"):
            st.write(f"**Pace:** {last['avg_pace']} /mi")
        if last.get("avg_hr"):
            st.write(f"**Avg HR:** {last['avg_hr']} bpm")

    st.markdown('</div>', unsafe_allow_html=True)

    # ================= Weekly Summary =================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📅 Weekly Summary")

    week_mask = pd.to_datetime(df["date"]) >= (datetime.today() - timedelta(days=7))
    last7 = df[week_mask]

    if last7.empty:
        st.info("No runs logged in the last week.")
    else:
        total_miles = last7["distance"].sum()
        runs_count = len(last7)
        avg_effort = last7["effort"].mean() if "effort" in last7 else None

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Mileage (7 days)", f"{total_miles:.1f} mi")
        with c2:
            st.metric("Runs Logged", runs_count)
        with c3:
            if avg_effort:
                st.metric("Avg Effort", f"{avg_effort:.1f}/10")

    st.markdown('</div>', unsafe_allow_html=True)

    # ================= Quick Actions =================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("⚡ Quick Actions")

    a1, a2, a3 = st.columns(3)

    with a1:
        if st.button("📝 Log a Run"):
            st.switch_page("pages/log_run.py")

    with a2:
        if st.button("🤖 AI Coach"):
            st.switch_page("pages/ai_coach.py")

    with a3:
        if st.button("📆 Calendar"):
            st.switch_page("pages/calendar.py")

    st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------------------------------------------
# MAIN APP
# -------------------------------------------------------------------
def main():
    st.set_page_config(page_title="Run Tracker", layout="wide")
    inject_css()
    init_db()
    load_pages()

    # ---------------- Sidebar Navigation ----------------
    st.sidebar.markdown("## 📚 Navigation")

    page_names = list(PAGE_ICONS.keys())

    selected = st.sidebar.radio(
        "",
        page_names,
        format_func=lambda name: f"{PAGE_ICONS.get(name, '')}  {name}",
    )

    # ---------------- Page Routing ----------------
    if selected == "Home":
        render_home()

    elif selected == "Feed":
        st.switch_page("pages/feed.py")

    elif selected == "Calendar":
        st.switch_page("pages/calendar.py")

    elif selected == "Log a Run":
        st.switch_page("pages/log_run.py")

    elif selected == "Dashboard":
        st.switch_page("pages/dashboard.py")

    elif selected == "Garmin Import":
        st.switch_page("pages/garmin_import.py")

    elif selected == "AI Coach":
        st.switch_page("pages/ai_coach.py")

    elif selected == "Compare Runs":
        st.switch_page("pages/compare_runs.py")

    elif selected == "Pace Zones":
        st.switch_page("pages/pace_zones.py")

    elif selected == "Settings":
        st.switch_page("pages/settings.py")


if __name__ == "__main__":
    main()
