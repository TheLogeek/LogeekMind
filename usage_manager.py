import streamlit as st

def premium_gate(feature_name):

    if 'user' in st.session_state:
        return True

    st.warning(f"🔒 You must be logged in to **{feature_name}**.")
    st.info("Creating an account is free and saves your progress!")
    if st.button(f"Login to {feature_name}"):
        st.switch_page("pages/00_login.py")
    return False