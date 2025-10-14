import google.generativeai as genai
import json
import re
import os
from datetime import datetime
from pathlib import Path

def ensure_log_directory():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    return log_dir / "score.log"

def log_api_call(message):
    log_file = ensure_log_directory()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def check_gemini_configured():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log_api_call("ERROR: GEMINI_API_KEY not found")
        raise ValueError("Gemini API key not configured")
    return True

def get_match_score(resume_data, jd_data):
    try:
        check_gemini_configured()
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""Compare the following resume and job description. Rate the candidate's fit from 1-10 and justify briefly.
Return in JSON format: {{"score": <number>, "justification": "<text>"}}

Resume:
Name: {resume_data.get('name', 'N/A')}
Skills: {', '.join(resume_data.get('skills', []))}
Education: {resume_data.get('education', 'N/A')}
Experience: {resume_data.get('experience', 'N/A')}
Projects: {', '.join(resume_data.get('projects', []))}

Job Description:
Title: {jd_data.get('job_title', 'N/A')}
Required Skills: {', '.join(jd_data.get('required_skills', []))}
Experience Required: {jd_data.get('experience_required', 'N/A')}
Qualifications: {', '.join(jd_data.get('qualifications', []))}"""

        log_api_call(f"Calling Gemini API for match score - Candidate: {resume_data.get('name', 'Unknown')}")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        json_match = re.search(r'\{[^}]+\}', response_text)
        if json_match:
            result = json.loads(json_match.group())
            score = float(result.get('score', 0))
            justification = result.get('justification', 'No justification provided')
        else:
            score_match = re.search(r'(\d+\.?\d*)\s*(?:/\s*10)?', response_text)
            score = float(score_match.group(1)) if score_match else 5.0
            justification = response_text[:200]
        
        log_api_call(f"Match score generated: {score}/10")
        return {
            "score": min(max(score, 0), 10),
            "justification": justification
        }
    
    except Exception as e:
        log_api_call(f"ERROR in get_match_score: {str(e)}")
        return {
            "score": 0,
            "justification": f"Error generating match score: {str(e)}"
        }

def get_detailed_score(resume_data, jd_data):
    try:
        check_gemini_configured()
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""Compare candidate resume details with the job description and rate:
- Skill Match (1-10)
- Experience Relevance (1-10)
- Education Fit (1-10)
- Overall Fit (1-10)

Provide a short justification for each rating.

Resume:
Name: {resume_data.get('name', 'N/A')}
Skills: {', '.join(resume_data.get('skills', []))}
Education: {resume_data.get('education', 'N/A')}
Experience: {resume_data.get('experience', 'N/A')}
Projects: {', '.join(resume_data.get('projects', []))}

Job Description:
Title: {jd_data.get('job_title', 'N/A')}
Required Skills: {', '.join(jd_data.get('required_skills', []))}
Experience Required: {jd_data.get('experience_required', 'N/A')}
Qualifications: {', '.join(jd_data.get('qualifications', []))}
Responsibilities: {', '.join(jd_data.get('responsibilities', [])[:3])}

Return as JSON:
{{
  "skills_match": <number>,
  "experience_relevance": <number>,
  "education_fit": <number>,
  "overall_fit": <number>,
  "justification": "<detailed text>"
}}"""

        log_api_call(f"Calling Gemini API for detailed score - Candidate: {resume_data.get('name', 'Unknown')}")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            
            skills_match = float(result.get('skills_match', 5))
            experience_relevance = float(result.get('experience_relevance', 5))
            education_fit = float(result.get('education_fit', 5))
            overall_fit = float(result.get('overall_fit', 5))
            justification = result.get('justification', 'No justification provided')
        else:
            skills_match = 5.0
            experience_relevance = 5.0
            education_fit = 5.0
            overall_fit = 5.0
            justification = response_text[:300]
        
        result = {
            "skills_match": min(max(skills_match, 0), 10),
            "experience_relevance": min(max(experience_relevance, 0), 10),
            "education_fit": min(max(education_fit, 0), 10),
            "overall_fit": min(max(overall_fit, 0), 10),
            "justification": justification
        }
        
        log_api_call(f"Detailed score generated - Overall: {result['overall_fit']}/10")
        return result
    
    except Exception as e:
        log_api_call(f"ERROR in get_detailed_score: {str(e)}")
        return {
            "skills_match": 0,
            "experience_relevance": 0,
            "education_fit": 0,
            "overall_fit": 0,
            "justification": f"Error generating detailed score: {str(e)}"
        }

def get_detailed_analysis(resume_data, jd_data):
    try:
        check_gemini_configured()
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""Analyze this candidate's fit for the job role. Provide:
1. Strengths (what matches well)
2. Gaps (what's missing)
3. Overall recommendation

Resume: {json.dumps(resume_data, indent=2)}
Job Description: {json.dumps(jd_data, indent=2)}"""

        log_api_call(f"Calling Gemini API for detailed analysis - Candidate: {resume_data.get('name', 'Unknown')}")
        response = model.generate_content(prompt)
        log_api_call("Detailed analysis generated successfully")
        return response.text.strip()
    
    except Exception as e:
        log_api_call(f"ERROR in get_detailed_analysis: {str(e)}")
        return f"Error generating analysis: {str(e)}"
