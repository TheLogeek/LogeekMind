import streamlit as st
from supabase import create_client

# Initialize Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]  # anon/public key
    return create_client(url, key)

supabase = init_supabase()

st.title("Reset Your Password")
st.write("Enter your new password below.")

new_password = st.text_input("New Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")

if st.button("Update Password"):
    if new_password != confirm_password:
        st.error("Passwords do not match.")
    else:
        try:
            supabase.auth.update_user({"password": new_password})
            st.success("Password updated successfully! You can now log in.")
            st.page_link("pages/00_login.py", label="Go to Login")
        except Exception as e:
            st.error(f"Failed to update password: {e}")
