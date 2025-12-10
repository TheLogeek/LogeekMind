import streamlit as st
from google.genai.errors import APIError
from pypdf import PdfReader
from io import BytesIO
from docx import Document
from utils import get_gemini_client
import usage_manager as um
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
import nltk

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")
#model_name = "gemini-2.5-flash"

st.title("📝 PDF/Notes Summarizer")
st.markdown("Upload your document and instantly receive a summary of its key points.")

#client = get_gemini_client()


if "lecture_text" not in st.session_state:
    st.session_state.lecture_text = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None


def extract_text_from_uploaded_file(file):
    """Extracts text from a streamlit uploaded file based on its extension."""
    file_name = file.name
    st.session_state.uploaded_file_name = file_name

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

def summarize_text(lecture_text, sentence_count=10):
    """Sends the text to Gemini for summarization
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
    """
    parser = PlaintextParser.from_string(lecture_text, Tokenizer("english"))
    summarizer = TextRankSummarizer()

    summary_sentences = summarizer(parser.document, sentence_count)

    key_points = "\n".join([f"- **{str(sentence)}**" for sentence in summary_sentences])

    overview = " ".join([str(sentence) for sentence in summary_sentences[:3]])

    final_summary = f"### **Key Points**\n{key_points}\n\n### **Overview**\n{overview}"

    return final_summary


uploaded_file = st.file_uploader("Choose a PDF, TXT or DOCX file", type=["pdf", "txt", "docx"])
if uploaded_file is not None:
    st.session_state.lecture_text = extract_text_from_uploaded_file(uploaded_file)

if st.session_state.lecture_text:
    st.info(f"Successfully extracted {len(st.session_state.lecture_text):,} characters of text.")

    if st.button("Generate Summary"):
        if not um.check_guest_limit("Summarizer", limit=1):
            st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")
            st.stop()

        with st.spinner("Generating key points..."):
            try:
                st.session_state.summary = summarize_text(st.session_state.lecture_text)
                st.success("Summary Complete!")

            #except APIError as e:
                #error_text = str(e)
                #if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text.upper():
                    #if "api_key" in st.session_state:
                        #del st.session_state.api_key
                    #st.error("🚨 **Quota Exceeded!** The Gemini API key has hit its limit")
                    #st.stop()
                #elif "503" in error_text:
                    #st.markdown("The Gemini AI model is currently experiencing high traffic. Please try again later.")
                    #st.info("Meanwhile, try other non-AI features like GPA Calculator, Study Scheduler, etc.")
                #else:
                    #st.error(f"An API Error occurred: {e}")
            except Exception as e:
                st.error(f"An Error occurred: {e}")


if st.session_state.summary:
    st.markdown("---")
    st.subheader("Key Takeaways")
    st.markdown(st.session_state.summary)

    if "user" in st.session_state:
        auth_user_id = st.session_state.user.id
        username = st.session_state.user_profile.get("username", "Scholar")
        um.log_usage(auth_user_id, username, "Summarizer", "generated", {"topic": 'N/A'})

    col1, col2 = st.columns(2)

    with col1:
        if um.premium_gate("Download Summary"):
            download_clicked = st.download_button(
                label="Download Summary",
                data=st.session_state.summary.encode("utf-8"),
                file_name=f"{st.session_state.uploaded_file_name}_lecture_summary.txt",
                mime="text/plain"
            )
            if download_clicked:
                st.session_state.summary = None
                st.session_state.lecture_text = None
                st.session_state.uploaded_file_name = None
        else:
            st.info("Creating an account is free and saves your progress!")
            st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")

    with col2:
        if st.button("Generate New Summary"):
            st.session_state.summary = None
            st.session_state.lecture_text = None
            st.session_state.uploaded_file_name = None
            st.rerun()
