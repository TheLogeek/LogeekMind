import streamlit as st
from google.genai.errors import APIError
from google.genai import types
from utils import get_gemini_client
import usage_manager as um

model_name = "gemini-2.5-flash"

System_instruction = (
    "You are a patient, expert, and encouraging teacher. "
    "Explain complex topics in a simple, step-by-step manner. "
    "Use clear analogies. After your explanation, ask a brief comprehension question."
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


if st.session_state.saved_notes:
    st.success("📘 Previously generated lecture notes found!")

    st.text_area("Lecture Notes", st.session_state.saved_notes, height=300)

    if um.premium_gate("Download Lecture Notes"):
        downloaded = st.download_button(
            "⬇ Download Previous Notes",
            data=st.session_state.saved_notes.encode("utf-8"),
            file_name=f"{st.session_state.last_prompt}_lecture_notes.txt",
            mime="text/plain",
        )

        if downloaded:
            st.session_state.saved_notes = None
            st.session_state.last_prompt = None
            st.session_state.messages = []
            st.success("✔ Notes cleared after download.")
            st.rerun()

    else:
        st.info("Create an account to download your notes.")
        st.page_link("pages/00_login.py", icon="🔑", label="Login/Signup")

    st.markdown("---")
    if st.button("🆕 Start New Teaching Session"):
        st.session_state.saved_notes = None
        st.session_state.last_prompt = None
        st.session_state.messages = []
        st.rerun()

    st.stop()


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

            if um.premium_gate("Download Lecture Notes"):
                downloaded = st.download_button(
                    label="⬇ Download Notes",
                    data=ai_text.encode("utf-8"),
                    file_name=f"{prompt}_lecture_notes.txt",
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