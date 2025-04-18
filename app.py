import streamlit as st
import PyPDF2
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get Gemini API key from environment
api_key = os.getenv("GEMINI_API_KEY")

# Check if API key is available
if not api_key:
    st.error("❌ Gemini API key not found. Please set GEMINI_API_KEY in your environment.")
    st.stop()

# Configure the Gemini API with the provided key
genai.configure(api_key=api_key)

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def analyze_resume_with_gemini(resume_text):
    prompt = f"""
    Analyze the following resume text and provide:
    1. Pros of this resume
    2. Cons of this resume
    3. ATS (Applicant Tracking System) score out of 100
    
    Resume Text:
    {resume_text}
    """

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text

# Streamlit App UI
st.set_page_config(page_title="AI Resume Analyzer", layout="wide", page_icon=":briefcase:")

st.markdown(
    """
    <style>
    .main {
        background-color: #F8F9FA;
    }
    .title {
        text-align: center;
        font-size: 2.8em;
        font-weight: bold;
        margin-bottom: 0.2em;
        color: #004080;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2em;
        color: #555;
        margin-bottom: 2em;
    }
    .stApp {
        padding: 2rem;
    }
    </style>
    """, unsafe_allow_html=True
)

st.markdown('<div class="title">AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload your resume (PDF or text) to receive AI-generated pros, cons, and ATS score</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "txt"], label_visibility="visible")

if uploaded_file:
    st.subheader("Resume Text Preview")
    
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = uploaded_file.read().decode("utf-8")

    st.code(resume_text[:3000], language="markdown")  # limit preview to first 3000 chars

    st.subheader("AI-Powered Evaluation")
    with st.spinner("Analyzing resume with Gemini AI..."):
        result = analyze_resume_with_gemini(resume_text)

    # Extract sections
    pros = result.split("2.")[0].replace("1.", "").strip()
    cons = result.split("2.")[1].split("3.")[0].strip()
    ats_score = result.split("3.")[1].strip()

    st.markdown("### ✅ Pros")
    st.success(pros)

    st.markdown("### ❌ Cons")
    st.warning(cons)

    st.markdown("### 📊 ATS Score")
    st.info(ats_score)

else:
    st.info("Please upload a resume (PDF or text) to start the analysis.")
