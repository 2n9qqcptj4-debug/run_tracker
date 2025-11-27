import streamlit as st

def inject_css():
    st.markdown(
        """
        <style>

        /* GLOBAL FONT + BODY */
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif !important;
        }

        /* CLEAN PAGE WIDTH */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 950px;
            margin: auto;
        }

        /* HEADINGS */
        h1, h2, h3 {
            font-weight: 700 !important;
        }
        h1 { font-size: 2.2rem !important; }
        h2 { font-size: 1.6rem !important; }
        h3 { font-size: 1.3rem !important; }

        /* CARD STYLE */
        .card {
            padding: 1rem 1.2rem;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.03);
            margin-bottom: 1rem;
        }

        /* BUTTONS */
        .stButton>button {
            background: linear-gradient(120deg, #4a90e2, #357ABD);
            color: white;
            padding: 0.55rem 1.1rem;
            font-weight: 600;
            border-radius: 8px;
            border: none;
        }
        .stButton>button:hover {
            background: linear-gradient(120deg, #5aa2ff, #4a90e2);
        }

        /* INPUTS */
        .stTextInput>div>div>input,
        .stNumberInput>div>div>input,
        .stTextArea textarea {
            border-radius: 6px !important;
        }

        /* TABS UPGRADE */
        div[data-baseweb="tab-list"] {
            gap: 6px;
        }
        div[data-baseweb="tab"] {
            padding: 0.6rem 1rem !important;
            border-radius: 8px 8px 0 0;
            backdrop-filter: blur(8px);
        }

        /* TABLE IMPROVEMENTS */
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
