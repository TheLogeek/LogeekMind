import streamlit as st
from gtts import gTTS
import io
import time
from pypdf import PdfReader
from io import BytesIO
from docx import Document
import usage_manager as um
from lib.storage_manager import upload_file_to_bucket, create_content_record


# -------------------------------------------------------
# Page Title
# -------------------------------------------------------
st.title("Lecture Notes-to-Audio Converter 📢")
st.markdown("Convert your notes into an MP3 lecture instantly!")


# -------------------------------------------------------
# Session State Setup
# -------------------------------------------------------
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None
if "audio_filename" not in st.session_state:
    st.session_state.audio_filename = None
if "lecture_text" not in st.session_state:
    st.session_state.lecture_text = None
if "input_mode" not in st.session_state:
    st.session_state.input_mode = "paste"


# -------------------------------------------------------
# Extract Text from Uploaded File
# -------------------------------------------------------
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


# -------------------------------------------------------
# Convert Text to Audio
# -------------------------------------------------------
def convert_to_audio(text):
    try:
        tts = gTTS(text=text, lang="en")

        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        return True, audio_buffer
    except Exception as e:
        return False, f"Error during audio generation: {e}"


# -------------------------------------------------------
# Resume Previous Generation
# -------------------------------------------------------
if st.session_state.audio_data:
    st.success("📌 A previously generated audio lecture is ready")

    st.audio(st.session_state.audio_data, format="audio/mp3")

    if um.premium_gate("Download Transcript"):
        download_clicked = st.download_button(
            label="⬇ Download Previous Audio Lecture",
            data=st.session_state.audio_data,
            file_name=st.session_state.audio_filename,
            mime="audio/mp3",
        )
        if download_clicked:
            del st.session_state.audio_data
            del st.session_state.audio_filename
            st.success("✔ Removed previous lecture from memory")
            st.rerun()
    else:
        st.info("Login to download.")
        st.page_link("pages/00_login.py", label="Login / Signup", icon="🔑")

    st.markdown("---")

    if st.button("🆕 New Audio Lecture"):
        st.session_state.audio_data = None
        st.session_state.audio_filename = None
        st.session_state.lecture_text = None
        st.rerun()

    st.stop()


# -------------------------------------------------------
# Input Mode Selection
# -------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    if st.button("Paste Text", use_container_width=True):
        st.session_state.input_mode = "paste"

with col2:
    if st.button("Upload File (.txt, .pdf, .docx)", use_container_width=True):
        st.session_state.input_mode = "upload"

st.markdown("---")

lecture_text = None

# -------------------------------------------------------
# Text Input Mode
# -------------------------------------------------------
if st.session_state.input_mode == "paste":
    st.subheader("Text Input")
    lecture_text = st.text_area("Paste your lecture notes:", height=200)

# -------------------------------------------------------
# File Upload Mode
# -------------------------------------------------------
elif st.session_state.input_mode == "upload":
    st.subheader("File Uploader")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"])

    if uploaded_file:
        with st.spinner("Extracting text…"):
            ok, lecture_text = extract_text_from_uploaded_file(uploaded_file)
            if not ok:
                st.error("Unsupported file format.")
                st.stop()

# Save text to state if present
if lecture_text:
    st.session_state.lecture_text = lecture_text
    st.info(f"Notes loaded. Characters: {len(lecture_text)}")


# -------------------------------------------------------
# Generate Audio Button
# -------------------------------------------------------
if st.session_state.lecture_text:
    if st.button("Generate Audio Lecture"):
        if not um.check_guest_limit("Lecture Notes to Audio Converter", limit=1):
            st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")
            st.stop()

        with st.spinner("Generating audio…"):
            ok, audio_buffer = convert_to_audio(st.session_state.lecture_text)

        if not ok:
            st.error(audio_buffer)
            st.stop()

        st.success("✔ Audio generated!")
        st.audio(audio_buffer, format="audio/mp3")

        filename = f"Study_notes_audio_{time.strftime('%Y%m%d%H%M')}.mp3"
        st.session_state.audio_filename = filename
        st.session_state.audio_data = audio_buffer.getvalue()

        # -------------------------------------------------------
        # Allow download (premium)
        # -------------------------------------------------------
        if um.premium_gate("Download Transcript"):
            download_clicked = st.download_button(
                label="⬇ Download Audio Lecture",
                data=st.session_state.audio_data,
                file_name=filename,
                mime="audio/mp3",
            )
            if download_clicked:
                del st.session_state.audio_data
                del st.session_state.audio_filename
                del st.session_state.lecture_text
                st.rerun()
        else:
            st.info("Create an account to download.")
            st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")

        # -------------------------------------------------------
        # Save to Library (NEW — uses correct Supabase upload)
        # -------------------------------------------------------
        if "user" in st.session_state and st.session_state.user:
            if st.button("Save Audio to My Library"):
                try:
                    user_id = st.session_state.user.id

                    audio_bytes = (
                        st.session_state.audio_data
                        if isinstance(st.session_state.audio_data, (bytes, bytearray))
                        else st.session_state.audio_data.getvalue()
                    )

                    filename = st.session_state.audio_filename

                    # Upload using new correct pattern
                    path = upload_file_to_bucket(
                        user_id=user_id,
                        file_bytes=audio_bytes,
                        filename=filename
                    )

                    # Create record in DB
                    create_content_record(
                        user_id=user_id,
                        title="Lecture Audio",
                        content_type="audio/mp3",
                        storage_path=path,
                        filename=filename,
                        size_bytes=len(audio_bytes),
                        content_json={
                            "source": "Lecture Notes to Audio",
                            "char_count": len(st.session_state.lecture_text or "")
                        }
                    )

                    st.success("Audio saved to My Library! ✅")

                except Exception as e:
                    st.error(f"Failed to save audio: {e}")

        st.stop()


# -------------------------------------------------------
# Reset Button
# -------------------------------------------------------
st.markdown("---")
if st.button("🆕 New Audio Lecture"):
    st.session_state.audio_data = None
    st.session_state.audio_filename = None
    st.session_state.lecture_text = None
    st.rerun()
