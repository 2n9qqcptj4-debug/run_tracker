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

    st.title("Run Tracker")
    st.write("Select a page from the sidebar.")

if __name__ == "__main__":
    main()
