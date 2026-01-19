import streamlit as st
from gtts import gTTS
import io
import time
from pypdf import PdfReader
from io import BytesIO
from docx import Document
import usage_manager as um


st.title("Lecture Notes-to-Audio Converter 📢")
st.markdown("Convert your notes into an MP3 lecture instantly!")

st.warning(
    """
    **LogeekMind 2.0 is Here! 🎉**

    This version of LogeekMind is no longer being actively updated. For a faster, more powerful, and feature-rich experience, please use the new and improved **LogeekMind 2.0**.

    **[👉 Click here to launch LogeekMind 2.0](https://logeekmind.vercel.app)**
    """,
    icon="🚀"
)

if "audio_data" not in st.session_state:
    st.session_state.audio_data = None
if "audio_filename" not in st.session_state:
    st.session_state.audio_filename = None
if "lecture_text" not in st.session_state:
    st.session_state.lecture_text = None
if "input_mode" not in st.session_state:
    st.session_state.input_mode = "paste"


def extract_text_from_uploaded_file(file):
    filename = file.name.lower()

    if filename.endswith(".pdf"):
        pdf_reader = PdfReader(BytesIO(file.read()))
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return True, text

    elif filename.endswith(".docx"):
        document = Document(BytesIO(file.read()))
        text = "\n".join(p.text for p in document.paragraphs)
        return True, text

    elif filename.endswith(".txt"):
        return True, file.read().decode("utf-8")

    return False, None


def convert_to_audio(text):
    try:
        tts = gTTS(text=text, lang="en")

        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        return True, audio_buffer
    except Exception as e:
        return False, f"Error during audio generation: {e}"


col1, col2 = st.columns(2)
with col1:
    if st.button("Paste Text", use_container_width=True):
        st.session_state.input_mode = "paste"

with col2:
    if st.button("Upload File (.txt, .pdf, .docx)", use_container_width=True):
        st.session_state.input_mode = "upload"

st.markdown("---")

lecture_text = None

if st.session_state.input_mode == "paste":
    st.subheader("Text Input")
    lecture_text = st.text_area("Paste your lecture notes:", height=200)

elif st.session_state.input_mode == "upload":
    st.subheader("File Uploader")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"])

    if uploaded_file:
        with st.spinner("Extracting text…"):
            ok, lecture_text = extract_text_from_uploaded_file(uploaded_file)
            if not ok:
                st.error("Unsupported file format.")
                st.stop()

if lecture_text:
    st.session_state.lecture_text = lecture_text
    st.info(f"Notes loaded. Characters: {len(lecture_text)}")


if st.button("Generate Audio Lecture"):
    if st.session_state.lecture_text:
        if not um.check_guest_limit("Lecture Notes to Audio Converter", limit=1):
            st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")
            st.stop()
    else:
        st.warning("Provide your lecture text or file!")
        st.stop()

    with st.spinner("Generating audio… this may take a few minutes for long notes."):
        ok, audio_buffer = convert_to_audio(st.session_state.lecture_text)

    if not ok:
            st.error(audio_buffer)
            st.stop()

    if "user" in st.session_state:
            auth_user_id = st.session_state.user.id
            username = st.session_state.user_profile.get("username", "Scholar")
            um.log_usage(auth_user_id, username, "Lecture Notes to Audio Converter", "generated", {"topic": 'N/A'})

    filename = f"Study_notes_audio_{time.strftime('%Y%m%d%H%M')}.mp3"
    st.session_state.audio_filename = filename
    st.session_state.audio_data = audio_buffer.getvalue()

if st.session_state.audio_data is not None:
    st.success("✔ Audio generated!")
    st.audio(st.session_state.audio_data, format="audio/mp3")
    if um.premium_gate("Download Transcript"):
            download_clicked = st.download_button(
                label="⬇ Download Audio Lecture",
                data=st.session_state.audio_data,
                file_name=st.session_state.audio_filename,
                mime="audio/mp3"
            )
            if download_clicked:
                del st.session_state.audio_data
                del st.session_state.audio_filename
                del st.session_state.lecture_text
                st.rerun()
    else:
            st.info("Create an account to download.")
            st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")
            st.stop()


st.markdown("---")
if st.button("🆕 New Audio Lecture"):
    st.session_state.audio_data = None
    st.session_state.audio_filename = None
    st.session_state.lecture_text = None
    st.rerun()
