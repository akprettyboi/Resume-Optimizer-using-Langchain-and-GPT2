import fitz  # PyMuPDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from typing import Dict, List
import json

# In pdf_processor.py > extract_text_from_pdf()
def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        doc = fitz.open(pdf_path)
        text_sections = []
        
        for page in doc:
            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE).get("blocks", [])
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            # Add null checks for font properties
                            text_sections.append({
                                "text": span.get("text", ""),
                                "font_size": span.get("size", 11),  # Default font size
                                "font": span.get("font", "unknown"),
                                "is_bold": bool(span.get("flags", 0) & 2 ** 4)
                            })
        return json.dumps(process_text_sections(text_sections))
    except Exception as e:
        raise RuntimeError(f"PDF processing failed: {str(e)}")
    
    # # Process sections to identify headers and content
    # structured_content = process_text_sections(text_sections)
    # return json.dumps(structured_content)

def process_text_sections(sections: List[Dict]) -> Dict:
    """
    Process extracted text sections to identify document structure
    """
    structured_content = {
        "header": {},
        "summary": "",
        "experience": [],
        "education": [],
        "skills": []
    }
    
    current_section = 0
    current_font_size = None
    
    for section in sections:
        text = section["text"].strip()
        font_size = section["font_size"]
        
        # Identify section headers
        if current_font_size is not None and section["is_bold"] and font_size > current_font_size:
            if "EXPERIENCE" in text.upper():
                current_section = "experience"
            elif "EDUCATION" in text.upper():
                current_section = "education"
            elif "SKILLS" in text.upper():
                current_section = "skills"
            elif "SUMMARY" in text.upper():
                current_section = "summary"
        
        # Add content to appropriate section
        if current_section:
            if current_section == "experience":
                structured_content["experience"].append(text)
            elif current_section == "education":
                structured_content["education"].append(text)
            elif current_section == "skills":
                structured_content["skills"].append(text)
            elif current_section == "summary":
                structured_content["summary"] += text + " "
    
    return structured_content

def generate_pdf(content: Dict, output_path: str):
    """
    Generate a PDF file from structured content
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=20
    )
    
    content_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12
    )
    
    # Add sections
    if content.get("summary"):
        story.append(Paragraph("Professional Summary", header_style))
        story.append(Paragraph(content["summary"], content_style))
        story.append(Spacer(1, 20))
    
    if content.get("experience"):
        story.append(Paragraph("Professional Experience", header_style))
        for exp in content["experience"]:
            story.append(Paragraph(exp, content_style))
        story.append(Spacer(1, 20))
    
    if content.get("education"):
        story.append(Paragraph("Education", header_style))
        for edu in content["education"]:
            story.append(Paragraph(edu, content_style))
        story.append(Spacer(1, 20))
    
    if content.get("skills"):
        story.append(Paragraph("Skills", header_style))
        skills_text = ", ".join(content["skills"])
        story.append(Paragraph(skills_text, content_style))
    
    doc.build(story)