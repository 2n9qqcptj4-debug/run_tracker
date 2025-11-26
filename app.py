import streamlit as st
from utils.styling import inject_css
from utils.database import init_db, fetch_runs

# DEBUG: import os and print folder contents
import os
print("FILES IN WORKING DIRECTORY:", os.listdir())

if os.path.exists("utils"):
    print("FILES IN utils/:", os.listdir("utils"))
else:
    print("utils folder NOT FOUND!")

# TEMPORARY: Disable all page imports so the app can run
def load_pages():
    print("Skipping page imports temporarily for debugging...")
    # import pages.home
    # import pages.feed
    # import pages.calendar
    # import pages.log_run
    # import pages.dashboard
    # import pages.garmin_import
    # import pages.ai_coach
    # import pages.compare_runs
    # import pages.pace_zones
    # import pages.settings
    # import pages.edit_run


def main():
    st.set_page_config(page_title="Run Tracker", layout="wide")

    inject_css()
    init_db()

    # TEMPORARY: Comment this out so we don't load the broken page files
    # load_pages()

    st.title("Debug Mode Active")
    st.write(
        "If this message shows up, the app is running. "
        "Scroll down to see the deployment logs in Streamlit Cloud."
    )

    st.write("Open the Streamlit Cloud logs to see the directory listings.")


if __name__ == "__main__":
    main()