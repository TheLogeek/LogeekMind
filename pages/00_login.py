import streamlit as st
import auth_manager as auth
import time

st.set_page_config(page_title="Login / Sign Up", page_icon="🔐", layout="wide")

st.markdown("""
    <style>
    /* Center the card on the screen */
    .stApp {
        background-color: #f7f9fc;
    }
    .main-card {
        max-width: 450px;
        margin: 50px auto;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        background-color: white;
    }
    h1 {
        text-align: center;
        color: #1f2937;
    }
    </style>
    <div class="main-card">
    """, unsafe_allow_html=True)

st.title("🔐 LogeekMind Access")

tab1, tab2 = st.tabs(["Login", "Sign Up"])

# --- LOGIN ---
with tab1:
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email_root")
        password = st.text_input("Password", type="password", key="login_pass_root")

        login_submitted = st.form_submit_button("Login", type="primary")

        if login_submitted:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                success, msg = auth.sign_in_user(email, password)
                if success:
                    st.success(msg)
                    time.sleep(1)
                    st.switch_page("LogeekMind_App.py")
                else:
                    st.error(f"Error: {msg}")

# --- SIGN UP ---
with tab2:
    with st.form("signup_form"):
        st.caption("Create a free account to unlock unlimited access and downloads.")
        new_email = st.text_input("Email", key="signup_email_root")
        new_username = st.text_input("Choose a Unique Username", key="signup_user_root",
                                     help="This will be visible in the Community Chat.")
        new_password = st.text_input("Password", type="password", key="signup_pass_root")

        # Checkbox for Terms (Required)

        pp_link = st.page_link("pages/98_Privacy_Policy.py", label="Read Privacy Policy", icon="📄")
        tos_link = st.page_link("pages/99_Terms_Of_Service.py", label="Read Terms of Service", icon="⚖️")

        terms_check = st.checkbox("I agree to the Privacy Policy and Terms of Service", key="terms_check_root")

        signup_submitted = st.form_submit_button("Create Account", type="primary")

        if signup_submitted:
            if not terms_check:
                st.error("You must agree to the Terms of Service to register.")
            elif not new_username:
                st.error("Please enter a username.")
            else:
                success, msg = auth.sign_up_user(new_email, new_password, new_username, terms_check)
                if success:
                    st.success(msg)
                    st.toast("Check your email to verify your account!", icon="📧")
                else:
                    st.error(msg)

st.markdown("</div>", unsafe_allow_html=True)