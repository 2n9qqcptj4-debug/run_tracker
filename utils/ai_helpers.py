import streamlit as st
import traceback
import openai   # <-- use module, NOT OpenAI()

# =========================================================
# CONFIGURE OPENAI (OLD-STABLE STYLE)
# =========================================================
def configure_openai():
    debug = []

    if "OPENAI_API_KEY" not in st.secrets:
        debug.append("❌ OPENAI_API_KEY missing from secrets.")
        st.session_state["debug_info"] = "\n".join(debug)
        return False

    try:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        debug.append("✅ OpenAI API key loaded.")
        st.session_state["debug_info"] = "\n".join(debug)
        return True

    except Exception as e:
        debug.append(f"❌ Failed to configure OpenAI: {e}")
        st.session_state["debug_info"] = "\n".join(debug)
        return False


# =========================================================
# CALL OPENAI SAFELY USING OLD API
# =========================================================
def call_ai(prompt: str):
    """
    Uses the old OpenAI global-call syntax.
    This completely bypasses the Client() constructor,
    so Streamlit's unwanted 'proxies' argument cannot break it.
    """

    if not configure_openai():
        return "❌ OpenAI not configured. Check your secrets."

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful running coach."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

    except Exception as e:
        st.session_state["debug_info"] = f"❌ OpenAI error:\n{traceback.format_exc()}"
        return f"❌ Error contacting OpenAI:\n{e}"


# =========================================================
# DEBUG INFO
# =========================================================
def get_debug_info():
    return st.session_state.get("debug_info", "No debug info yet.")
