import streamlit as st
from pypdf import PdfReader
from io import BytesIO
from docx import Document
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

st.title("📝 PDF/Notes Summarizer")
st.markdown("Upload your document and instantly receive a summary of its key points.")

st.warning(
    """
    **LogeekMind 2.0 is Here! 🎉**

    This version of LogeekMind is no longer being actively updated. For a faster, more powerful, and feature-rich experience, please use the new and improved **LogeekMind 2.0**.

    **[👉 Click here to launch LogeekMind 2.0](https://logeekmind.vercel.app)**
    """,
    icon="🚀"
)

if "lecture_text" not in st.session_state:
    st.session_state.lecture_text = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None


def extract_text_from_uploaded_file(file):
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

def summarize_text(lecture_text):

    parser = PlaintextParser.from_string(lecture_text, Tokenizer("english"))
    summarizer = TextRankSummarizer()

    total_sentences = len(parser.document.sentences)

    sentence_count = max(10, int(total_sentences * 0.12))

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
