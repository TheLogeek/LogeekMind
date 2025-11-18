import streamlit as st
from google import genai
from google.genai.errors import APIError

def get_gemini_client():
    gemini_api_key = None

    if "api_key" in st.session_state and st.session_state.api_key:
        gemini_api_key = st.session_state.api_key
    #elif "GEMINI_API_KEY" in st.secrets :
        #gemini_api_key = st.secrets["GEMINI_API_KEY"]

    if not gemini_api_key:
        with st.sidebar:
            st.warning("Please enter your Gemini API key to use the AI features.")

            user_key = st.text_input("Gemini API key", type="password")

            if user_key:
                st.session_state.api_key = user_key
                st.rerun()

        st.header("🔒 AI Features Locked")
        st.info("Please check the sidebar and enter your Gemini API Key to unlock LogeekMind's AI features.")
        st.markdown("If you don't already have a Gemini API Key, [**View the complete LogeekMind API Key Setup Guide here!**](https://github.com/TheLogeek/LogeekMind#getting-started)")
        st.stop()

    try:
        @st.cache_resource
        def initialize_client():
            return genai.Client(api_key=gemini_api_key)

        return initialize_client()
    except APIError as e:
        st.error(f"API Key Error: Failed to initialize client. Please check your key. Details: {e}")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred during client initialization: {e}")
        st.stop()