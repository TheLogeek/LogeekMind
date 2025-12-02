import streamlit as st
from google.genai.errors import APIError
from google.genai import types
from utils import get_gemini_client
import usage_manager as um

model_name = "gemini-2.5-flash"
System_instruction = (
        "You are a patient, expert, and encouraging teacher."
        "Explain complex topics in a simple, step-by-step manner."
        "Use clear analogies, and ask a brief comprehension question after your explanation to check understanding"
    )

st.title("🧠Your AI Teacher")
st.markdown("Struggling with a topic? Tell me the subject and topic, and I'll explain it simply!")

client = get_gemini_client()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(message["text"])

if prompt := st.chat_input("Ask your teacher a question..."):
    if not um.check_guest_limit("AI Teacher", limit=1):
        login_link = st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")
        st.stop()
    st.session_state.messages.append({"role": "user", "text": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("📝Preparing Notes..."):

        try:
            contents = []

            for msg in st.session_state.messages:
                part = types.Part.from_text(text=msg["text"])

                content_obj = types.Content(
                    role=msg["role"],
                    parts=[part]
                )

                contents.append(content_obj)

            response = client.models.generate_content(
                model=model_name,
                config=types.GenerateContentConfig(
                    system_instruction=System_instruction
                ),
                contents=contents
            )

            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "model", "text": response.text})
            if um.premium_gate("Download Lecture Notes"):
                st.download_button(
                    label="Download Notes",
                    data=response.text.encode('utf-8'),
                    file_name=f"{prompt} lecture_notes.txt",
                    mime="text/plain"
                )
            else:
                st.info("Creating an account is free and saves your progress!")
                login_link = st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")




        except APIError as e:

            error_text = str(e)

            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text.upper():

                if "api_key" in st.session_state:
                    del st.session_state.api_key

                st.error("🚨 **Quota Exceeded!** The Gemini API key has hit it's limit")

                st.stop()

            elif "503" in error_text:

                st.markdown("The Gemini AI model is currently experiencing high traffic. Please try again later. "

                        "Thank you for your patience!")

                st.info(
                    "In the meantime, you can try other non-AI features **(GPA Calculator, Study Scheduler, Lecture Note-to-Audio Converter, Lecture Audio-to-Text Converter)**")

            else:

                st.error(f"An API error occurred during generation: {e}")


        except Exception as e:

            st.error(f"An unexpected error occurred: {e}")
