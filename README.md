# 📄 ATS Resume Analyzer (Google Gemini Pro + Streamlit + PyPDF2)

This project is an **end-to-end ATS (Applicant Tracking System) Resume Analyzer** powered by **Google Gemini Pro** and built with **Streamlit**.

It analyzes a candidate's resume against a job description and provides:

- ✅ **ATS Match Percentage**
- ✅ **Keyword & Skill Gap Analysis**
- ✅ **Improvement Suggestions & Learning Roadmap**
- ✅ **Detailed Resume Review**
- ✅ **Multi-page PDF Support using PyPDF2**

The goal is to simulate how modern ATS systems and hiring managers evaluate resumes, and help candidates optimize their profiles for real-world job descriptions.

---

## 🚀 Features

### 🧾 1. Multi-Page Resume Text Extraction (PyPDF2)

- Uses **PyPDF2** to read and extract text from each page of a PDF resume
- Handles multi-page resumes
- Optional `max_pages` parameter to limit how many pages are processed

### 🤖 2. AI-Powered ATS Analysis (Google Gemini Pro)

Three main analysis modes:

| Mode | Description |
|------|-------------|
| **Resume Review** | Detailed strengths/weaknesses, alignment with JD, bullet point critique |
| **Skill Improvement** | Skill gap detection + concrete roadmap (projects, courses, certifications) |
| **ATS Match %** | Match score (0–100%) + missing keywords and optimization tips |

### 📊 3. Visual ATS Score

- Extracts ATS match percentage from Gemini’s first output line
- Displays it as:
  - A large `ATS Match` metric
  - A progress bar for visual impact

### 🔐 4. Secure API Handling

- Uses `.env` for storing `GOOGLE_API_KEY`
- No secrets are hardcoded in the repository

---

## 🧠 How It Works

### 1. Resume Upload & Extraction

The user uploads a **PDF resume** via Streamlit:

```python
uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
```

Text is extracted from all (or first N) pages using **PyPDF2**:
```python
from PyPDF2 import PdfReader

reader = PdfReader(uploaded_file)
page_text = reader.pages[i].extract_text()
```
All page texts are concatenated into one string, with page markers like:
```text
--- Page 1 ---
<text>

--- Page 2 ---
<text>
```

### 2. Building the Multimodal Prompt

For each request, the app builds a Gemini input consisting of:
- A **role/task instruction** (one of the three prompt templates)
- The **job description text**
- The **resume text extracted from PDF**
```python
parts = [
  {"text": instruction},
  {"text": "Job Description:\n" + jd_text},
  {"text": "Candidate Resume (extracted from PDF):\n" + resume_text},
]
```
Then calls:
```python
model = genai.GenerativeModel("gemini-2.5-pro")
response = model.generate_content(parts)
```

### 3. ATS Match Score Parsing

For the ATS mode, the prompt enforces:
- The **first line** must be something like `78%`

The code extracts digits from the first line:
```python
lines = response.strip().splitlines()
first_line = lines[0].strip()
digits = "".join(ch for ch in first_line if ch.isdigit())
score = int(digits)
```

This drives:

- `st.metric("ATS Match", "78%")`
- `st.progress(score / 100)`

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| AI Model | Google Gemini 2.5 Pro |
| Frontend | Streamlit |
| Backend | Python 3.10+ |
| PDF text extraction | PyPDF2 |
| Environment Management | python-dotenv |

---

## 📦 Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/ats-gemini-pypdf2.git
cd ats-gemini-pypdf2
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
```

### 3️⃣ Activate the Virtual Environment
Windows:
```bash
venv\Scripts\activate
```
macOS / Linux:
```bash
source venv/bin/activate
```

### 4️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

## 🔐 Environment Setup

Create a .env file in the project root and add your Gemini API key:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```
Never commit `.env` to GitHub.

## ▶️ Run the App

Run the Streamlit app:
```bash
streamlit run app.py
```
Then open the provided local URL in your browser (usually http://localhost:8501).

Open in browser:
```bash
http://localhost:8501
```

## 📁 File Structure
```bash
📁 project-root/
│── app.py                # Main Streamlit application
│── requirements.txt      # Dependencies
│── README.md             # Project documentation
│── .env                  # Environment variables (ignored in git)
```

## 🧪 Example Use Cases

- Job seekers testing and improving their resumes
- Career coaches helping candidates with tailored feedback
- HR teams screening applicants against specific job descriptions
- Students preparing their first technical CV
- Portfolio/demo project showcasing practical LLM + PDF integration

## 🤝 Contributing

Contributions are welcome!

Ideas to extend:

- Export results as PDF or Markdown
- Add support for multiple resumes comparison
- Integrate LinkedIn job scraping for auto-filling job descriptions
- Auto-rewrite resume sections based on feedback

## ⭐ Support

If you find this project useful:

- ⭐ Star the repository
- 🗣️ Share it with friends or colleagues
- 💬 Open issues or PRs with suggestions

Happy hacking & job hunting! 🚀

