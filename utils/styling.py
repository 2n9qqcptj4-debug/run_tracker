import streamlit as st

def inject_css():
    st.markdown(
        """
        <style>

        /* GLOBAL APP BACKGROUND */
        body, .stApp {
            background-color: #0B0E14 !important;
        }

        /* SIDEBAR */
        [data-testid="stSidebar"] {
            background-color: #111827 !important;
            border-right: 1px solid #1f2937 !important;
        }

        /* SIDEBAR TEXT */
        [data-testid="stSidebar"] * {
            color: #e5e7eb !important;
            font-size: 15px !important;
        }

        /* CARD STYLE */
        .card {
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.08);
        }

        /* SECTION HEADER */
        .section-header {
            font-size: 1.3rem;
            font-weight: 600;
            margin: 20px 0 12px;
        }

        /* TAB CONTENT SPACING */
        .tab-content {
            padding-top: 15px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
