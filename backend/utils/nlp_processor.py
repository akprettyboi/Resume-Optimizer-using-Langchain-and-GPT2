import spacy
from typing import List, Dict
from collections import Counter
import yake
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import nltk

# Download required NLTK data
nltk.download('stopwords')
nltk.download('punkt')

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_keywords_from_job_description(text: str) -> Dict:
    """
    Extract key information from job description using multiple NLP techniques
    """
    # Initialize keyword extractor
    kw_extractor = yake.KeywordExtractor(
        lan="en",
        n=3,  # ngrams
        dedupLim=0.3,
        dedupFunc='seqm',
        windowsSize=1,
        top=20
    )
    
    # Process text with spaCy
    doc = nlp(text)
    
    # Extract different types of information
    extracted_info = {
        "skills": extract_skills(doc),
        "technical_terms": extract_technical_terms(doc),
        "requirements": extract_requirements(doc),
        "keywords": extract_keywords_yake(text, kw_extractor),
        "important_phrases": extract_important_phrases(doc)
    }
    
    return extracted_info

def extract_skills(doc) -> List[str]:
    """
    Extract technical skills and abilities
    """
    skill_patterns = [
        "Python", "Java", "JavaScript", "SQL", "AWS", "Azure",
        "machine learning", "data analysis", "project management",
        "agile", "scrum", "leadership"
    ]
    
    skills = []
    for token in doc:
        if token.text.lower() in [p.lower() for p in skill_patterns]:
            skills.append(token.text)
    
    return list(set(skills))

def extract_technical_terms(doc) -> List[str]:
    """
    Extract technical terminology and tools
    """
    technical_terms = []
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT"]:
            technical_terms.append(ent.text)
    
    return list(set(technical_terms))

def extract_requirements(doc) -> List[str]:
    """
    Extract job requirements and qualifications
    """
    requirement_indicators = [
        "required", "must have", "minimum", "qualification",
        "experience in", "knowledge of", "familiarity with"
    ]
    
    requirements = []
    for sent in doc.sents:
        for indicator in requirement_indicators:
            if indicator in sent.text.lower():
                requirements.append(sent.text.strip())
                break
    
    return requirements

def extract_keywords_yake(text: str, extractor) -> List[str]:
    """
    Extract keywords using YAKE
    """
    keywords = extractor.extract_keywords(text)
    return [kw[0] for kw in keywords]

def extract_important_phrases(doc) -> List[str]:
    """
    Extract important phrases using noun chunks and entity recognition
    """
    important_phrases = []
    
    # Add noun chunks
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) > 1:  # Only phrases, not single words
            important_phrases.append(chunk.text)
    
    # Add named entities
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "GPE", "NORP"]:
            important_phrases.append(ent.text)
    
    return list(set(important_phrases))

def calculate_keyword_importance(text: str, keywords: List[str]) -> Dict[str, float]:
    """
    Calculate importance scores for keywords using TF-IDF
    """
    vectorizer = TfidfVectorizer(
        stop_words=stopwords.words('english'),
        ngram_range=(1, 3)
    )
    
    # Fit vectorizer on text
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    
    # Calculate scores for keywords
    keyword_scores = {}
    for keyword in keywords:
        if keyword in feature_names:
            idx = feature_names.tolist().index(keyword)
            score = tfidf_matrix[0, idx]
            keyword_scores[keyword] = float(score)
    
    return keyword_scores