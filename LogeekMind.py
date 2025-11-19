import streamlit as st

APP_VERSION = "1.1.0"

st.set_page_config(
    page_title="LogeekMind: Your AI Academic Assistant",
    page_icon="favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#1E90FF">
""", unsafe_allow_html=True)

st.title("🧠 LogeekMind: The AI Academic Assistant")
st.markdown("""
Welcome to **LogeekMind**, your all-in-one AI platform designed to simplify studying, accelerate learning, 
and maximize your academic success.
""")

GITHUB_REPO_URL = "https://github.com/TheLogeek/LogeekMind"
st.markdown(f"""
Need help getting started or setting up your **Gemini API Key**?
[**View the complete LogeekMind README & Setup Guide here!**]({GITHUB_REPO_URL}#getting-started)
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.header("💡 AI Learning")
    st.info("Ask concepts, generate quizzes, and get instant feedback on any subject.")

with col2:
    st.header("📝 Content Mastery")
    st.info("Summarize long PDFs/notes, generate course outlines, and convert lectures audio to text and vice versa.")

with col3:
    st.header("🛠 Planning & Solving")
    st.info("Solve homework problems from images, plan your study schedule and calculate your GPA.")

st.markdown("---")

st.header("🚀 Get Started")
st.write("Use the **sidebar navigation** to access any of the powerful features.")
st.info("💡 **Tip:** You will be required to enter your Gemini API key in the sidebar to use AI features")
#st.sidebar.markdown("---")
st.sidebar.header("Developer & Feedback")
st.sidebar.info("Developed by **Solomon Adenuga a.k.a Logeek**.")

st.sidebar.markdown("""
If you encounter any issues, find a bug, or have a brilliant feature suggestion, your feedback is highly valued!
*📧 **Email:** [solomonadenuga8@gmail.com](mailto:solomonadenuga8@gmail.com)
*📱 **WhatsApp: [+2348023710562](https://wa.me/+2348023710562)**
""")

with st.sidebar:
	st.markdown("---")
	st.info(f"**LogeekMind Version:** **`v{APP_VERSION}`**")