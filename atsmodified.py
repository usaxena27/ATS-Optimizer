from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os

import google.generativeai as genai
from PyPDF2 import PdfReader  # <-- Using PyPDF2 for multi-page text extraction


# -------------------------------------------------------------------
# Gemini Configuration
# -------------------------------------------------------------------

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# -------------------------------------------------------------------
# Helper: Extract multi-page text from PDF using PyPDF2
# -------------------------------------------------------------------

def extract_text_from_pdf(uploaded_file, max_pages: int | None = None) -> str:
    """
    Extract text from an uploaded PDF using PyPDF2.
    Reads all pages (or up to max_pages if provided) and concatenates them.
    """
    if uploaded_file is None:
        raise FileNotFoundError("No file uploaded")

    uploaded_file.seek(0)  # Ensure pointer at start
    reader = PdfReader(uploaded_file)

    texts = []
    num_pages = len(reader.pages)

    for i in range(num_pages):
        if max_pages is not None and i >= max_pages:
            break
        page = reader.pages[i]
        page_text = page.extract_text() or ""
        if page_text.strip():
            texts.append(f"--- Page {i+1} ---\n{page_text.strip()}")

    full_text = "\n\n".join(texts).strip()

    if not full_text:
        raise ValueError("No text could be extracted from the PDF. "
                         "This might be a scanned document without selectable text.")

    return full_text


# -------------------------------------------------------------------
# Helper: Call Gemini with JD + resume text + instruction
# -------------------------------------------------------------------

def get_gemini_response(jd_text: str, resume_text: str, instruction: str) -> str:
    """
    Call Gemini model with:
    - instruction (role / task)
    - job description text
    - resume text (multi-page extracted from PDF)
    """
    model = genai.GenerativeModel("gemini-2.5-pro")  # or "gemini-1.5-flash"

    parts = []

    # Instruction / role
    parts.append({"text": instruction})

    # Job description
    if jd_text and jd_text.strip():
        parts.append({"text": "Job Description:\n" + jd_text.strip()})
    else:
        parts.append({"text": "No job description provided. Assume a generic technical role."})

    # Resume text
    parts.append({"text": "Candidate Resume (extracted from PDF):\n" + resume_text})

    response = model.generate_content(parts)
    return response.text


# -------------------------------------------------------------------
# Prompts / Instructions
# -------------------------------------------------------------------

PROMPT_ANALYZE = """
You are an experienced Technical Hiring Manager and ATS expert with over 10 years of experience
reviewing resumes in the fields of Data Science, Artificial Intelligence, Machine Learning, Data Analysis,
DevOps, Data Engineering, and Web Development.

Task:
1. Review the candidate's resume text against the job description.
2. Analyze line by line where relevant.
3. Highlight strengths and specific areas where the candidate is a strong match.
4. Point out flaws, vague language, weak bullet points, or missing impact statements.
5. Suggest concrete improvements to wording and structure.

Your response should be:
- Well structured with headings.
- Focused on how well the resume aligns with the job description.
- Honest but constructive and encouraging.
"""

PROMPT_SKILLS = """
You are a senior career coach and technical hiring manager.

Task:
1. Based on the resume and job description, identify the key skills, tools, and technologies required.
2. Show which of these the candidate already has.
3. Highlight gaps: skills, tools, or experiences that the candidate should build.
4. Recommend specific actions: courses, projects, certifications, or contributions to gain those skills.
5. Keep the tone supportive and practical.

Format:
- Section 1: Skills the candidate already matches.
- Section 2: Missing or weak skills (with priority).
- Section 3: Actionable roadmap (projects, learning, and improvements).
"""

PROMPT_MATCH = """
You are an expert ATS (Applicant Tracking System) and technical recruiter.

Task:
1. Evaluate how well the resume matches the job description in terms of:
   - Required skills and tools
   - Relevant experience
   - Domain/industry alignment
   - Keywords typically used by ATS
2. Decide an overall match percentage between 0 and 100.

VERY IMPORTANT OUTPUT FORMAT:
- The FIRST line of your response must be only the match percentage as an integer followed by a percent sign.
  Example: 78%
- After a blank line, provide:
  - A short explanation of why you gave that score.
  - A bullet list of important missing keywords/skills.
  - Suggestions to improve the match.

Do NOT include anything else on the first line except the percentage.
"""


# -------------------------------------------------------------------
# Streamlit UI
# -------------------------------------------------------------------

st.set_page_config(page_title="ATS Resume Expert", page_icon="📄")
st.title("📄 ATS Resume Expert (Gemini Powered)")
st.write(
    "Upload your resume (PDF) and paste a job description to get ATS-style analysis, "
    "skill improvement suggestions, and a match percentage."
)

# Job description input
input_text = st.text_area(
    "Job Description (paste here):",
    key="input",
    height=200,
    placeholder="Paste the job description here..."
)

# File upload
uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ Resume PDF uploaded successfully")

# Buttons
col1, col2, col3 = st.columns(3)
with col1:
    submit1 = st.button("Tell Me About the Resume")
with col2:
    submit2 = st.button("How Can I Improve My Skills?")
with col3:
    submit3 = st.button("Percentage Match (ATS Score)")

# -------------------------------------------------------------------
# Button Actions
# -------------------------------------------------------------------

if submit1:
    if uploaded_file is not None:
        try:
            with st.spinner("Analyzing resume vs job description..."):
                resume_text = extract_text_from_pdf(uploaded_file, max_pages=5)  # use up to 5 pages
                response = get_gemini_response(input_text, resume_text, PROMPT_ANALYZE)
            st.subheader("🧾 Detailed Resume Review")
            st.write(response)
        except Exception as e:
            st.error(f"Error during analysis: {e}")
    else:
        st.error("Please upload your resume PDF first.")

elif submit2:
    if uploaded_file is not None:
        try:
            with st.spinner("Analyzing skill gaps and improvement suggestions..."):
                resume_text = extract_text_from_pdf(uploaded_file, max_pages=5)
                response = get_gemini_response(input_text, resume_text, PROMPT_SKILLS)
            st.subheader("📈 Skill Gap & Improvement Plan")
            st.write(response)
        except Exception as e:
            st.error(f"Error during skill analysis: {e}")
    else:
        st.error("Please upload your resume PDF first.")

elif submit3:
    if uploaded_file is not None:
        try:
            with st.spinner("Calculating ATS match percentage..."):
                resume_text = extract_text_from_pdf(uploaded_file, max_pages=5)
                response = get_gemini_response(input_text, resume_text, PROMPT_MATCH)

            # Parse the first line as percentage
            lines = response.strip().splitlines()
            first_line = lines[0].strip() if lines else ""
            digits = "".join(ch for ch in first_line if ch.isdigit())

            score = None
            if digits:
                try:
                    score = int(digits)
                except ValueError:
                    score = None

            st.subheader("📊 ATS Match Result")

            if score is not None and 0 <= score <= 100:
                st.metric("ATS Match", f"{score}%")
                st.progress(score / 100)
            else:
                st.warning(
                    "Couldn't reliably parse the percentage from the model's first line. "
                    "Please check the raw response below."
                )

            st.markdown("---")
            st.write(response)

        except Exception as e:
            st.error(f"Error during ATS match evaluation: {e}")
    else:
        st.error("Please upload your resume PDF first.")