import streamlit as st

def premium_gate(feature_name):

    if 'user' in st.session_state:
        return True

    st.warning(f"🔒 You must be logged in to **{feature_name}**.")
    st.info("Creating an account is free and saves your progress!"
            "Simply open the sidebar and click the login section")
    return False