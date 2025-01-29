# Resume Optimizer - AI-Powered Resume Tailoring

## 📌 Project Overview
This project is an AI-powered Resume Optimizer that allows users to upload their resumes, input job descriptions, and generate a tailored resume aligning with the job description. The application integrates NLP and LLM technologies to extract key skills and rewrite resume sections accordingly.

## 🚀 Features
- Upload resume in PDF format
- Extract text from resume using PyMuPDF
- Extract keywords from job descriptions using spaCy and NLTK
- Modify resume using OpenAI's GPT-4 via LangChain
- Generate an updated PDF resume
- Simple Streamlit-based UI
- Deployable using Docker and AWS Lambda

---

## 🏗️ Tech Stack
### **Backend - FastAPI (Python)**
- **FastAPI** (Web framework for API handling)
- **PyMuPDF** (PDF text extraction)
- **spaCy / NLTK** (NLP-based keyword extraction)
- **LangChain + OpenAI GPT-4** (Resume modification)
- **FAISS** (For RAG-based improvements if needed)
- **pdfkit / ReportLab** (For generating PDFs)
- **Uvicorn** (Running FastAPI server)

### **Frontend - Streamlit (Python)**
- **Streamlit** (UI framework for user interaction)
- **Requests** (To communicate with FastAPI backend)
- **UI Elements**: File uploader, text area, process button, download button

### **LLM Integration - Resume Modification**
- **LangChain** (Framework for LLM interactions)
- **OpenAI API (GPT-4-Turbo)** (AI-powered resume rewriting)
- **JSON Formatting** (Retain structured formatting of resume)

### **PDF Processing**
- **PyMuPDF** (Text extraction from PDF)
- **pdfkit + wkhtmltopdf** (Generating professional PDF resumes)
- **ReportLab** (Alternative structured PDF creation)

### **Deployment**
- **Docker** (Containerization for backend services)
- **AWS Lambda** (Serverless deployment for backend)
- **Vercel / Streamlit Cloud** (Deploy frontend UI)

---

## 🔥 Installation & Setup
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-repo/resume-optimizer.git
cd resume-optimizer
```

### 2️⃣ Set Up Backend (FastAPI)
#### Install dependencies
```bash
pip install -r requirements.txt
```
#### Run FastAPI server
```bash
uvicorn main:app --reload
```

### 3️⃣ Set Up Frontend (Streamlit)
#### Install dependencies
```bash
pip install streamlit requests
```
#### Run Streamlit UI
```bash
streamlit run app.py
```

---

## 🛠️ API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload_resume` | POST | Upload a resume PDF and extract text |
| `/process_job_description` | POST | Extract keywords from job description |
| `/generate_updated_resume` | POST | Modify the resume using GPT-4 and return new content |
| `/download_resume` | GET | Download the newly generated resume PDF |

---

## 📌 Deployment
### **Using Docker**
#### Build and Run Docker container
```bash
docker build -t resume-optimizer .
docker run -p 8000:8000 resume-optimizer
```

### **Deploying on AWS Lambda**
- Package the FastAPI app using `serverless-wsgi`
- Deploy using AWS SAM or AWS Lambda UI

### **Deploying Streamlit UI on Vercel**
- Push frontend code to GitHub
- Deploy using Vercel CLI or GitHub integration

---

## ✅ Next Steps
1️⃣ Run the AI-generated code for each module
2️⃣ Test API endpoints using Postman
3️⃣ Integrate frontend with backend
4️⃣ Deploy the application

---

## 🎯 Contributing
Feel free to submit pull requests or raise issues to improve this project!

---

## 📝 License
This project is licensed under the MIT License. Feel free to modify and use it for your projects!


