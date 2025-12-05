import streamlit as st
import streamlit.components.v1 as components
from auth_manager import sign_out_user

manifest_path = "/static/manifest.json"

html_code = f"""
    <link rel="manifest" href="{manifest_path}">
    <style>
        div[data-testid="stHtml]{{
            display: none;
        }}
    <style>
"""

components.html(html_code, height=0, width=0)

APP_VERSION = "1.5.0"

st.set_page_config(
    page_title="LogeekMind: Your AI Academic Assistant",
    page_icon="favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

ADMIN_ID = st.secrets["ADMIN_ID"]

if 'user' in st.session_state:
    if st.session_state.user.id == ADMIN_ID:
        st.sidebar.page_link("pages/_admin_dashboard.py", label="Admin Dashboard")

def render_auth_header():
    """Renders the login/logout status in the main app body."""
    # Use columns to position the logo/title on the left and auth button on the right
    col1, col2 = st.columns([4, 1])

    with col1:
        st.title("🧠 LogeekMind: The AI Academic Assistant")
        st.markdown("""
        Welcome to **LogeekMind**, your all-in-one AI platform designed to simplify studying, accelerate learning, 
        and maximize your academic success.
        """)

    with col2:
        if "user" in st.session_state and st.session_state.user:
            # Logged In State
            username = st.session_state.user_profile.get("username", "Scholar")

            st.markdown(f'<div style="text-align: right; margin-top: 10px;">👋 {username}</div>', unsafe_allow_html=True)

            if st.button("Log Out", key="header_logout_btn"):
                sign_out_user()
                st.rerun()

        else:
            # Guest State
            st.markdown(f'<div style="text-align: right; margin-top: 10px;">Guest Mode</div>', unsafe_allow_html=True)
            if st.button("🔐 Login / Sign Up", type="primary", key="header_login_btn"):
                st.switch_page("pages/00_login.py")


render_auth_header()

st.divider()

GITHUB_REPO_URL = "https://github.com/TheLogeek/LogeekMind"
st.markdown(f"""
Need help getting started or setting up your **Gemini API Key**?
[**View the complete LogeekMind README & Setup Guide here!**]({GITHUB_REPO_URL}#getting-started)
""")

col3, col4, col5 = st.columns(3)

with col3:
        st.header("💡 AI Learning")
        st.info("Ask concepts, generate quizzes, simulate real exam pressure and get instant feedback on any subject.")

with col4:
        st.header("📝 Content Mastery")
        st.info("Summarize long PDFs/notes, generate course outlines, and convert lectures audio to text and vice versa.")

with col5:
        st.header("🛠 Planning & Solving")
        st.info("Solve homework problems from images, plan your study schedule and calculate your GPA.")

st.markdown("---")

st.header("🚀 Get Started")
st.write("Use the **sidebar navigation** to access any of the powerful features.")
st.info("💡 **Tip:** You may be required to enter your Gemini API key in the sidebar to use AI features")
#st.sidebar.markdown("---")
st.sidebar.header("Developer & Feedback")
st.sidebar.info("Developed by [**Solomon Adenuga a.k.a Logeek**](https://github.com/TheLogeek).")

st.sidebar.markdown("""
If you encounter any issues, find a bug, or have a brilliant feature suggestion, your feedback is highly valued!
*📧 **Email:** [solomonadenuga8@gmail.com](mailto:solomonadenuga8@gmail.com)
*📱 **WhatsApp: [+2348023710562](https://wa.me/+2348023710562)**
""")

with st.sidebar:
        st.markdown("---")
        st.info(f"**LogeekMind Version:** **`v{APP_VERSION}`**")