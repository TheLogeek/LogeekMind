import streamlit as st
from gtts import gTTS
import io
import time
from pypdf import PdfReader
from io import BytesIO
from docx import Document
import usage_manager as um
from lib.storage_manager import upload_file_to_bucket, create_content_record


st.title("Lecture Notes-to-Audio Converter 📢")
st.markdown("Converts your notes into an MP3 file")


if "audio_data" not in st.session_state:
    st.session_state.audio_data = None
if "audio_filename" not in st.session_state:
    st.session_state.audio_filename = None
if "lecture_text" not in st.session_state:
    st.session_state.lecture_text = None
if "input_mode" not in st.session_state:
    st.session_state.input_mode = "paste"


def extract_text_from_uploaded_file(file):
    file_name = file.name.lower()

    if file_name.endswith(".pdf"):
        pdf_reader = PdfReader(BytesIO(file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += (page.extract_text() or "") + "\n"
        return True, text

    elif file_name.endswith(".docx"):
        document = Document(BytesIO(file.read()))
        text = "\n".join(p.text for p in document.paragraphs)
        return True, text

    elif file_name.endswith(".txt"):
        return True, file.read().decode("utf-8")

    return False, None


def convert_to_audio(text):
    try:
        tts = gTTS(text=text, lang="en")

        audio_io = io.BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
        return True, audio_io

    except Exception as e:
        return False, f"An error occurred during audio generation: {e}"


if st.session_state.audio_data:
    st.success("📌 A previously generated audio lecture was found.")

    st.audio(st.session_state.audio_data, format="audio/mp3")

    if um.premium_gate("Download Transcript"):
        download_clicked = st.download_button(
            label="⬇ Download Previous Audio Lecture",
            data=st.session_state.audio_data,
            file_name=st.session_state.audio_filename,
            mime="audio/mp3",
            key="download_previous_audio",
        )

        if download_clicked:
            del st.session_state.audio_data
            del st.session_state.audio_filename
            st.success("✔ Previous audio cleared after download.")
            st.rerun()
    else:
        st.info("Create an account to download your previously generated audio.")
        st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")

    st.markdown("---")

    if st.button("🆕 Generate New Audio Lecture"):
        del st.session_state.audio_data
        del st.session_state.audio_filename
        del st.session_state.lecture_text
        st.rerun()

    st.stop()


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
    lecture_text = st.text_area("Paste your lecture notes here:", height=200)


elif st.session_state.input_mode == "upload":
    st.subheader("File Uploader")
    uploaded_file = st.file_uploader("Choose a PDF, TXT, or DOCX file", type=["pdf", "txt", "docx"])

    if uploaded_file:
        with st.spinner("Extracting text from file..."):
            ok, lecture_text = extract_text_from_uploaded_file(uploaded_file)
            if not ok:
                st.error("Unsupported file type.")
                st.stop()


if lecture_text:
    st.session_state.lecture_text = lecture_text
    st.info(f"Notes loaded. Character count: {len(lecture_text)}")


if st.session_state.lecture_text:
    if st.button("Generate Audio Lecture"):


        if not um.check_guest_limit("Lecture Notes to Audio Converter", limit=1):
            st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")
            st.stop()

        with st.spinner("Synthesizing audio..."):
            valid, audio_lecture = convert_to_audio(st.session_state.lecture_text)

        if valid:
            st.success("✔ Audio generated successfully!")
            st.audio(audio_lecture, format="audio/mp3")

            filename = f"Study_notes_audio_{time.strftime('%Y%m%d%H%M')}.mp3"
            st.session_state.audio_data = audio_lecture.getvalue()
            st.session_state.audio_filename = filename

            if um.premium_gate("Download Transcript"):
                download_clicked = st.download_button(
                    label="⬇ Download Audio Lecture",
                    data=st.session_state.audio_data,
                    file_name=filename,
                    mime="audio/mp3",
                    key="download_generated_audio",
                )

                if download_clicked:
                    del st.session_state.audio_data
                    del st.session_state.audio_filename
                    del st.session_state.lecture_text
                    st.success("✔ Audio cleared after download.")
                    st.rerun()

            else:
                st.info("Creating an account is free and saves your progress!")
                st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")
        else:
            st.error(audio_lecture)

        # after successful generation and you have audio_io (BytesIO) or audio bytes:
        # You set st.session_state.audio_data = audio_lecture.getvalue()

        if 'user' not in st.session_state or st.session_state.user is None:
            pass
        else:
            if st.button("Save Audio to Library"):
                try:
                    user_id = user_id = st.session_state.user['uuid']
                    audio_bytes = st.session_state.audio_data if isinstance(st.session_state.audio_data, (
                    bytes, bytearray)) else st.session_state.audio_data.getvalue()
                    filename = st.session_state.audio_filename or f"notes_audio_{time.strftime('%Y%m%d%H%M')}.mp3"
                    path = upload_file_to_bucket("user-files", user_id, audio_bytes, filename)
                    rec = create_content_record(
                        user_id=user_id,
                        title="Lecture Audio",
                        content_type="audio/mp3",
                        storage_path=path,
                        filename=filename,
                        size_bytes=len(audio_bytes),
                        content_json={"source": "Lecture Notes to Audio",
                                      "char_count": len(st.session_state.lecture_text or "")}
                    )
                    st.success("Audio saved to My Library ✅")
                except Exception as e:
                    st.error(f"Failed to save audio: {e}")

st.markdown("---")
if st.button("🆕 Generate New Audio Lecture"):
    st.session_state.audio_data = None
    st.session_state.audio_filename = None
    st.session_state.lecture_text = None
    st.rerun()
