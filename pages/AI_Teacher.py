import streamlit as st
from google.genai.errors import APIError
from google.genai import types
from utils import get_gemini_client

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
    st.session_state.messages.append({"role": "user", "text": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

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
        st.download_button(
            label="Download Notes",
            data=response.text.encode('utf-8'),
            file_name=f"{prompt} lecture_notes.txt",
            mime="text/plain"
        )



    except APIError as e:

        error_text = str(e)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text.upper():

            if "api_key" in st.session_state:
                del st.session_state.api_key

            st.error("🚨 **Quota Exceeded!** Your Gemini API key has hit it's limit")

            st.stop()

        elif "503" in error_text:

            st.markdown("The Gemini AI model is currently experiencing high traffic. Please try again later. "

                        "Thank you for your patience!")

            st.info(
                "In the meantime, you can try other non-AI features **(GPA Calculator, Study Scheduler Lecture Note-to-Audio Converter, Lecture Audio-to-Text Converter)**")

        else:

            st.error(f"An API error occurred during generation: {e}")


    except Exception as e:

        st.error(f"An unexpected error occurred: {e}")