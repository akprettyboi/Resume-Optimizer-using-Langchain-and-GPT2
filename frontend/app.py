import streamlit as st
import requests
import json
from typing import Dict, Optional
import time

# Configure page
st.set_page_config(
    page_title="AI Resume Optimizer",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .upload-box {
        border: 2px dashed #4CAF50;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .success-message {
        color: #4CAF50;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .error-message {
        color: #f44336;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

class ResumeOptimizerUI:
    def __init__(self):
        self.API_URL = "http://localhost:8000"  # FastAPI backend URL
        
        if 'file_id' not in st.session_state:
            st.session_state.file_id = None
        if 'optimization_complete' not in st.session_state:
            st.session_state.optimization_complete = False
    
    def render_header(self):
        """Render the application header"""
        st.title("🚀 AI Resume Optimizer")
        st.markdown("""
        Upload your resume and a job description to get an optimized version of your resume 
        that highlights your most relevant skills and experience.
        """)
    
    def upload_resume(self) -> Optional[str]:
        """Handle resume upload"""
        st.subheader("1. Upload Your Resume")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload your resume in PDF format"
        )
        
        if uploaded_file:
            try:
                files = {"file": uploaded_file}
                response = requests.post(f"{self.API_URL}/upload_resume", files=files)
                
                if response.status_code == 200:
                    file_id = response.json()["file_id"]
                    st.session_state.file_id = file_id
                    st.success("✅ Resume uploaded successfully!")
                    return file_id
                else:
                    st.error("❌ Error uploading resume. Please try again.")
                    return None
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                return None
    
    def process_job_description(self) -> Optional[Dict]:
        """Handle job description processing"""
        st.subheader("2. Enter Job Description")
        
        job_description = st.text_area(
            "Paste the job description here",
            height=200,
            help="Paste the complete job description to analyze required skills and experience"
        )
        
        if job_description:
            try:
                response = requests.post(
                    f"{self.API_URL}/process_job_description",
                    json={"text": job_description}
                )
                
                if response.status_code == 200:
                    keywords = response.json()["keywords"]
                    self.display_extracted_keywords(keywords)
                    return keywords
                else:
                    st.error("❌ Error processing job description. Please try again.")
                    return None
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                return None
    
    def display_extracted_keywords(self, keywords: Dict):
        """Display extracted keywords and skills"""
        with st.expander("View Extracted Keywords", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Required Skills")
                for skill in keywords["skills"]:
                    st.markdown(f"- {skill}")
            
            with col2:
                st.markdown("### Technical Requirements")
                for term in keywords["technical_terms"]:
                    st.markdown(f"- {term}")
    
    def optimize_resume(self, job_description: str):
        """Handle resume optimization"""
        st.subheader("3. Optimize Resume")
        
        if st.button("🔄 Generate Optimized Resume"):
            if not st.session_state.file_id:
                st.warning("⚠️ Please upload a resume first.")
                return
                
            if not job_description:
                st.warning("⚠️ Please enter a job description.")
                return
            
            try:
                with st.spinner("🔄 Optimizing your resume..."):
                    response = requests.post(
                        f"{self.API_URL}/generate_updated_resume/{st.session_state.file_id}",
                        json={"text": job_description}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result["status"] == "success":
                            st.session_state.optimization_complete = True
                            st.success("✅ Resume optimization complete!")
                            self.show_download_button(result["file_id"])
                        else:
                            st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                    else:
                        st.error("❌ Error generating optimized resume. Please try again.")
                        
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    def show_download_button(self, file_id: str):
        """Display download button for optimized resume"""
        st.markdown("### Download Your Optimized Resume")
        
        if st.download_button(
            label="📥 Download Optimized Resume",
            data=requests.get(f"{self.API_URL}/download_resume/{file_id}").content,
            file_name="optimized_resume.pdf",
            mime="application/pdf"
        ):
            st.success("✅ Download started!")
    
    def run(self):
        """Run the Streamlit application"""
        self.render_header()
        
        # Create two columns for the main content
        col1, col2 = st.columns([3, 2])
        
        with col1:
            self.upload_resume()
            job_description = st.text_area(
                "Enter Job Description",
                height=300,
                key="job_description"
            )
        
        with col2:
            if job_description:
                keywords = self.process_job_description()
                if keywords:
                    self.optimize_resume(job_description)

if __name__ == "__main__":
    app = ResumeOptimizerUI()
    app.run()