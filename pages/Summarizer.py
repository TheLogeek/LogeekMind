import streamlit as st
from google.genai.errors import APIError
from pypdf import PdfReader
from io import BytesIO
from docx import Document
from utils import get_gemini_client

model_name = "gemini-2.5-flash"

st.title("📝 PDF/Notes Summarizer")
st.markdown("Upload your document and instantly receive a summary of its key points.")

client = get_gemini_client()

def extract_text_from_uploaded_file(file):
    """Extracts text from a streamlit uploaded file based on its extension."""
    file_name = file.name

    if file_name.endswith('.pdf'):
        pdf_reader = PdfReader(BytesIO(file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text

    elif file_name.endswith('.docx'):
        document = Document(BytesIO(file.read()))
        text = ""
        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"
        return text

    elif file_name.endswith('.txt'):
        return file.read().decode("utf-8")

    else:
        st.error("Unsupported file type. ")
        return None

def summarize_text(lecture_text):
    """Sends the text to Gemini for summarization."""
    prompt = (
        "Summarize the following lecture notes thoroughly. "
        "Output the most important key points as a clear, **bolded** bulleted list, "
        "and follow it with a one-paragraph summary overview. Use professional academic language. "
        f"\n\n--- NOTES ---\n\n{lecture_text}"
    )

    response = client.models.generate_content(
        model=model_name,
        contents=[prompt]
    )
    return response.text

try:
    uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt", "docx"])

    if uploaded_file is not None:
        with st.spinner("Extracting text from file..."):
            lecture_text = extract_text_from_uploaded_file(uploaded_file)

        if lecture_text:
            st.info(f"Successfully extracted {len(lecture_text):,} characters of text.")

            if st.button("Generate Summary"):
                with st.spinner("Generating key points..."):
                    summary = summarize_text(lecture_text)

                st.success("Summary Complete!")
                st.markdown("---")
                st.subheader("Key Takeaways")
                st.markdown(summary)
                st.download_button(
                    label="Download Summary",
                    data=summary.encode('utf-8'),
                    file_name=f"{uploaded_file.name}lecture_summary.txt",
                    mime="text/plain"
                )
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
        st.error(f"An API Error occurred: {e}")

except Exception as e:
    st.error(f"An Error occurred: {e}")