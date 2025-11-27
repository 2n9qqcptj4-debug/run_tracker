import streamlit as st

def inject_css():
    st.markdown("""
    <style>

    /* --------- GLOBAL FONT + SMOOTHING ---------- */
    * {
        font-family: 'Inter', sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    /* --------- CARD STYLE ---------- */
    .card {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 20px;
        backdrop-filter: blur(6px);
    }

    /* --------- SECTION HEADERS ---------- */
    .section-header {
        background: linear-gradient(90deg, #4a90e2, #2d73b8);
        padding: 8px 14px;
        color: white !important;
        font-weight: 600;
        border-radius: 8px;
        margin-bottom: 12px;
        margin-top: 25px;
    }

    /* ------------ PREMIUM DESIGNER TABS -------------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px !important;
        padding: 12px 0 !important;
        justify-content: center !important;
        border-bottom: 1px solid rgba(255,255,255,0.08) !important;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 24px !important;
        border-radius: 12px !important;
        background: rgba(255,255,255,0.05) !important;
        font-weight: 600 !important;
        transition: all 0.25s ease-in-out !important;
        backdrop-filter: blur(6px) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255,255,255,0.15) !important;
        transform: translateY(-2px) !important;
        cursor: pointer !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #4a90e2, #2d73b8) !important;
        color: white !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.25) !important;
        border: none !important;
        transform: translateY(0px) !important;
    }

    /* --------- TAB CONTENT FADE-IN ---------- */
    .tab-content {
        animation: fadeIn 0.4s ease-in-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }

    </style>
    """, unsafe_allow_html=True)
