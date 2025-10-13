import google.generativeai as genai
import json
import re
import os

def get_match_score(resume_data, jd_data):
    try:
        model = genai.GenerativeModel('gemini-pro')
        
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
        
        return {
            "score": min(max(score, 0), 10),
            "justification": justification
        }
    
    except Exception as e:
        return {
            "score": 0,
            "justification": f"Error generating match score: {str(e)}"
        }

def get_detailed_analysis(resume_data, jd_data):
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""Analyze this candidate's fit for the job role. Provide:
1. Strengths (what matches well)
2. Gaps (what's missing)
3. Overall recommendation

Resume: {json.dumps(resume_data, indent=2)}
Job Description: {json.dumps(jd_data, indent=2)}"""

        response = model.generate_content(prompt)
        return response.text.strip()
    
    except Exception as e:
        return f"Error generating analysis: {str(e)}"
