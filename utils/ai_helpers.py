import streamlit as st

# Full diagnostic imports
import sys
import pkgutil
import importlib
import traceback

# Try importing OpenAI
try:
    import openai
except Exception as e:
    st.error(f"❌ Failed to import openai: {e}")
    openai = None


def get_debug_info():
    info = []

    info.append("🔍 Python version: " + sys.version)
    
    if openai:
        info.append(f"📦 openai module file: {getattr(openai, '__file__', 'NO FILE')}")
        info.append(f"📦 openai version: {getattr(openai, '__version__', 'NO VERSION')}")

        # Show what the module actually contains
        attrs = dir(openai)
        info.append("📦 openai attributes sample: " + ", ".join(attrs[:40]))

    else:
        info.append("⚠️ openai failed to import")

    return "\n".join(info)


def get_client():
    """
    Creates OpenAI client and returns detailed diagnostic info when failing.
    """
    try:
        from openai import OpenAI  # safe import
    except Exception as e:
        return None, f"❌ Could not import OpenAI class:\n{e}\n\nTraceback:\n{traceback.format_exc()}"

    # Try to initialize the client
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        return client, None
    except Exception as e:
        return None, f"""
❌ Failed to initialize OpenAI client
Error: {e}

📘 Debug Info:
{get_debug_info()}

Traceback:
{traceback.format_exc()}
"""


def call_ai(prompt: str):
    """
    Sends prompt to OpenAI with full debug reporting.
    """
    client, err = get_client()
    if err:
        return err  # return debug info right to Streamlit

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"""
🚨 Unexpected error contacting OpenAI:
{e}

📘 Debug Info:
{get_debug_info()}

Traceback:
{traceback.format_exc()}
"""
