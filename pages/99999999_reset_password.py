import streamlit as st
from supabase import create_client

# --- Initialize Supabase ---
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

st.title("🔐 Reset Your Password")

# --- Get token from URL query param ---
query = st.query_params
token_list = query.get("token", None)
token = token_list[0] if token_list else None

if not token:
    st.error("Invalid or missing reset token. Please use the link from your email.")
    st.stop()

st.write("Enter your new password below.")

new_password = st.text_input("New Password", type="password")
confirm_password = st.text_input("Confirm New Password", type="password")

if st.button("Update Password"):
    if not new_password or not confirm_password:
        st.error("Please fill both password fields.")
    elif new_password != confirm_password:
        st.error("Passwords do not match.")
    else:
        try:
            import requests

            url = f"{st.secrets['SUPABASE_URL']}/auth/v1/admin/users/reset-password"
            headers = {
                "apikey": st.secrets["SUPABASE_KEY"],
                "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}",
                "Content-Type": "application/json",
            }
            data = {"token": token, "password": new_password}

            res = requests.post(url, json=data, headers=headers)

            if res.status_code in [200, 204]:
                st.success("Password reset successfully! You can now log in.")
                st.page_link("pages/00_login.py", label="Go to Login")
            else:
                st.error(f"Failed to reset password: {res.text}")

        except Exception as e:
            st.error(f"Error: {e}")
