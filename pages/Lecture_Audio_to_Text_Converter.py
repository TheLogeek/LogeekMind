import streamlit as st
import whisper
import tempfile
import os
#from fpdf import FPDF
#from io import BytesIO

@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

"""def create_pdf(text_content, filename):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=12)

    pdf.set_font("Arial", 'B', 16)

    pdf.cell(200, 10, txt="Lecture Transcription", ln=1, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, txt=text_content)
    pdf_buffer = BytesIO()

    pdf.output(dest=pdf_buffer)
    pdf_bytes = pdf_buffer.getvalue()
    return pdf_bytes"""

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
    
    if st.button("Convert and Generate PDF"):
        with st.spinner("Converting... this may take a few minutes for long lectures."):
            
            try:
                result = model.transcribe(audio_path)
                transcribed_text = result["text"]
                
                st.subheader("Transcription")
                st.code(transcribed_text)
                
                with st.spinner("Generating PDF..."):
                    st.success("Transcription complete and PDF is ready!")
                    filename = os.path.splitext(audio_file.name)[0] + "transcription.pdf"
                    
                    st.download_button(
                        label="Download Transcription as PDF",
                        data=transcribed_text.encode('utf-8'),
                        file_name=f"{filename}.txt",
                        mime="text/plain"
                    )
            except Exception as e:
                st.error(f"An error occurred during transcription: {e}")
            finally:
                os.remove(audio_path)