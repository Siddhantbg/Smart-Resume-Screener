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

def calculate_education_score(resume_data: Dict[str, Any], jd_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate education fit score considering academic performance and field relevance.
    
    Returns:
        Tuple of (score, details_dict)
    """
    education = str(resume_data.get('education', 'Not specified'))
    qualifications = [q.lower() for q in jd_data.get('qualifications', [])]
    
    if education == 'Not specified' or education.lower() == 'unknown':
        return 4.0, {'reason': 'Education not specified'}
    
    education_lower = education.lower()
    
    cgpa_match = re.search(r'cgpa[:\s-]*(\d+\.?\d*)', education_lower)
    percentage_match = re.search(r'(\d{2,3}\.?\d*)%', education_lower)
    
    academic_score = 5.0
    if cgpa_match:
        cgpa = float(cgpa_match.group(1))
        if cgpa >= 9.0:
            academic_score = 10.0
        elif cgpa >= 8.0:
            academic_score = 8.5
        elif cgpa >= 7.0:
            academic_score = 7.0
        elif cgpa >= 6.0:
            academic_score = 5.5
    elif percentage_match:
        percentage = float(percentage_match.group(1))
        if percentage >= 90:
            academic_score = 10.0
        elif percentage >= 80:
            academic_score = 8.5
        elif percentage >= 70:
            academic_score = 7.0
        elif percentage >= 60:
            academic_score = 5.5
    
    tech_degrees = ['computer', 'software', 'information technology', 'it ', 'engineering', 'cs ', 'computer science']
    has_tech_degree = any(degree in education_lower for degree in tech_degrees)
    
    has_bachelors = 'bachelor' in education_lower or 'b.tech' in education_lower or 'b.e.' in education_lower
    has_masters = 'master' in education_lower or 'm.tech' in education_lower or 'm.s.' in education_lower
    
    if has_masters:
        degree_bonus = 1.5
    elif has_bachelors:
        degree_bonus = 1.0
    else:
        degree_bonus = 0.5
    
    field_bonus = 1.0 if has_tech_degree else 0.7
    
    final_score = min(10, academic_score * field_bonus * degree_bonus / 1.5)
    
    details = {
        'academic_performance': round(academic_score, 1),
        'has_tech_degree': has_tech_degree,
        'degree_level': 'Masters' if has_masters else 'Bachelors' if has_bachelors else 'Other',
        'education_text': education[:100]
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
    
    justification_parts = []
    
    if is_shortlisted:
        justification_parts.append(f"**SHORTLISTED** - {name} is a strong fit for {job_title}.")
    else:
        justification_parts.append(f"**NOT SHORTLISTED** - {name} does not meet minimum requirements for {job_title}.")
    
    justification_parts.append(f"\n**Seniority Level:** {seniority.title()}")
    justification_parts.append(f"**Overall Score:** {scores['overall_fit']:.1f}/10")
    
    justification_parts.append(f"\n**Skills Match ({scores['skills_match']:.1f}/10):**")
    if skill_details['matched']:
        justification_parts.append(f"✓ Matched skills: {', '.join(skill_details['matched'][:5])}")
    if skill_details['critical_missing']:
        justification_parts.append(f"✗ Missing critical skills: {', '.join(skill_details['critical_missing'])}")
    elif skill_details['missing']:
        justification_parts.append(f"• Missing: {', '.join(skill_details['missing'][:3])}")
    justification_parts.append(f"• Match ratio: {skill_details['match_ratio']}%")
    
    justification_parts.append(f"\n**Experience ({scores['experience_relevance']:.1f}/10):**")
    if exp_details['resume_years'] > 0:
        justification_parts.append(f"• {exp_details['resume_years']} years of experience")
    if exp_details['has_internship']:
        justification_parts.append(f"• Has internship experience")
    if exp_details['required_years'] > 0:
        justification_parts.append(f"• Required: {exp_details['required_years']}+ years")
    
    justification_parts.append(f"\n**Education ({scores['education_fit']:.1f}/10):**")
    justification_parts.append(f"• {edu_details.get('degree_level', 'Unknown')} degree")
    if edu_details.get('has_tech_degree'):
        justification_parts.append(f"• Technical field (CS/IT/Engineering)")
    if edu_details.get('academic_performance', 0) >= 8:
        justification_parts.append(f"• Strong academic performance ({edu_details['academic_performance']:.1f}/10)")
    
    if not is_shortlisted:
        rejection_reasons = []
        if scores['overall_fit'] < 4.0:
            rejection_reasons.append("Overall fit below minimum threshold (40%)")
        if skill_details['critical_missing']:
            rejection_reasons.append(f"Missing critical skills: {', '.join(skill_details['critical_missing'])}")
        if seniority == 'senior' and scores['experience_relevance'] < 5.0:
            rejection_reasons.append("Insufficient experience for senior role")
        
        if rejection_reasons:
            justification_parts.append(f"\n**Rejection Reasons:**")
            for reason in rejection_reasons:
                justification_parts.append(f"• {reason}")
    
    return "\n".join(justification_parts)

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
        
        # Improved shortlisting logic:
        # - Score >= 7.0 (70%): Auto-shortlist regardless of minor gaps
        # - Score >= 6.0 (60%): Shortlist if no critical missing skills
        # - Score >= 4.0 (40%): Shortlist if no critical missing AND good skill match
        # - Score < 4.0: Auto-reject
        if overall_score >= 7.0:
            is_shortlisted = True  # High performers get auto-shortlisted
        elif overall_score >= 6.0:
            is_shortlisted = not skill_details['critical_missing']  # Good scores need no critical gaps
        elif overall_score >= 4.0:
            # Borderline scores need both no critical gaps AND decent skill match
            is_shortlisted = not skill_details['critical_missing'] and skill_score >= 5.0
        else:
            is_shortlisted = False  # Below threshold = auto-reject
        
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
            'skills_match': round(skill_score, 1),
            'experience_relevance': round(experience_score, 1),
            'education_fit': round(education_score, 1),
            'overall_fit': round(overall_score, 1),
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
