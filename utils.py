import streamlit as st
import requests, time
from google import genai
from google.genai.errors import APIError


def is_gemini_key_valid(api_key: str) -> bool:
    if not api_key:
        return False

    try:
        client = genai.Client(api_key=api_key)
        _ = client.models.get(model="gemini-2.5-flash")

        return True

    except APIError as e:
        st.error("Invalid API Key! Please check your key and try again") if "400" in str(e) else st.error(f"Validation error: {e}")
        return False
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return False

def check_rate_limit():

    MAX_REQUESTS = 5
    TIME_WINDOW = 30
    SESSION_HISTORY_KEY = 'gemini_request_history'

    if SESSION_HISTORY_KEY not in st.session_state:
        st.session_state[SESSION_HISTORY_KEY] = []

    current_time = time.time()
    history = st.session_state[SESSION_HISTORY_KEY]

    history = [t for t in history if t > current_time - TIME_WINDOW]

    if len(history) >= MAX_REQUESTS:
        time_to_wait = int(TIME_WINDOW - (current_time - history[0]))

        st.error(f"**Rate Limit Hit!** Please wait {time_to_wait} seconds before making using any AI feature, "
                 f"or enter your own API key for unlimited access.")
        st.session_state[SESSION_HISTORY_KEY] = history
        return False

    history.append(current_time)
    st.session_state[SESSION_HISTORY_KEY] = history
    return True

def get_gemini_client():
    gemini_api_key = None

    if "api_key" in st.session_state and st.session_state.api_key:
        gemini_api_key = st.session_state.api_key
    elif "GEMINI_API_KEY" in st.secrets :
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
        st.sidebar.warning("You are using LogeekMind's shared API Key. This key has usage limits, which might affect "
                           "performance or restrict access if exceeded."
                           "For uninterrupted, limit-free service, consider using your own API Key.")

    if not st.session_state.get('api_key'):
        with st.sidebar:

            user_key = st.text_input("Gemini API key", type="password")

            st.markdown(
                "If you don't know how to get a Gemini API Key, "
                "[**View the complete LogeekMind API Key Setup Guide here!**](https://github.com/TheLogeek/LogeekMind#getting-started)")

            if user_key:
                if is_gemini_key_valid(user_key):
                    st.session_state.api_key = user_key
                    st.success("API Key accepted and validated!")
                    time.sleep(1)
                    st.rerun()
                else:
                    #st.error("Invalid API Key!. Please check your key and try again.")
                    pass

            elif not user_key and not check_rate_limit():
                return None


    try:
        @st.cache_resource
        def initialize_client():
            return genai.Client(api_key=gemini_api_key)

        return initialize_client()
    except APIError as e:
        error_text = str(e)
        if "rate limit" in error_text.lower():
            st.error("Rate limit hit! Please wait a moment or enter your own key if you haven't already.")
        else:
            st.error(f"API Key Error: Failed to initialize client. Please check your key. Details: {e}")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred during client initialization: {e}")
        st.stop()
