import streamlit as st
import pandas as pd
import datetime
from google.genai.errors import APIError
from utils import get_gemini_client
import usage_manager as um

model_name = "gemini-2.5-flash"

st.title("Study Schedule Generator 🗓️")
st.markdown("Create a personalized study plan for any exam or course.")

st.warning(
    """
    **LogeekMind 2.0 is Here! 🎉**

    This version of LogeekMind is no longer being actively updated. For a faster, more powerful, and feature-rich experience, please use the new and improved **LogeekMind 2.0**.

    **[👉 Click here to launch LogeekMind 2.0](https://logeekmind.vercel.app)**
    """,
    icon="🚀"
)

client = get_gemini_client()


if "schedule" not in st.session_state:
    st.session_state.schedule = None
if "schedule_filename" not in st.session_state:
    st.session_state.schedule_filename = None


with st.form("study_schedule_form"):
    st.subheader("Study Plan Details")
    col1, col2 = st.columns(2)
    with col1:
        course_name = st.text_input("Course Name", placeholder="e.g., Data Structures and Algorithms")
        exam_date = st.date_input("Exam Date", datetime.date.today() + datetime.timedelta(days=7))
    with col2:
        study_duration_hours = st.slider("Daily Study Hours", 1, 8, 2)
        study_days = st.multiselect(
            "Preferred Study Days",
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        )
    study_topics = st.text_area("Key Topics to Cover (comma-separated)",
                                placeholder="e.g., Linked Lists, Trees, Graphs, Sorting Algorithms")

    submitted = st.form_submit_button("Generate Study Schedule", type="primary")

if submitted:
    if not course_name or not study_topics:
        st.error("Please fill in Course Name and Key Topics.")
        st.stop()

    if not um.check_guest_limit("Study Schedule Generator", limit=1):
        st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")
        st.stop()

    prompt = f"""
    You are an expert academic planner. Create a detailed study schedule for the course: "{course_name}".
    The exam is on {exam_date}.
    The student can study for {study_duration_hours} hours per day on {", ".join(study_days)}.
    Key topics to cover: {study_topics}.

    Generate a day-by-day study plan, including specific topics, tasks, and estimated times.
    The output should be in Markdown format, using a table for the schedule.
    """

    with st.spinner("Crafting your personalized study schedule..."):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[prompt]
            )

            schedule_text = response.text
            st.session_state.schedule = schedule_text
            st.session_state.schedule_filename = f"{course_name.replace(' ', '_')}_Study_Schedule.txt"

            if "user" in st.session_state:
                auth_user_id = st.session_state.user.id
                username = st.session_state.user_profile.get("username", "Scholar")
                um.log_usage(auth_user_id, username, "Study Schedule Generator", "generated", {"course": course_name})


        except APIError as e:
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg.upper():
                if "api_key" in st.session_state:
                    del st.session_state.api_key
                st.error("🚨 **Quota Exceeded!** The Gemini API key has hit its limit.")
                st.stop()
            elif "503" in msg:
                st.warning("The Gemini AI model is currently experiencing high traffic. Please try again later.")
            else:
                st.error(f"API Error: {e}")
        except Exception as e:
            st.error(f"Unexpected Error: {e}")

if st.session_state.schedule is not None:
    st.subheader("Your Study Schedule")
    st.markdown(st.session_state.schedule)

    if um.premium_gate("Download Study Schedule"):
        download_clicked = st.download_button(
            label="⬇ Download Schedule as TXT",
            data=st.session_state.schedule.encode("utf-8"),
            file_name=st.session_state.schedule_filename,
            mime="text/plain"
        )
        if download_clicked:
            del st.session_state.schedule
            del st.session_state.schedule_filename
            st.rerun()
    else:
        st.info("Creating an account is free and saves your progress!")
        st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")


st.markdown("---")
if st.button("🆕 Generate New Schedule"):
    st.session_state.schedule = None
    st.session_state.schedule_filename = None
    st.rerun()