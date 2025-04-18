import os
import streamlit as st
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("❌ Gemini API key not found. Please set GEMINI_API_KEY in your environment.")
    st.stop()

genai.configure(api_key=api_key)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"❌ Error extracting text from PDF: {e}")
        return None

# Function to analyze resume with Gemini
def analyze_resume_with_gemini(resume_text):
    try:
        prompt = f"""
        You are a career expert and AI assistant.

        Analyze this resume and provide:
        1. Pros of this resume
        2. Cons of this resume
        3. ATS (Applicant Tracking System) Score out of 100

        Resume:
        {resume_text}
        """
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"❌ Error analyzing resume with Gemini AI: {e}")
        return "❌ Analysis failed. Please try again later."

# UI setup
st.set_page_config(page_title="AI Resume Analyzer", layout="centered", page_icon="📄")

st.markdown("""
    <h1 style='text-align: center; color: #004080;'>📄 AI Resume Analyzer</h1>
    <p style='text-align: center; color: #555;'>Upload your resume to get AI-powered feedback (Pros, Cons & ATS Score)</p>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"])

if uploaded_file:
    # Extract text based on file type
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = uploaded_file.read().decode("utf-8")

    if resume_text:
        st.subheader("📄 Resume Preview")
        st.code(resume_text[:3000])  # Show preview (limit to 3000 characters)

        with st.spinner("🤖 Analyzing resume..."):
            result = analyze_resume_with_gemini(resume_text)

        if "❌ Error" in result:
            st.error(result)
        else:
            # Try parsing based on known format
            try:
                pros = result.split("2.")[0].replace("1.", "").strip()
                cons = result.split("2.")[1].split("3.")[0].strip()
                ats_score = result.split("3.")[1].strip()
            except Exception as e:
                st.error(f"❌ Error parsing results: {e}")
                pros, cons, ats_score = "Could not parse pros", "Could not parse cons", "N/A"

            st.markdown("### ✅ Pros")
            st.success(pros)

            st.markdown("### ❌ Cons")
            st.warning(cons)

            st.markdown("### 📊 ATS Score")
            st.info(ats_score)
else:
    st.info("Please upload a resume (PDF or TXT) to begin.")
