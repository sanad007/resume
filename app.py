import streamlit as st
import PyPDF2
import google.generativeai as genai
from PIL import Image

# Configure your Gemini API Key
genai.configure(api_key="YOUR_GEMINI_API_KEY")  # Replace with your actual Gemini API key

# Function to list available models in the Gemini API
def list_available_models():
    try:
        # Get available models
        client = genai.GenerativeModelClient()  # Initialize the client
        models = client.list_models()  # List available models
        model_names = [model.name for model in models]
        st.write("Available Models:", model_names)
    except Exception as e:
        st.error(f"Error listing models: {e}")

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to analyze resume with the correct Gemini model
def analyze_resume_with_gemini(resume_text):
    prompt = f"""
    Analyze the following resume text and provide:
    1. Pros of this resume
    2. Cons of this resume
    3. ATS (Applicant Tracking System) score out of 100
    
    Resume Text:
    {resume_text}
    """
    
    try:
        # Use the correct model for Gemini analysis (replace '<correct_model_name>' with the valid model)
        model = genai.GenerativeModel("<correct_model_name>")  # Replace with valid model name
        response = model.generate_content(prompt)
        return response.text
    except google.api_core.exceptions.NotFound as e:
        st.error(f"❌ The requested resource was not found: {e}")
        return None
    except google.api_core.exceptions.DeadlineExceeded as e:
        st.error(f"❌ The request timed out: {e}")
        return None
    except google.api_core.exceptions.PermissionDenied as e:
        st.error(f"❌ Permission denied: {e}")
        return None
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {e}")
        return None

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

# Analyze button to trigger the resume evaluation
if uploaded_file:
    st.subheader("Resume Text Preview")
    
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = uploaded_file.read().decode("utf-8")

    st.code(resume_text[:3000], language="markdown")  # limit preview to first 3000 chars

    # Show "Analyze" button
    analyze_button = st.button("Analyze Resume")
    
    if analyze_button:
        st.subheader("AI-Powered Evaluation")
        
        with st.spinner("Analyzing resume with Gemini AI..."):
            result = analyze_resume_with_gemini(resume_text)

        if result:
            # Extract sections from the result
            try:
                pros = result.split("2.")[0].replace("1.", "").strip()
                cons = result.split("2.")[1].split("3.")[0].strip()
                ats_score = result.split("3.")[1].strip()

                st.markdown("### ✅ Pros")
                st.success(pros)

                st.markdown("### ❌ Cons")
                st.warning(cons)

                st.markdown("### 📊 ATS Score")
                st.info(ats_score)
            except Exception as e:
                st.error(f"Error parsing the analysis result: {e}")

else:
    st.info("Please upload a resume (PDF or text) to start the analysis.")

# Call the function to list available models if you need to see the available models
list_available_models()
