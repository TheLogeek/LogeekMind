import streamlit as st
from google.genai.errors import APIError
from utils import get_gemini_client
from docx import Document
import io
import usage_manager as um

model_name = "gemini-2.5-flash"

st.title("📝Course Outline Generator")
st.markdown("Instantly generate a detailed, university-level course syllabus and outline")

client = get_gemini_client()

#User Input Form
with st.form("course_outline_form"):
    course_full_name = st.text_input("Course Full Name", placeholder="e.g.. Introduction to Computer Science")
    course_code = st.text_input("Course Code (Optional)", placeholder="e.g., CSC 101")
    university_name = st.text_input("University Name (Optional)", placeholder="e.g., Harvard University or Lagos State "
                                                                              "University")
    submitted = st.form_submit_button("Generate Outline", type="primary")

if submitted:
    if not course_full_name:
        st.error("Please enter the **Course Full Name** to generate an outline")
        st.stop()
    if not um.check_guest_limit("Course Outline Generator", limit=1):
        st.stop()

#AI Prompt
    uni_context = f"taught at {university_name}." if university_name else "taught at a major Nigerian University."

    code_context = f"(Code: {course_code})" if course_code else ""

    OUTLINE_PROMPT = f"""
    You are an expert curriculum designer. Generate a comprehensive, 12-week university_level course outline for the 
    course: "{course_full_name}" {code_context}. The course should reflect standards {uni_context}.
    
    **REQUIRED SECTIONS:**
    1. **Course Description:** (2-3 sentences)
    2. **Course Objectives:** (4-5 bullet points)
    3. **12-Week Schedule:** Use a **Markdown table** with the columns: **Week**, **Topic**, and **Key Learning 
    Objectives**.
    
    Ensure the output is formatted cleanly using **Markdown**.
    """

    with st.spinner(f"Generating 12-week outline for {course_full_name}..."):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[OUTLINE_PROMPT]
            )
            outline_text = response.text

            st.subheader("✔ Generated Course Outline")
            st.markdown(outline_text)

            doc = Document()
            doc.add_heading(f"Course Outline: {course_full_name}", 0)
            doc.add_paragraph(outline_text)

            doc_io = io.BytesIO()
            doc.save(doc_io)
            doc_io.seek(0)

            if um.premium_gate("Download Course Outline"):
                st.download_button(
                    label="Download as DOCX",
                    data=doc_io,
                    file_name=f"{course_full_name.replace(' ', '_')}_Outline.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            else:
                st.button("Download Course Outline (Login Required)", disabled=True)

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
                st.info("In the meantime, you can try other non-AI features **(GPA Calculator, Study Scheduler, Lecture Note-to-Audio Converter, Lecture Audio-to-Text Converter)**")
            else:
                st.error(f"An API error occurred during generation: {e}")

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")