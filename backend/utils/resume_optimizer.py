from typing import Dict, List
import json
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms import Anthropic
from llama_index.embeddings import OpenAIEmbedding
import os
from dotenv import load_dotenv

load_dotenv()

class ResumeOptimizer:
    def __init__(self):
        """Initialize the resume optimizer with necessary models and configurations"""
        self.llm = Anthropic(model="claude-3-sonnet-20240229")
        self.embedding_model = OpenAIEmbedding()
        
    def optimize_resume(self, resume_content: Dict, job_keywords: Dict, job_description: str) -> Dict:
        """
        Optimize resume content based on job description and extracted keywords
        
        Args:
            resume_content: Dictionary containing structured resume sections
            job_keywords: Dictionary containing extracted job keywords and requirements
            job_description: Original job description text
        
        Returns:
            Dictionary containing optimized resume content
        """
        optimized_content = resume_content.copy()
        
        # Optimize each section
        optimized_content["summary"] = self._optimize_summary(
            resume_content["summary"],
            job_keywords,
            job_description
        )
        
        optimized_content["experience"] = self._optimize_experience(
            resume_content["experience"],
            job_keywords,
            job_description
        )
        
        optimized_content["skills"] = self._optimize_skills(
            resume_content["skills"],
            job_keywords["skills"],
            job_keywords["technical_terms"]
        )
        
        return optimized_content
    
    def _optimize_summary(self, original_summary: str, job_keywords: Dict, job_description: str) -> str:
        """Optimize the professional summary section"""
        prompt = f"""Task: Optimize this professional summary for the given job description.

Original Summary:
{original_summary}

Job Description:
{job_description}

Key Requirements:
{json.dumps(job_keywords['requirements'], indent=2)}

Important Keywords:
{json.dumps(job_keywords['keywords'], indent=2)}

Instructions:
1. Maintain professionalism and authenticity
2. Incorporate relevant keywords naturally
3. Highlight matching qualifications
4. Keep similar length to original
5. Focus on value proposition
6. Don't fabricate experience

Modified Summary:"""
        
        response = self.llm.complete(prompt)
        return response.text.strip()
    
    def _optimize_experience(self, experiences: List[str], job_keywords: Dict, job_description: str) -> List[str]:
        """Optimize professional experience entries"""
        optimized_experiences = []
        
        for experience in experiences:
            prompt = f"""Task: Optimize this professional experience entry for the given job requirements.

Original Entry:
{experience}

Job Description:
{job_description}

Key Requirements:
{json.dumps(job_keywords['requirements'], indent=2)}

Technical Terms:
{json.dumps(job_keywords['technical_terms'], indent=2)}

Instructions:
1. Maintain factual accuracy
2. Emphasize relevant achievements
3. Incorporate key technical terms naturally
4. Use strong action verbs
5. Quantify achievements where possible
6. Don't fabricate experience

Modified Entry:"""
            
            response = self.llm.complete(prompt)
            optimized_experiences.append(response.text.strip())
        
        return optimized_experiences
    
    def _optimize_skills(self, original_skills: List[str], required_skills: List[str], technical_terms: List[str]) -> List[str]:
        """Optimize skills section"""
        # Combine all skills and remove duplicates
        all_skills = set(original_skills)
        
        # Sort skills by relevance to job requirements
        relevant_skills = []
        other_skills = []
        
        for skill in all_skills:
            if skill in required_skills or skill in technical_terms:
                relevant_skills.append(skill)
            else:
                other_skills.append(skill)
        
        # Combine skills with relevant ones first
        optimized_skills = relevant_skills + other_skills
        
        # Format skills for better presentation
        prompt = f"""Task: Organize and group these skills effectively:

Skills:
{json.dumps(optimized_skills, indent=2)}

Technical Terms from Job:
{json.dumps(technical_terms, indent=2)}

Instructions:
1. Group similar skills together
2. Highlight most relevant skills first
3. Use consistent formatting
4. Remove redundant skills
5. Keep authenticity

Organized Skills:"""
        
        response = self.llm.complete(prompt)
        return [skill.strip() for skill in response.text.strip().split(',')]
    
    def _get_embedding_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts using embeddings"""
        emb1 = self.embedding_model.get_text_embedding(text1)
        emb2 = self.embedding_model.get_text_embedding(text2)
        
        # Calculate cosine similarity
        similarity = sum(a * b for a, b in zip(emb1, emb2))
        norm1 = sum(a * a for a in emb1) ** 0.5
        norm2 = sum(b * b for b in emb2) ** 0.5
        
        return similarity / (norm1 * norm2)

def optimize_resume(resume_text: str, job_keywords: Dict, job_description: str) -> Dict:
    """
    Main function to optimize resume
    
    Args:
        resume_text: JSON string containing structured resume content
        job_keywords: Dictionary containing extracted keywords
        job_description: Original job description text
    
    Returns:
        Dictionary containing optimized resume content
    """
    optimizer = ResumeOptimizer()
    resume_content = json.loads(resume_text)
    
    optimized_content = optimizer.optimize_resume(
        resume_content,
        job_keywords,
        job_description
    )
    
    return optimized_content