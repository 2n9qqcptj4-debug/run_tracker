import streamlit as st
from utils.styling import inject_css
from utils.database import init_db


def load_pages():
    import pages.home
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


def main():
    st.set_page_config(page_title="Run Tracker", layout="wide")

    inject_css()
    init_db()
    load_pages()

    # Automatically redirect to Home page
    st.switch_page("pages/home.py")


if __name__ == "__main__":
    main()
