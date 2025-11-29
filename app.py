# =============================================================================
# 🔍 OPENAI DEBUG BLOCK — MUST RUN FIRST
# =============================================================================
import sys

print("\n================ OPENAI DEBUG ================")
print("PYTHON PATH:", sys.path)

try:
    import openai
    print("OPENAI MODULE:", openai)
    print("OPENAI FILE:", openai.__file__)
    print("OPENAI VERSION:", getattr(openai, "__version__", "NO VERSION FOUND"))
    print("OPENAI DIR SAMPLE:", dir(openai)[:20])
except Exception as e:
    print("❌ FAILED TO IMPORT OPENAI:", str(e))

print("==============================================\n")


# =============================================================================
# NORMAL IMPORTS BELOW
# =============================================================================
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# These imports MUST come AFTER debug
try:
    from utils.styling import inject_css
    from utils.database import init_db, fetch_runs
    from utils.metrics import prepare_metrics_df
except Exception as e:
    print("❌ ERROR IMPORTING UTILS:", e)


# =============================================================================
# SAFE PAGE LOADER (won’t crash app.py)
# =============================================================================
def load_pages():
    try:
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
    except Exception as e:
        print("❌ Page load error:", e)


# =============================================================================
# HOME PAGE
# =============================================================================
def render_home():
    st.title("🏃‍♂️ Run Tracker")
    st.caption("Your running summary, insights, and quick actions — all in one place.")

    try:
        df = fetch_runs()
    except Exception as e:
        st.error(f"Database error: {e}")
        return

    if df.empty:
        st.markdown(
            """
            ### 👋 Welcome!
            No runs logged yet.

            **Next steps:**
            - 📝 Log a run  
            - 📥 Import Garmin  
            - 🤖 Ask AI Coach  
            """
        )
        return

    metrics = prepare_metrics_df(df)

    # Last run card
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

    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# MAIN
# =============================================================================
def main():
    st.set_page_config(page_title="Run Tracker", layout="wide")

    try:
        inject_css()
    except Exception as e:
        st.write("⚠ CSS load error:", e)

    try:
        init_db()
    except Exception as e:
        st.write("⚠ DB init error:", e)

    load_pages()
    render_home()


if __name__ == "__main__":
    main()
