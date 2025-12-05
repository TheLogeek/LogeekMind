import streamlit as st
import whisper
import tempfile
import os
import usage_manager as um

# --------------------------
# LOAD WHISPER MODEL (CACHED)
# --------------------------
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

st.title("🎧 Lecture Audio-to-Text Converter & Document Generator")
st.markdown("Upload a lecture audio file to transcribe it and download the text as a .txt.")

model = load_whisper_model()
st.success("STT model loaded successfully! Ready for audio")

# --------------------------
# SESSION STATE VARIABLES
# --------------------------
if "audio_file" not in st.session_state:
    st.session_state.audio_file = None

if "audio_path" not in st.session_state:
    st.session_state.audio_path = None

if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = None

# --------------------------
# FILE UPLOADER
# --------------------------
uploaded_file = st.file_uploader(
    "Upload a lecture audio file (MP3, WAV, M4A, OGG)",
    type=["mp3", "wav", "m4a", "ogg"]
)

if uploaded_file is not None:
    st.session_state.audio_file = uploaded_file

    # Save temporary file
    with tempfile.NamedTemporaryFile(delete=False,
                                     suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
        tmp.write(uploaded_file.read())
        st.session_state.audio_path = tmp.name

# --------------------------
# AUDIO PLAYER
# --------------------------
if st.session_state.audio_file:
    st.audio(st.session_state.audio_file)

# --------------------------
# TRANSCRIBE FUNCTION
# --------------------------
def transcribe_audio():
    if not um.check_guest_limit("Lecture Audio to Text Converter", limit=2):
        st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")
        st.stop()

    try:
        with st.spinner("Converting... this may take a few minutes for long lectures."):
            result = model.transcribe(st.session_state.audio_path)
            st.session_state.transcribed_text = result["text"]

    except Exception as e:
        st.error(f"An error occurred during transcription: {e}")

# --------------------------
# BUTTONS
# --------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("Convert and Generate File", type="primary"):
        if st.session_state.audio_path is None:
            st.warning("Please upload an audio file first.")
        else:
            transcribe_audio()

with col2:
    if st.button("Generate New"):
        # Clear all session data
        st.session_state.audio_file = None
        st.session_state.audio_path = None
        st.session_state.transcribed_text = None
        st.rerun()

# SHOW TRANSCRIPTION + DOWNLOAD
if st.session_state.transcribed_text:
    st.subheader("Transcription")
    st.code(st.session_state.transcribed_text)

    if "user" in st.session_state:
        auth_user_id = st.session_state.user.id
        username = st.session_state.user_profile.get("username", "Scholar")
        um.log_usage(auth_user_id, username, "Lecture Audio to Text Converter", "generated", {"topic": 'N/A'})

    filename = os.path.splitext(st.session_state.audio_file.name)[0] + "_transcription.txt"

    if um.premium_gate("Download Transcript"):
        download_clicked = st.download_button(
            label="Download Transcript (.txt)",
            data=st.session_state.transcribed_text.encode("utf-8"),
            file_name=filename,
            mime="text/plain",
        )

        if download_clicked:
            # Delete transcript immediately after download
            st.session_state.transcribed_text = None

    else:
        st.info("Create a free account to download and save your transcripts.")
        st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")
