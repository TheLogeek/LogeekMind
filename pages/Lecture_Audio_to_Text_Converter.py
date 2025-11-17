import streamlit as st
import whisper
import tempfile
import os
#from fpdf import FPDF
#from io import BytesIO

@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")


st.title("🎧Lecture Audio-to-text Converter & Document Generator")
st.markdown("Upload a lecture audio file to transcribe it and download the text as a .txt.")

model = load_whisper_model()
st.success("STT model loaded successfully! Ready for audio")

audio_file = st.file_uploader(
    "Upload a lecture audio file (MP3, WAV, M4A, OGG)",
    type=["mp3","wav","m4a","ogg"]
)

if audio_file is not None:
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.name.split('.'[-1])}") as tmp_file:
        tmp_file.write(audio_file.read())
        audio_path = tmp_file.name
        
    st.audio(audio_file)
    
    if st.button("Convert and Generate File"):
        with st.spinner("Converting... this may take a few minutes for long lectures."):
            
            try:
                result = model.transcribe(audio_path)
                transcribed_text = result["text"]
                
                st.subheader("Transcription")
                st.code(transcribed_text)
                
                with st.spinner("Generating file..."):
                    st.success("Transcription complete and file is ready!")
                    filename = os.path.splitext(audio_file.name)[0] + "transcription.txt"
                    
                    st.download_button(
                        label="Download Transcription as .txt file",
                        data=transcribed_text.encode('utf-8'),
                        file_name=filename,
                        mime="text/plain"
                    )
            except Exception as e:
                st.error(f"An error occurred during transcription: {e}")
            finally:
                os.remove(audio_path)