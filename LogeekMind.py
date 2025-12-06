import streamlit as st
import streamlit.components.v1 as components
from auth_manager import sign_out_user

manifest_path = "/static/manifest.json"

css = """
<link rel="manifest" href='/static/manifest.json'>

<style>
    div[data-testid="stHtml"] {
        display: none;
    }

    /* GLOBAL FONT */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    /* HERO SECTION */
    .hero {
        padding: 60px 30px;
        border-radius: 20px;
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.15);
        margin-bottom: 30px;
    }

    .hero h1 {
        font-size: 40px;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .hero p {
        font-size: 18px;
        opacity: 0.95;
    }

    /* FEATURE CARDS */
    .feature-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        border: 1px solid #edf0f7;
        transition: 0.2s;
    }

    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    }

    .feature-icon {
        font-size: 32px;
        margin-bottom: 10px;
    }
</style>
"""

# Inject CSS safely
st.markdown(css, unsafe_allow_html=True)

APP_VERSION = "1.5.1"

st.set_page_config(
    page_title="LogeekMind: Your AI Academic Assistant",
    page_icon="favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------
# AUTH HEADER (FUNCTIONALITY UNTOUCHED)
# -----------------------------------------------------------------
def render_auth_header():
    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown(
            """
            <div class="hero">
                <h1>🧠 LogeekMind</h1>
                <p>Your all-in-one AI-powered learning assistant.  
                Understand faster, study smarter, achieve better.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Auth controls
    with col2:
        if "user" in st.session_state and st.session_state.user:
            username = st.session_state.user_profile.get("username", "Scholar")

            st.markdown(
                f"<div style='text-align:right; font-size:18px;'>👋 {username}</div>",
                unsafe_allow_html=True
            )

            if st.button("Log Out", key="header_logout_btn"):
                sign_out_user()
                st.rerun()

        else:
            st.markdown("<div style='text-align:right;'>Guest Mode</div>", unsafe_allow_html=True)
            if st.button("🔐 Login / Sign Up", type="primary", key="header_login_btn"):
                st.switch_page("pages/00_login.py")

render_auth_header()

# -----------------------------------------------------------------
# FEATURE SECTION
# -----------------------------------------------------------------
st.markdown("### ✨ What You Can Do With LogeekMind")
st.write("Explore powerful tools designed to supercharge your learning.")

feature_col1, feature_col2, feature_col3 = st.columns(3)

with feature_col1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">💡</div>
            <h4>AI Learning</h4>
            <p>Understand concepts, get quizzes, simulate exams, and learn interactively.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with feature_col2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <h4>Content Mastery</h4>
            <p>Summaries, course outlines, PDF analysis, lecture transcription and more.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with feature_col3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">⚙️</div>
            <h4>Planning & Solving</h4>
            <p>Solve homework, calculate GPA, plan your study schedule efficiently.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# -----------------------------------------------------------------
# GET STARTED
# -----------------------------------------------------------------
st.header("🚀 Get Started")
st.write("Use the **sidebar** to navigate all tools and features.")
st.info("💡 Enter your Gemini API key in the sidebar to activate all AI tools.")

# -----------------------------------------------------------------
# SIDEBAR (FUNCTIONALITY UNTOUCHED)
# -----------------------------------------------------------------
st.sidebar.header("Developer & Feedback")
st.sidebar.info(
    "Developed by **Solomon Adenuga (Logeek)**.\n\n"
    "📧 Email: solomonadenuga8@gmail.com\n"
    "📱 WhatsApp: +2348023710562"
)

st.sidebar.markdown("---")
st.sidebar.info(f"LogeekMind Version: **v{APP_VERSION}**")
