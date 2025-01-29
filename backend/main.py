from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import Dict, List
import os
import json
from utils.pdf_processor import extract_text_from_pdf, generate_pdf
from utils.nlp_processor import extract_keywords_from_job_description
from utils.resume_optimizer import optimize_resume
from utils.db_manager import save_temp_file, get_temp_file, cleanup_temp_files
import traceback


app = FastAPI(title="Resume Optimizer API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobDescription(BaseModel):
    text: str

class OptimizationResult(BaseModel):
    status: str
    file_id: str = None
    error: str = None

# In main.py > upload_resume()
@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)) -> Dict:
    try:
        # Add file size validation
        max_size = 5 * 1024 * 1024  # 5MB
        contents = await file.read()
        if len(contents) > max_size:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Verify PDF magic number
        if contents[:4] != b'%PDF':
            raise HTTPException(status_code=400, detail="Invalid PDF file")
            
        file_id = await save_temp_file(file)
        pdf_path = get_temp_file(file_id)
        
        # Add error logging
        print(f"Processing PDF: {pdf_path}")
        extracted_text = extract_text_from_pdf(pdf_path)
        
        # Store text as plain text instead of JSON
        with open(f"temp/{file_id}.txt", "w") as f:
            f.write(extracted_text)  # Ensure this is string data
            
        return {"status": "success", "file_id": file_id}
        
    except Exception as e:
        # Add detailed error logging
        print(f"Upload Error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# @app.post("/upload_resume")
# async def upload_resume(file: UploadFile = File(...)) -> Dict:
#     """
#     Upload and process a resume PDF file
#     """
#     try:
#         if not file.filename.endswith('.pdf'):
#             raise HTTPException(status_code=400, detail="Only PDF files are accepted")
        
#         # Save uploaded file temporarily
#         file_id = await save_temp_file(file)
        
#         # Extract text from PDF
#         pdf_path = get_temp_file(file_id)
#         extracted_text = extract_text_from_pdf(pdf_path)
        
#         # Store extracted text for later use
#         with open(f"temp/{file_id}.txt", "w") as f:
#             f.write(extracted_text)
        
#         return {"status": "success", "file_id": file_id}
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_job_description")
async def process_job_description(job_description: JobDescription) -> Dict:
    """
    Process job description and extract key information
    """
    try:
        keywords = extract_keywords_from_job_description(job_description.text)
        return {
            "status": "success",
            "keywords": keywords
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_updated_resume/{file_id}")
async def generate_updated_resume(file_id: str, job_description: JobDescription) -> OptimizationResult:
    """
    Generate an optimized resume based on the job description
    """
    try:
        # Get original resume text
        resume_path = f"temp/{file_id}.txt"
        if not os.path.exists(resume_path):
            raise HTTPException(status_code=404, detail="Resume not found")
            
        with open(resume_path, "r") as f:
            resume_text = f.read()
            
        # Extract keywords from job description
        keywords = extract_keywords_from_job_description(job_description.text)
        
        # Optimize resume
        optimized_resume = optimize_resume(resume_text, keywords, job_description.text)
        
        # Generate new PDF
        output_path = f"temp/{file_id}_optimized.pdf"
        generate_pdf(optimized_resume, output_path)
        
        return OptimizationResult(status="success", file_id=f"{file_id}_optimized")
        
    except Exception as e:
        return OptimizationResult(status="error", error=str(e))

@app.get("/download_resume/{file_id}")
async def download_resume(file_id: str):
    """
    Download the optimized resume
    """
    try:
        file_path = f"temp/{file_id}.pdf"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
            
        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename="optimized_resume.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """
    Initialize required directories and resources
    """
    os.makedirs("temp", exist_ok=True)

@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup temporary files
    """
    cleanup_temp_files()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)