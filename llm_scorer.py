import google.generativeai as genai
import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

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
        log_api_call("WARNING: GEMINI_API_KEY not found - using logic-based scoring only")
        return False
    return True

def infer_seniority_level(jd_data: Dict[str, Any]) -> Tuple[str, float, float, float]:
    """
    Infer seniority level from job description and return appropriate weights.
    
    Returns:
        Tuple of (level, skill_weight, experience_weight, education_weight)
    """
    jd_text = " ".join([
        str(jd_data.get('job_title', '')),
        str(jd_data.get('experience_required', '')),
        " ".join(jd_data.get('responsibilities', [])),
        " ".join(jd_data.get('qualifications', []))
    ]).lower()
    
    entry_keywords = ['intern', 'internship', 'entry', 'junior', 'graduate', 'trainee', 'fresher', '0-1 year', '0 year']
    mid_keywords = ['mid', 'intermediate', '2-4 year', '3-5 year', 'associate']
    senior_keywords = ['senior', 'lead', 'principal', 'staff', 'architect', 'head', '5+ year', '7+ year', '10+ year']
    
    entry_score = sum(1 for kw in entry_keywords if kw in jd_text)
    mid_score = sum(1 for kw in mid_keywords if kw in jd_text)
    senior_score = sum(1 for kw in senior_keywords if kw in jd_text)
    
    if senior_score > max(entry_score, mid_score):
        return 'senior', 0.40, 0.45, 0.15
    elif entry_score > max(mid_score, senior_score):
        return 'entry', 0.60, 0.15, 0.25
    elif mid_score > 0:
        return 'mid', 0.50, 0.30, 0.20
    else:
        return 'mid', 0.50, 0.30, 0.20

def extract_critical_skills(jd_data: Dict[str, Any]) -> List[str]:
    """Extract critical/must-have skills from job description."""
    required_skills = jd_data.get('required_skills', [])
    
    critical_indicators = ['required', 'must', 'essential', 'mandatory', 'proficient', 'expert']
    jd_text = " ".join([
        str(jd_data.get('job_title', '')),
        " ".join(jd_data.get('responsibilities', [])),
        " ".join(jd_data.get('qualifications', []))
    ]).lower()
    
    critical_skills = []
    for skill in required_skills[:5]:
        skill_lower = skill.lower()
        if any(indicator in jd_text and skill_lower in jd_text for indicator in critical_indicators):
            critical_skills.append(skill)
    
    if not critical_skills and required_skills:
        critical_skills = required_skills[:3]
    
    return critical_skills

def calculate_skill_match_score(resume_data: Dict[str, Any], jd_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate skill match with detailed breakdown.
    
    Returns:
        Tuple of (score, details_dict)
    """
    resume_skills = [s.lower().strip() for s in resume_data.get('skills', [])]
    required_skills = [s.lower().strip() for s in jd_data.get('required_skills', [])]
    critical_skills = [s.lower().strip() for s in extract_critical_skills(jd_data)]
    
    if not required_skills:
        return 5.0, {'matched': [], 'missing': [], 'critical_missing': []}
    
    matched_skills = [skill for skill in required_skills if skill in resume_skills]
    missing_skills = [skill for skill in required_skills if skill not in resume_skills]
    critical_missing = [skill for skill in critical_skills if skill not in resume_skills]
    
    match_ratio = len(matched_skills) / len(required_skills) if required_skills else 0
    critical_penalty = 0.2 * len(critical_missing)
    
    score = max(0, min(10, (match_ratio * 10) - critical_penalty))
    
    details = {
        'matched': matched_skills[:10],
        'missing': missing_skills[:10],
        'critical_missing': critical_missing,
        'match_ratio': round(match_ratio * 100, 1)
    }
    
    return score, details

def calculate_experience_score(resume_data: Dict[str, Any], jd_data: Dict[str, Any], seniority: str) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate experience relevance score based on seniority level.
    
    Returns:
        Tuple of (score, details_dict)
    """
    experience_text = str(resume_data.get('experience', '')).lower()
    required_exp = str(jd_data.get('experience_required', '')).lower()
    
    year_pattern = r'(\d+)[\s+-]*(?:to|-)?\s*(\d+)?\s*(?:year|yr)'
    resume_years_match = re.findall(year_pattern, experience_text)
    required_years_match = re.findall(year_pattern, required_exp)
    
    resume_years = 0
    if resume_years_match:
        years = resume_years_match[0]
        resume_years = max(int(years[0]), int(years[1]) if years[1] else 0)
    
    required_years = 0
    if required_years_match:
        years = required_years_match[0]
        required_years = int(years[0])
    
    if 'intern' in experience_text or 'internship' in experience_text:
        has_internship = True
    else:
        has_internship = False
    
    if seniority == 'entry':
        if has_internship or resume_years >= 0:
            score = min(10, 7 + resume_years * 1.5)
        else:
            score = 6.0
    elif seniority == 'senior':
        if required_years > 0:
            if resume_years >= required_years:
                score = 10.0
            elif resume_years >= required_years * 0.7:
                score = 8.0
            elif resume_years >= required_years * 0.5:
                score = 6.0
            else:
                score = max(3.0, resume_years * 1.5)
        else:
            score = min(10, resume_years * 1.5)
    else:
        if required_years > 0:
            ratio = resume_years / required_years if required_years > 0 else 1
            score = min(10, ratio * 8)
        else:
            score = min(10, 5 + resume_years)
    
    details = {
        'resume_years': resume_years,
        'required_years': required_years,
        'has_internship': has_internship,
        'seniority_level': seniority
    }
    
    return score, details

def extract_marks_with_gemini(education_text: str) -> Tuple[float, str]:
    """Use Gemini to extract academic marks if regex fails."""
    try:
        if not check_gemini_configured():
            return None, None
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""Extract the HIGHEST academic performance score from this education text.

Education text: {education_text}

Return ONLY a single line in this exact format:
TYPE: VALUE

Where TYPE is either "CGPA" or "PERCENTAGE" and VALUE is the numeric score.
Examples:
- CGPA: 9.2
- PERCENTAGE: 92.5

If no score found, return: NONE"""
        
        response = model.generate_content(prompt)
        result = response.text.strip()
        
        if 'CGPA:' in result:
            value = float(result.split('CGPA:')[1].strip())
            return value, 'CGPA'
        elif 'PERCENTAGE:' in result:
            value = float(result.split('PERCENTAGE:')[1].strip())
            return value, 'PERCENTAGE'
        
        return None, None
        
    except Exception as e:
        log_api_call(f"Gemini marks extraction failed: {e}")
        return None, None

def calculate_education_score(resume_data: Dict[str, Any], jd_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate education fit score with fine-grained academic performance differentiation.
    
    Returns:
        Tuple of (score, details_dict)
    """
    education = str(resume_data.get('education', 'Not specified'))
    qualifications = [q.lower() for q in jd_data.get('qualifications', [])]
    
    if education == 'Not specified' or education.lower() == 'unknown':
        return 4.0, {'reason': 'Education not specified', 'academic_performance': 0, 'has_tech_degree': False, 'degree_level': 'Unknown'}
    
    education_lower = education.lower()
    
    # Extract CGPA or percentage with improved patterns
    cgpa_patterns = [
        r'cgpa[\s:=\-]*(\d+\.?\d*)\s*/?\s*(?:10|4)',
        r'cgpa[\s:=\-]*(\d+\.?\d*)',
        r'gpa[\s:=\-]*(\d+\.?\d*)\s*/?\s*(?:10|4)',
        r'gpa[\s:=\-]*(\d+\.?\d*)',
        r'aggregate[\s:=\-]*(\d+\.?\d*)\s*cgpa',
        r'overall[\s:=\-]*(\d+\.?\d*)\s*cgpa'
    ]
    
    percentage_patterns = [
        r'(\d{2,3}\.\d+)\s*%',
        r'(\d{2,3})\.(\d+)\s*%',
        r'(\d{2,3})\s*%',
        r'percentage[\s:=\-]*(\d{2,3}\.?\d*)',
        r'marks[\s:=\-]*(\d{2,3}\.?\d*)',
        r'aggregate[\s:=\-]*(\d{2,3}\.?\d*)\s*%',
        r'overall[\s:=\-]*(\d{2,3}\.?\d*)\s*%'
    ]
    
    academic_score = 5.0  # default
    academic_value = None
    academic_type = None
    
    # Try to extract CGPA first
    for pattern in cgpa_patterns:
        cgpa_match = re.search(pattern, education_lower)
        if cgpa_match:
            cgpa = float(cgpa_match.group(1))
            # Normalize if CGPA is out of 4 or other scale
            if cgpa <= 4.5:
                cgpa = (cgpa / 4.0) * 10.0
            elif cgpa > 10:
                cgpa = 10.0
            
            academic_value = cgpa
            academic_type = 'CGPA'
            
            # Fine-grained scoring with 0.1 precision
            if cgpa >= 9.5:
                academic_score = 10.0
            elif cgpa >= 9.0:
                academic_score = 9.5
            elif cgpa >= 8.5:
                academic_score = 9.0
            elif cgpa >= 8.0:
                academic_score = 8.5
            elif cgpa >= 7.5:
                academic_score = 7.8
            elif cgpa >= 7.0:
                academic_score = 7.2
            elif cgpa >= 6.5:
                academic_score = 6.5
            elif cgpa >= 6.0:
                academic_score = 5.8
            elif cgpa >= 5.5:
                academic_score = 5.0
            else:
                academic_score = max(3.0, cgpa * 0.8)
            break
    
    # Try percentage if CGPA not found
    if not academic_value:
        for pattern in percentage_patterns:
            percentage_match = re.search(pattern, education_lower)
            if percentage_match:
                if len(percentage_match.groups()) > 1 and percentage_match.group(2):
                    percentage = float(f"{percentage_match.group(1)}.{percentage_match.group(2)}")
                else:
                    percentage = float(percentage_match.group(1))
                
                academic_value = percentage
                academic_type = 'Percentage'
                
                # Fine-grained scoring
                if percentage >= 95:
                    academic_score = 10.0
                elif percentage >= 90:
                    academic_score = 9.5
                elif percentage >= 85:
                    academic_score = 9.0
                elif percentage >= 80:
                    academic_score = 8.5
                elif percentage >= 75:
                    academic_score = 7.8
                elif percentage >= 70:
                    academic_score = 7.0
                elif percentage >= 65:
                    academic_score = 6.2
                elif percentage >= 60:
                    academic_score = 5.5
                elif percentage >= 55:
                    academic_score = 4.8
                else:
                    academic_score = max(3.0, percentage / 15.0)
                break
    
    # If still no academic value found, try Gemini as last resort
    if not academic_value:
        log_api_call(f"Regex failed to extract marks, trying Gemini for: {education[:100]}")
        gemini_value, gemini_type = extract_marks_with_gemini(education)
        
        if gemini_value and gemini_type:
            if gemini_type == 'CGPA':
                cgpa = gemini_value
                if cgpa <= 4.5:
                    cgpa = (cgpa / 4.0) * 10.0
                elif cgpa > 10:
                    cgpa = 10.0
                
                academic_value = cgpa
                academic_type = 'CGPA (Gemini)'
                
                if cgpa >= 9.5:
                    academic_score = 10.0
                elif cgpa >= 9.0:
                    academic_score = 9.5
                elif cgpa >= 8.5:
                    academic_score = 9.0
                elif cgpa >= 8.0:
                    academic_score = 8.5
                elif cgpa >= 7.5:
                    academic_score = 7.8
                elif cgpa >= 7.0:
                    academic_score = 7.2
                elif cgpa >= 6.5:
                    academic_score = 6.5
                elif cgpa >= 6.0:
                    academic_score = 5.8
                elif cgpa >= 5.5:
                    academic_score = 5.0
                else:
                    academic_score = max(3.0, cgpa * 0.8)
                    
            elif gemini_type == 'PERCENTAGE':
                percentage = gemini_value
                academic_value = percentage
                academic_type = 'Percentage (Gemini)'
                
                if percentage >= 95:
                    academic_score = 10.0
                elif percentage >= 90:
                    academic_score = 9.5
                elif percentage >= 85:
                    academic_score = 9.0
                elif percentage >= 80:
                    academic_score = 8.5
                elif percentage >= 75:
                    academic_score = 7.8
                elif percentage >= 70:
                    academic_score = 7.0
                elif percentage >= 65:
                    academic_score = 6.2
                elif percentage >= 60:
                    academic_score = 5.5
                elif percentage >= 55:
                    academic_score = 4.8
                else:
                    academic_score = max(3.0, percentage / 15.0)
            
            log_api_call(f"Gemini extracted: {gemini_type} = {gemini_value}, score = {academic_score}")
    
    # Field relevance
    tech_degrees = ['computer', 'software', 'information technology', 'it ', 'engineering', 'cs ', 'computer science', 'cse', 'ece', 'electrical']
    has_tech_degree = any(degree in education_lower for degree in tech_degrees)
    
    # Degree level
    has_bachelors = any(deg in education_lower for deg in ['bachelor', 'b.tech', 'b.e.', 'btech', 'be ', 'b.sc', 'bca'])
    has_masters = any(deg in education_lower for deg in ['master', 'm.tech', 'm.e.', 'mtech', 'me ', 'm.sc', 'mca', 'ms '])
    has_phd = 'phd' in education_lower or 'doctorate' in education_lower
    
    # Degree multiplier with finer gradations
    if has_phd:
        degree_multiplier = 1.4
    elif has_masters:
        degree_multiplier = 1.3
    elif has_bachelors:
        degree_multiplier = 1.0
    else:
        degree_multiplier = 0.6
    
    # Field multiplier
    field_multiplier = 1.0 if has_tech_degree else 0.75
    
    # Combine with multiplicative scaling
    final_score = min(10.0, academic_score * field_multiplier * degree_multiplier / 1.2)
    
    details = {
        'academic_performance': round(academic_score, 2),
        'academic_value': academic_value,
        'academic_type': academic_type,
        'has_tech_degree': has_tech_degree,
        'degree_level': 'PhD' if has_phd else 'Masters' if has_masters else 'Bachelors' if has_bachelors else 'Other',
        'education_text': education[:150]
    }
    
    return final_score, details

def compute_weighted_score(
    skill_score: float,
    experience_score: float,
    education_score: float,
    skill_weight: float,
    exp_weight: float,
    edu_weight: float
) -> float:
    """Compute final weighted score."""
    return (
        skill_score * skill_weight +
        experience_score * exp_weight +
        education_score * edu_weight
    )

def generate_justification(
    resume_data: Dict[str, Any],
    jd_data: Dict[str, Any],
    scores: Dict[str, Any],
    seniority: str,
    is_shortlisted: bool
) -> str:
    """Generate human-readable justification for the scoring decision."""
    
    name = resume_data.get('name', 'Candidate')
    job_title = jd_data.get('job_title', 'this position')
    
    skill_details = scores['skill_details']
    exp_details = scores['experience_details']
    edu_details = scores['education_details']
    
    # Build natural paragraph-style analysis
    paragraphs = []
    
    # Opening statement with context
    if is_shortlisted:
        opening = f"{name} has been shortlisted for the {job_title} position. "
    else:
        opening = f"{name} does not meet the minimum requirements for the {job_title} role. "
    
    opening += f"This is an {seniority.lower()} level position, and the candidate achieved an overall score of {scores['overall_fit']:.2f} out of 10. "
    
    # Skills assessment
    if skill_details['matched']:
        opening += f"In terms of skills, the candidate demonstrates proficiency in {', '.join(skill_details['matched'][:5])}"
        if len(skill_details['matched']) > 5:
            opening += f" and {len(skill_details['matched']) - 5} additional skills"
        opening += f", achieving a {skill_details['match_ratio']}% match ratio with a skills score of {scores['skills_match']:.2f}/10. "
    else:
        opening += f"The candidate shows limited skill alignment with only a {skill_details['match_ratio']}% match ratio, resulting in a skills score of {scores['skills_match']:.2f}/10. "
    
    if skill_details['critical_missing']:
        opening += f"However, there are critical gaps in essential skills such as {', '.join(skill_details['critical_missing'])}. "
    elif skill_details['missing']:
        opening += f"Some desirable skills that could strengthen the profile include {', '.join(skill_details['missing'][:3])}. "
    
    paragraphs.append(opening.strip())
    
    # Experience and education in second paragraph
    second_para = ""
    
    # Experience
    exp_details_list = []
    if exp_details['resume_years'] > 0:
        exp_details_list.append(f"{exp_details['resume_years']} years of relevant experience")
    if exp_details['has_internship']:
        exp_details_list.append("internship background")
    
    if exp_details_list:
        second_para += f"Regarding work experience, the candidate brings {' and '.join(exp_details_list)}"
    else:
        second_para += f"The candidate has limited documented work experience"
    
    if exp_details['required_years'] > 0:
        second_para += f", while the role requires {exp_details['required_years']}+ years"
    
    second_para += f", earning an experience score of {scores['experience_relevance']:.2f}/10. "
    
    # Education
    second_para += f"On the educational front, the candidate holds a {edu_details.get('degree_level', 'degree').lower()}"
    
    if edu_details.get('has_tech_degree'):
        second_para += " in a technical field such as Computer Science, IT, or Engineering"
    
    second_para += ". "
    
    if edu_details.get('academic_performance', 0) >= 8:
        second_para += f"Academic performance is strong with excellent grades, reflected in an education score of {scores['education_fit']:.2f}/10. "
    elif edu_details.get('academic_performance', 0) > 0:
        second_para += f"Academic performance is moderate, reflected in an education score of {scores['education_fit']:.2f}/10. "
    else:
        second_para += f"The education score is {scores['education_fit']:.2f}/10. "
    
    paragraphs.append(second_para.strip())
    
    # Rejection reasons as final paragraph
    if not is_shortlisted:
        rejection_reasons = []
        if scores['overall_fit'] < 6.5:
            rejection_reasons.append("the overall fit score falls below the acceptance threshold")
        if skill_details['critical_missing']:
            rejection_reasons.append(f"critical skills are missing, specifically {', '.join(skill_details['critical_missing'])}")
        if seniority == 'senior' and scores['experience_relevance'] < 5.0:
            rejection_reasons.append("the experience level is insufficient for a senior-level role")
        
        if rejection_reasons:
            conclusion = "The candidate was not shortlisted because "
            if len(rejection_reasons) == 1:
                conclusion += rejection_reasons[0] + "."
            elif len(rejection_reasons) == 2:
                conclusion += rejection_reasons[0] + " and " + rejection_reasons[1] + "."
            else:
                conclusion += ", ".join(rejection_reasons[:-1]) + ", and " + rejection_reasons[-1] + "."
            paragraphs.append(conclusion)
    
    return "\n\n".join(paragraphs)

def get_detailed_score(resume_data: Dict[str, Any], jd_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to score candidate with intelligent shortlisting logic.
    
    Returns comprehensive scoring with weighted calculations based on job seniority.
    """
    try:
        has_gemini = check_gemini_configured()
        
        seniority, skill_weight, exp_weight, edu_weight = infer_seniority_level(jd_data)
        
        log_api_call(f"Scoring candidate: {resume_data.get('name', 'Unknown')} for {jd_data.get('job_title', 'Unknown')} ({seniority} level)")
        
        skill_score, skill_details = calculate_skill_match_score(resume_data, jd_data)
        experience_score, exp_details = calculate_experience_score(resume_data, jd_data, seniority)
        education_score, edu_details = calculate_education_score(resume_data, jd_data)
        
        overall_score = compute_weighted_score(
            skill_score, experience_score, education_score,
            skill_weight, exp_weight, edu_weight
        )
        
        # Stricter shortlisting criteria: 7.5+ to be shortlisted
        # Most candidates will be rejected, very few waitlisted
        if overall_score >= 7.5:
            # Only top performers get shortlisted
            is_shortlisted = True  
        elif overall_score >= 7.0:
            # High scorers need no critical skill gaps to be shortlisted
            is_shortlisted = not skill_details['critical_missing']
        else:
            # Everyone below 7.0 is NOT shortlisted (waitlist or reject based on score)
            is_shortlisted = False  

        justification = generate_justification(
            resume_data, jd_data,
            {
                'skills_match': skill_score,
                'experience_relevance': experience_score,
                'education_fit': education_score,
                'overall_fit': overall_score,
                'skill_details': skill_details,
                'experience_details': exp_details,
                'education_details': edu_details
            },
            seniority,
            is_shortlisted
        )
        
        result = {
            'skills_match': round(skill_score, 2),
            'experience_relevance': round(experience_score, 2),
            'education_fit': round(education_score, 2),
            'overall_fit': round(overall_score, 2),
            'justification': justification,
            'is_shortlisted': is_shortlisted,
            'seniority_level': seniority,
            'weights': {
                'skills': skill_weight,
                'experience': exp_weight,
                'education': edu_weight
            },
            'details': {
                'skills': skill_details,
                'experience': exp_details,
                'education': edu_details
            }
        }
        
        log_api_call(f"Score: {overall_score:.1f}/10, Shortlisted: {is_shortlisted}")
        
        return result
    
    except Exception as e:
        log_api_call(f"ERROR in get_detailed_score: {str(e)}")
        return {
            'skills_match': 0,
            'experience_relevance': 0,
            'education_fit': 0,
            'overall_fit': 0,
            'justification': f"Error: {str(e)}",
            'is_shortlisted': False,
            'seniority_level': 'unknown',
            'weights': {'skills': 0.5, 'experience': 0.3, 'education': 0.2},
            'details': {}
        }

def get_match_score(resume_data: Dict[str, Any], jd_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Backward compatibility wrapper for simple match scoring.
    """
    detailed_score = get_detailed_score(resume_data, jd_data)
    return {
        'score': detailed_score['overall_fit'],
        'justification': detailed_score['justification']
    }

def get_detailed_analysis(resume_data: Dict[str, Any], jd_data: Dict[str, Any]) -> str:
    """
    Generate detailed analysis using Gemini for additional insights.
    """
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
