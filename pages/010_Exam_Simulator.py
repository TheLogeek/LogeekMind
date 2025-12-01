import streamlit as st
import time
import json
import io
from docx import Document
from streamlit_autorefresh import st_autorefresh
from google.genai.errors import APIError
from utils import get_gemini_client
import usage_manager as um

#push

# configuration and state
if 'exam_stage' not in st.session_state:
    st.session_state.exam_stage = "setup"  # Options: setup, active, finished
if 'exam_data' not in st.session_state:
    st.session_state.exam_data = []
if 'exam_answers' not in st.session_state:
    st.session_state.exam_answers = {}
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'duration_mins' not in st.session_state:
    st.session_state.duration_mins = 30

st.set_page_config(page_title="Exam Simulator", layout="wide")
st.title("🔥 Exam Simulator")


# callback to save radio selection immediately
def _save_radio_answer(idx):
    key = f"q_{idx}"
    # ensure exam_answers dict exists
    if "exam_answers" not in st.session_state or not isinstance(st.session_state.get("exam_answers"), dict):
        st.session_state["exam_answers"] = {}
    # read the widget value and persist into exam_answers using string key
    st.session_state["exam_answers"][str(idx)] = st.session_state.get(key)


# grading function
def calculate_grade(score, total):
    percentage = (score / total) * 100
    if percentage >= 70:
        return "A", "Excellent! Distinction level."
    elif percentage >= 60:
        return "B", "Very Good. Keep it up."
    elif percentage >= 50:
        return "C", "Credit. You passed, but barely."
    elif percentage >= 45:
        return "D", "Pass. You need to study more."
    elif percentage >= 40:
        return "E", "Weak Pass. Dangerous territory."
    else:
        return "F", "Fail. You are not ready for this exam."


model_name = "gemini-2.5-flash"
client = get_gemini_client()

# APP LOGIC

# STAGE 1: SETUP
if st.session_state.exam_stage == "setup":
    st.markdown("### 📝 Setup Your Mock Exam")
    col1, col2 = st.columns(2)

    with col1:
        course_code = st.text_input("Course Name", placeholder="e.g., Introduction to Computer Science")
        topic = st.text_input("Specific Topic (Optional)", placeholder="e.g., Algorithms")

    with col2:
        duration = st.selectbox("Exam Duration", [1, 5, 10, 30, 60], index=2, format_func=lambda x: f"{x} Minutes")
        num_q = st.slider("Number of Questions", 5, 50, 20)

    if st.button("Start Exam ⏱️", type="primary"):
        if not um.check_guest_limit("Exam Simulator", limit=1):
            st.stop()
        if not course_code:
            st.error("Please enter a Course Code.")
        else:
            with (st.spinner("Prof. LogeekMind is preparing your exam papers...")):
                st.session_state.course_code = course_code
                prompt = f"""
                    You are a strict university professor setting a final exam.
                    Course: {course_code}
                    Topic: {topic}

                    Generate {num_q} HARD, examination-standard multiple-choice questions.
                    These should not be simple definitions. They should require critical thinking or application of concepts.

                    OUTPUT FORMAT:
                    Return ONLY a raw JSON list of dictionaries. Do NOT use Markdown code blocks (like ```json).
                    Each dictionary must have these keys:
                    - "question": complex scenario or problem statement
                    - "options": A list of strings (e.g., ["Option A", "Option B", "Option C", "Option D"])
                    - "answer": The exact string of the correct option
                    - "explanation": A short explanation of why it is correct
                    """

                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[prompt]
                    )

                    cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
                    st.session_state.exam_data = json.loads(cleaned_text)

                except json.JSONDecodeError as e:
                    st.error(f"JSONDecodeError: The AI output was malformed. Details: {e}.")
                    st.stop()

                except APIError as e:
                    error_text = str(e)
                    if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text.upper():
                        if "api_key" in st.session_state:
                            del st.session_state.api_key
                        st.error("🚨 **Quota Exceeded!** The Gemini API key has hit its limit.")
                    elif "503" in error_text:
                        st.error(
                            """The Gemini AI model is currently experiencing high traffic. Please try again later.""")
                    else:
                        st.error("An API error occurred during generation.")
                    st.stop()

                except Exception as e:
                    st.error(f"Error: {e}")
                    st.stop()
                # 2. Set Timers
                st.session_state.duration_mins = duration
                st.session_state.start_time = time.time()
                # 3. Clear any previous saved answers & change Stage
                st.session_state.exam_answers = {}  # clear persisted answers
                # clear widget keys from previous run if any
                for k in list(st.session_state.keys()):
                    if k.startswith("q_"):
                        st.session_state.pop(k, None)
                st.session_state.exam_stage = "active"
                st.rerun()

# STAGE 2: EXAM ACTIVE
elif st.session_state.exam_stage == "active":

    elapsed_time = time.time() - st.session_state.start_time
    total_seconds = st.session_state.duration_mins * 60
    remaining_seconds = total_seconds - elapsed_time
    total_questions = len(st.session_state.exam_data)

    if total_questions == 0:
        st.warning("No exam data found — please restart and generate the exam.")
    else:
        # Timer card
        mins, secs = divmod(int(max(0, remaining_seconds)), 60)
        timer_color = "red" if mins < 2 else "green"
        st.markdown(f"""
            <div style="position: fixed; top: 60px; right: 20px; padding: 10px; background-color: {timer_color}; color: white; border-radius: 5px; z-index: 9999;">
                <b>Time Left: {mins:02d}:{secs:02d}</b>
            </div>
        """, unsafe_allow_html=True)

        # progress tracking
        answered_count = 0
        if isinstance(st.session_state.get("exam_answers"), dict):
            answered_count = sum(1 for v in st.session_state["exam_answers"].values() if v is not None)

        progress_percent = answered_count / total_questions if total_questions > 0 else 0
        st.subheader("Question Progress")
        st.progress(progress_percent, text=f"**{answered_count} / {total_questions}** Questions Answered")
        st.write("---")

        # Questions rendering
        for idx, q in enumerate(st.session_state.exam_data):
            st.markdown(f"**Q{idx + 1}: {q['question']}**")
            st.radio(
                "Select Answer:",
                q['options'],
                key=f"q_{idx}",
                label_visibility="collapsed",
                index=None,
                on_change=_save_radio_answer,
                args=(idx,)
            )
            st.write("---")

        # Manual submit button just flips stage (answers already saved)
        if st.button("Submit Exam Now"):
            st.session_state.exam_stage = "finished"
            st.rerun()

        # Auto-submit: if time expired, flip stage
        if remaining_seconds <= 0:
            st.session_state.exam_stage = "finished"
            st.rerun()

        # Keep timer ticking
        st_autorefresh(interval=1000, key="timer_refresh")



# STAGE 3: RESULTS & GRADING
elif st.session_state.exam_stage == "finished":
    st.title("📄 Exam Results")

    score = 0
    total = len(st.session_state.exam_data)

    for idx, q in enumerate(st.session_state.exam_data):
        # reference auto saved exam answers
        user_choice = None
        if isinstance(st.session_state.get("exam_answers"), dict):
            user_choice = st.session_state["exam_answers"].get(str(idx))
        if user_choice is None:
            user_choice = st.session_state.get(f"q_{idx}")

        if user_choice == q.get('answer'):
            score += 1

    st.session_state.exam_score = score
    grade, remark = calculate_grade(score, total)

    # Display grade card
    st.markdown(f"""
        <div style="padding: 20px; background-color: #f0f2f6; border-radius: 10px; border-left: 10px solid {'#4CAF50' if grade in ['A', 'B'] else '#FF5722'};">
            <h2>Grade: {grade}</h2>
            <h3>Score: {score} / {total}</h3>
            <p><i>{remark}</i></p>
        </div>
        <br>
    """, unsafe_allow_html=True)
    if grade == "A" or grade == "B":
        st.balloons()

    # Review Answers
    with st.expander("View Corrections"):
        for idx, q in enumerate(st.session_state.exam_data):
            user_choice = None
            if isinstance(st.session_state.get("exam_answers"), dict):
                user_choice = st.session_state["exam_answers"].get(str(idx))
            if user_choice is None:
                user_choice = st.session_state.get(f"q_{idx}")

            with st.expander(f"Q{idx + 1}: {q['question']}", expanded=True):
                if user_choice == q['answer']:
                    st.success(f"✅ Your Answer: {user_choice}")
                else:
                    if user_choice is None:
                        st.error("❌ Your Answer: (No answer provided)")
                    else:
                        st.error(f"❌ Your Answer: {user_choice}")
                    st.info(f"✅ Correct Answer: {q['answer']}")
                st.markdown(f"**Explanation:** {q.get('explanation', 'No explanation provided.')}")
            st.divider()

        doc = Document()
        course_code = st.session_state.get("course_code", "course")
        doc.add_heading(f"Exam Results: {course_code}", 0)
        doc.add_paragraph(f"Final Score: {st.session_state.exam_score}/{total}\n")
        doc.add_paragraph(f"Grade: {grade}")

        for idx, q in enumerate(st.session_state.exam_data):
            doc.add_heading(f"Q{idx + 1}: {q['question']}", level=2)
            doc.add_paragraph(f"Options: {q['options']}")
            doc.add_paragraph(f"Correct Answer: {q['answer']}")
            doc.add_paragraph(f"Explanation: {q['explanation']}")
            doc.add_paragraph("-" * 20)

        doc_io = io.BytesIO()
        doc.save(doc_io)
        doc_io.seek(0)

        if um.premium_gate("Download Exam Results"):
            st.download_button(
                label="Download Results as DOCX",
                data=doc_io,
                file_name=f"{course_code} Exam_Results.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        else:
            st.button("Download Exam Results (Login Required)", disabled=True)


    if st.button("Take Another Exam"):
        if um.premium_gate("Take Another Exam"):
            st.session_state.exam_stage = "setup"
            st.session_state.exam_answers = {}
            st.session_state.exam_score = None
            st.rerun()
        else:
            st.button("Take Another Exam (Login Required)", disabled=True)