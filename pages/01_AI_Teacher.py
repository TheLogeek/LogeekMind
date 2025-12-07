import streamlit as st
from google.genai.errors import APIError
from google.genai import types
from utils import get_gemini_client
import usage_manager as um

model_name = "gemini-2.5-flash"

System_instruction = AI_TEACHER_INSTRUCTIONS = (
    """
You are LogeekMind AI Teacher, an intelligent, patient, and highly skilled academic instructor designed to teach any 
topic at any educational level—from primary school to university.

Your goals are:
1. Teach clearly and accurately.
2. Adapt to the student’s level and learning style.
3. Explain difficult ideas in simple ways.
4. Guide the learner step-by-step.
5. Encourage understanding, not memorization.
6. Provide structured lessons, examples, and practice questions.

TEACHING STYLE:
- Friendly, encouraging, clear, and concise.
- Adjust difficulty automatically based on the student's question.
- Explain ideas using simple language and relatable analogies.
- Never overwhelm the learner.
- Use bullet points, lists, tables, diagrams when helpful.

WHEN A STUDENT ASKS A QUESTION:
1. Detect the student's level automatically (primary, secondary, university, technical).
2. Give a clear and direct answer first.
3. Break the concept down into simple steps.
4. Provide 1–3 examples.
5. Create a visual/text explanation if useful.
6. Offer an optional deeper explanation for advanced learners.
7. Provide 2–5 practice questions unless the student says otherwise.

BEHAVIOR RULES:
- Do not hallucinate facts or formulas. If unsure, say so.
- Adapt to Nigerian/British/International curriculum based on context.
- Avoid long paragraphs; use clean structure.
- Never shame or discourage learners.
- Show full steps for math/science problems.
- For essays, give structured frameworks (INTRO → POINTS → EXAMPLES → CONCLUSION).
- For programming questions, explain logic before code.
- Double-check calculations.
- Provide citations only when asked.

IF THE STUDENT REQUESTS A FULL LESSON:
Provide:
- A short introduction.
- Learning objectives.
- Well-structured sections.
- Examples.
- Summary.
- Practice questions with answers.

DO NOT:
- Give advanced explanations to beginners.
- Assume context not provided.
- Use overly casual language.
- Generate unsafe, harmful, or restricted content.
- Give legal or medical advice.

TONE:
You speak like a friendly, experienced teacher focused on helping students understand, not memorize. The tone must be supportive, respectful, and motivating.

DEFAULT RESPONSE FORMAT:
1. Direct Answer
2. Simplified Explanation
3. Step-by-Step Breakdown
4. Examples
5. Summary of Key Points
6. Practice Questions

Follow this unless the user requests a different style.
"""
)


st.title("🧠 Your AI Teacher")
st.markdown("Struggling with a topic? Tell me the subject and topic, and I'll explain it simply!")

client = get_gemini_client()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "saved_notes" not in st.session_state:
    st.session_state.saved_notes = None

if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None


for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(message["text"])


if prompt := st.chat_input("Ask your teacher a question..."):
    if not um.check_guest_limit("AI Teacher", limit=1):
        st.page_link("pages/00_login.py", icon="🔑", label="Login/Signup")
        st.stop()

    st.session_state.messages.append({"role": "user", "text": prompt})
    st.session_state.last_prompt = prompt

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("📝 Preparing Notes..."):
        try:
            contents = []

            for msg in st.session_state.messages:
                part = types.Part.from_text(text=msg["text"])
                content_obj = types.Content(role=msg["role"], parts=[part])
                contents.append(content_obj)

            response = client.models.generate_content(
                model=model_name,
                config=types.GenerateContentConfig(system_instruction=System_instruction),
                contents=contents,
            )

            ai_text = response.text

            with st.chat_message("assistant"):
                st.markdown(ai_text)

            st.session_state.messages.append({"role": "model", "text": ai_text})

            st.session_state.saved_notes = ai_text

            if "user" in st.session_state:
                auth_user_id = st.session_state.user.id
                username = st.session_state.user_profile.get("username", "Scholar")
                um.log_usage(auth_user_id, username, "AI Teacher", "generated", {"topic": prompt})

            if st.session_state.saved_notes is not None:
                if um.premium_gate("Download Lecture Notes"):
                    downloaded = st.download_button(
                        label="⬇ Download Notes",
                        data=st.session_state.saved_notes.encode("utf-8"),
                        file_name=f"{st.session_state.last_prompt}_lecture_notes.txt",
                        mime="text/plain",
                    )
                    if downloaded:
                        st.session_state.saved_notes = None
                        st.session_state.last_prompt = None
                        st.session_state.messages = []
                        st.rerun()
                else:
                    st.info("Creating an account is free and saves your progress!")
                    st.page_link("pages/00_login.py", icon="🔑", label="Login/Signup")

        except APIError as e:
            error = str(e)

            if "429" in error or "RESOURCE_EXHAUSTED" in error.upper():
                if "api_key" in st.session_state:
                    del st.session_state.api_key
                st.error("🚨 Quota Exceeded! The Gemini API key has reached its limit.")
                st.stop()

            elif "503" in error:
                st.warning("Gemini is experiencing high traffic. Try again soon.")
                st.info(
                    "In the meantime, try other features "
                    "(GPA Calculator, Study Scheduler, Lecture Note-to-Audio Converter, Audio-to-Text Converter)"
                )
            else:
                st.error(f"API Error: {e}")

        except Exception as e:
            st.error(f"Unexpected error: {e}")


st.markdown("---")
if st.button("🆕 Start New Teaching Session"):
    st.session_state.messages = []
    st.session_state.saved_notes = None
    st.session_state.last_prompt = None
    st.rerun()