import streamlit as st
import auth_manager as auth

st.title("Reset Password")

params = st.query_params

if "type" in params and params["type"] == "recovery":
    new_pass = st.text_input("Enter New Password", type="password")
    confirm_pass = st.text_input("Confirm New Password", type="password")

    if st.button("Update Password"):
        if new_pass != confirm_pass:
            st.error("Passwords do not match.")
        else:
            try:
                auth.supabase.auth.update_user({"password": new_pass})
                st.success("Password updated! You can now log in.")
                #st.query_params.clear()
                login_link = st.page_link("pages/00_login.py", label="Go to Login", icon="🔑")
            except Exception as e:
                st.error(str(e))