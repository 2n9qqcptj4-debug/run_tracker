import streamlit as st

def inject_css():
    st.markdown(
        """
<style>

:root {
    --primary: #1B74D8;       /* TrainingPeaks Blue */
    --primary-dark: #1259A8;
    --accent-green: #2ecc71;
    --accent-orange: #f39c12;
    --card-bg: rgba(255, 255, 255, 0.06);
    --border-light: rgba(255, 255, 255, 0.12);
    --text-light: #E6E6E6;
    --header-height: 64px;
}

/* --------------------------------------------------------
   GLOBAL FONT
--------------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-light);
}

/* --------------------------------------------------------
   GLOBAL LAYOUT
--------------------------------------------------------- */

.main > div {
    padding-top: calc(var(--header-height) + 25px) !important;
}


/* --------------------------------------------------------
   TOP GLOBAL HEADER (TrainingPeaks Style)
--------------------------------------------------------- */

header[data-testid="stHeader"] {
    height: var(--header-height);
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(14px);
    border-bottom: 1px solid var(--border-light);
}

/* Replace default text with our app title */
header[data-testid="stHeader"]::after {
    content: "Run Tracker";
    display: flex;
    align-items: center;
    font-size: 21px;
    font-weight: 600;
    color: white;
    padding-left: 24px;
}

/* Hide Streamlit’s built-in content */
header[data-testid="stHeader"] * {
    visibility: hidden;
}


/* --------------------------------------------------------
   SIDEBAR
--------------------------------------------------------- */

section[data-testid="stSidebar"] {
    background-color: rgba(15, 23, 42, 0.92);
    backdrop-filter: blur(10px);
    border-right: 1px solid var(--border-light);
}

section[data-testid="stSidebar"] a {
    font-size: 15px !important;
    padding: 10px 6px !important;
    border-radius: 6px;
    transition: background 0.2s ease, padding-left 0.2s;
}

/* hover */
section[data-testid="stSidebar"] a:hover {
    background: rgba(255,255,255,0.06);
    padding-left: 10px !important;
}

/* selected */
section[data-testid="stSidebar"] .css-1lcbmhc {
    background: var(--primary);
    border-radius: 6px;
    color: white !important;
}

/* Icon + label alignment */
section[data-testid="stSidebar"] .stRadio > div {
    gap: 6px !important;
}

section[data-testid="stSidebar"] .stRadio label {
    font-size: 16px !important;
    font-weight: 500 !important;
}


/* --------------------------------------------------------
   CARDS
--------------------------------------------------------- */

.card {
    background: var(--card-bg);
    padding: 22px 28px;
    border-radius: 12px;
    border: 1px solid var(--border-light);
    margin-bottom: 22px;
    box-shadow: 0px 3px 12px rgba(0,0,0,0.25);
    animation: fadeIn 0.4s ease-out;
}

.section-header {
    margin-top: 10px;
    margin-bottom: 8px;
    font-size: 22px;
    font-weight: 600;
    color: var(--primary);
}


/* --------------------------------------------------------
   EXPANDERS
--------------------------------------------------------- */

.streamlit-expanderHeader {
    font-size: 17px !important;
    font-weight: 600 !important;
}

.streamlit-expanderContent {
    background: rgba(255,255,255,0.02) !important;
    padding: 15px 12px !important;
}


/* --------------------------------------------------------
   BUTTONS (clean, bold training UI)
--------------------------------------------------------- */

.stButton>button {
    background-color: var(--primary) !important;
    color: white !important;
    padding: 10px 22px !important;
    border-radius: 8px !important;
    border: 1px solid var(--primary-dark) !important;
    font-weight: 600 !important;
    transition: 0.2s ease-in-out;
    font-size: 15px !important;
}

.stButton>button:hover {
    background-color: var(--primary-dark) !important;
    transform: translateY(-1px);
}


/* --------------------------------------------------------
   METRICS
--------------------------------------------------------- */

[data-testid="stMetricValue"] {
    color: var(--primary) !important;
    font-size: 28px !important;
}

[data-testid="stMetricLabel"] {
    color: var(--text-light) !important;
    font-weight: 500 !important;
}


/* --------------------------------------------------------
   TABS
--------------------------------------------------------- */

.stTabs [role="tab"] {
    padding: 12px 16px;
    border-radius: 6px 6px 0 0;
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border-light);
    color: var(--text-light);
    font-weight: 500;
    margin-right: 4px;
}

.stTabs [aria-selected="true"] {
    background: var(--primary) !important;
    color: white !important;
}


/* --------------------------------------------------------
   INPUTS
--------------------------------------------------------- */

input, textarea, select, .stTextInput>div>div>input {
    border-radius: 6px !important;
}


/* --------------------------------------------------------
   ANIMATIONS
--------------------------------------------------------- */

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

</style>
        """,
        unsafe_allow_html=True,
    )
