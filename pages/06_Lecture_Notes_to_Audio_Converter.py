import streamlit as st
from gtts import gTTS
import io
import time
from pypdf import PdfReader
from io import BytesIO
from docx import Document
from utils import premium_gate

st.title("Lecture Notes-to-Audio Converter📢")
st.markdown("Converts your notes into an MP3 file")

def extract_text_from_uploaded_file(file):
    """Extracts text from a streamlit uploaded file based on its extension."""
    file_name = file.name

    if file_name.endswith('.pdf'):
        pdf_reader = PdfReader(BytesIO(file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return True, text

    elif file_name.endswith('.docx'):
        document = Document(BytesIO(file.read()))
        text = ""
        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"
        return True, text

    elif file_name.endswith('.txt'):
        return True, file.read().decode("utf-8")

    else:
        return False, None

def convert_to_audio(text):
    try:
        tts = gTTS(text=text, lang='en')

        audio_io = io.BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)

        return True, audio_io
    except Exception as e:
        return False, f"An error occurred during audio generation: {e}"

if 'input_mode' not in st.session_state:
    st.session_state.input_mode = 'paste'

def set_mode(mode):
    st.session_state.input_mode = mode

col1, col2 = st.columns(2)

with col1:
    if st.button("Paste Text", use_container_width=True, key='btn_paste'):
        set_mode('paste')

with col2:
    if st.button("Upload File (.txt, .pdf, .docx)", use_container_width=True, key='btn_upload'):
        set_mode('upload')

st.markdown("---")

lecture_text = None

if st.session_state.input_mode == 'paste':
    st.subheader("Text Input")
    lecture_text = st.text_area(
        "Paste your lecture notes here:",
        height=200,
        key='text_area_input'
    )

elif st.session_state.input_mode == 'upload':
    st.subheader("File Uploader")
    uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt", "docx"])
    if uploaded_file is not None:
        with st.spinner("Extracting text from file..."):
            is_true, lecture_text = extract_text_from_uploaded_file(uploaded_file)
            if is_true:
                pass
            else:
                st.error("Unsupported file type. ")

if lecture_text:
    st.info(f"Notes loaded. Character count: {len(lecture_text)}")

    if st.button("Generate Audio Lecture"):
            with st.spinner("Synthesizing audio..."):
                is_valid, audio_lecture = convert_to_audio(lecture_text)
                st.success("Audio generated successfully!")
                st.audio(audio_lecture, format='audio/mp3')
                if is_valid:
                    if premium_gate("Download Transcript"):
                        st.download_button(
                        label="Download Audio note",
                        data=audio_lecture.getvalue(),
                        file_name=f"Study_notes_audio_{time.strftime('%Y%m%d%H%M')}.mp3",
                        mime="audio/mp3"
                    )
                    else:
                        st.button("Download Transcript (Login Required)", disabled=True)
                else:
                    st.error(audio_lecture)
#else:
    #st.warning("Please paste some text or upload lecture note before generating audio.")
    #st.stop()