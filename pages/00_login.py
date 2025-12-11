import streamlit as st
import auth_manager as auth
import time

st.set_page_config(page_title="Login / Sign Up", page_icon="🔐", layout="wide")


st.title("🔐 LogeekMind Access")



#saved_email, saved_password = auth.get_saved_auth()

tab1, tab2 = st.tabs(["Login", "Sign Up"])

# LOGIN
with tab1:
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email_root")
        password = st.text_input("Password", type="password", key="login_pass_root")
        remember_me = st.checkbox("Remember Me", value=True)

        login_submitted = st.form_submit_button("Login", type="primary")

        if login_submitted:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                success, msg = auth.sign_in_user(email, password)
                if success:
                    st.success(msg)
                    if remember_me:
                        try:
                            auth.save_auth(email, password)
                        except:
                            pass
                    time.sleep(1)
                    st.switch_page("LogeekMind.py")
                else:
                    st.error(f"Error: {msg}")

    with st.form("forgot_pass_form"):
        st.subheader("Reset Password")
        reset_email = st.text_input("Enter your email: ")
        send_reset = st.form_submit_button("Send Reset Link")

        if send_reset:
            try:
                auth.supabase.auth.reset_password_for_email(reset_email, {"redirect_to":
                                                                              "https://logeekmind.streamlit.app/reset_password"})
                st.success("A reset link has been sent to your email.")
            except Exception as e:
                st.error(str(e))

#SIGN UP
with tab2:
    with st.form("signup_form"):
        st.caption("Create a free account to unlock unlimited access and downloads.")
        new_email = st.text_input("Email", key="signup_email_root")
        new_username = st.text_input("Choose a Unique Username", key="signup_user_root",
                                     help="This will be visible in the Community Chat.")
        new_password = st.text_input("Password", type="password", key="signup_pass_root")


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
                    st.toast("You can now proceed to login!", icon="📧")
                else:
                    st.error(msg)

#st.markdown("</div>", unsafe_allow_html=True)