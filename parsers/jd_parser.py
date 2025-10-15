from pdfminer.high_level import extract_text
import re

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text.strip()

def extract_job_title(text):
    lines = text.split('\n')
    
    job_keywords = [
        'developer', 'engineer', 'manager', 'analyst', 'designer', 'architect', 'lead', 
        'senior', 'junior', 'intern', 'internship', 'associate', 'specialist', 'coordinator',
        'consultant', 'officer', 'executive', 'administrator', 'technician', 'operator',
        'supervisor', 'director', 'head', 'chief', 'assistant', 'trainee', 'expert',
        'scientist', 'researcher', 'programmer', 'administrator', 'operations', 'support'
    ]
    
    for line in lines[:15]:
        line = line.strip()
        if line and 10 < len(line) < 100: 
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in job_keywords):
                if not any(exclude in line_lower for exclude in ['qualification', 'requirement', 'skill', 'description', 'about', 'overview']):
                    return line
    
    for line in lines[:15]:
        line = line.strip()
        if line and 10 < len(line) < 100:
            if re.search(r'\b(Intern|Engineer|Developer|Manager|Analyst|Specialist|Officer|Coordinator|Associate|Executive|Consultant)\b', line, re.IGNORECASE):
                return line
    
    for line in lines[:20]:
        match = re.search(r'(?:Position|Role|Title|Job)\s*:\s*(.+)', line, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            if 5 < len(title) < 100:
                return title
    
    return "Not specified"

def extract_required_skills(text):
    skill_keywords = [
        'python', 'java', 'javascript', 'react', 'node.js', 'nodejs', 'angular', 'vue',
        'mongodb', 'sql', 'postgresql', 'mysql', 'redis', 'docker', 'kubernetes',
        'aws', 'azure', 'gcp', 'git', 'html', 'css', 'typescript', 'c++', 'c#',
        'django', 'flask', 'fastapi', 'spring', 'express', 'rest', 'api', 'graphql',
        'machine learning', 'deep learning', 'ai', 'nlp', 'tensorflow', 'pytorch',
        'pandas', 'numpy', 'scikit-learn', 'data analysis', 'excel', 'powerbi',
        'agile', 'scrum', 'jira', 'ci/cd', 'jenkins', 'linux', 'bash', 'shell',
        'elasticsearch', 'kafka', 'rabbitmq', 'microservices', 'oauth', 'jwt'
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in skill_keywords:
        if skill in text_lower:
            found_skills.append(skill.title())
    
    return list(set(found_skills))

def extract_experience_required(text):
    exp_pattern = r'(\d+)\+?\s*(?:to|\-)\s*(\d+)\s*(?:years?|yrs?)'
    match = re.search(exp_pattern, text.lower())
    
    if match:
        return f"{match.group(1)}-{match.group(2)} years"
    
    single_exp_pattern = r'(\d+)\+?\s*(?:years?|yrs?)'
    match = re.search(single_exp_pattern, text.lower())
    
    if match:
        return f"{match.group(1)}+ years"
    
    return "Not specified"

def extract_qualifications(text):
    education_keywords = ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'mba', 'degree', 'diploma']
    lines = text.split('\n')
    
    qualifications = []
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in education_keywords):
            qualifications.append(clean_text(line[:100]))
            if len(qualifications) >= 2:
                break
    
    return qualifications if qualifications else ["Not specified"]

def extract_responsibilities(text):
    responsibilities = []
    lines = text.split('\n')
    
    in_responsibilities = False
    for line in lines:
        line_lower = line.lower()
        
        if 'responsibilit' in line_lower or 'duties' in line_lower or 'role' in line_lower:
            in_responsibilities = True
            continue
        
        if in_responsibilities and line.strip():
            if line.strip().startswith('-') or line.strip().startswith('•'):
                resp = re.sub(r'^[-•]\s*', '', line.strip())
                responsibilities.append(resp[:100])
            elif len(line.strip()) > 20:
                responsibilities.append(line.strip()[:100])
            
            if len(responsibilities) >= 5:
                break
    
    return responsibilities[:5]

def extract_company_name(text):
    lines = text.split('\n')
    
    for line in lines[:20]:
        match = re.search(r'(?:Company|Organization|Employer)\s*:\s*(.+)', line, re.IGNORECASE)
        if match:
            company = match.group(1).strip()
            if 2 < len(company) < 80:
                return company
    
    for line in lines[:15]:
        line_stripped = line.strip()
        if re.search(r'\b(?:Inc|Ltd|LLC|Corp|Corporation|Company|Technologies|Solutions|Systems|Services|Group|Pvt|Private Limited)\b', line_stripped):
            if 5 < len(line_stripped) < 80:
                return line_stripped[:50]
    
    for line in lines[:10]:
        line_stripped = line.strip()
        if line_stripped and line_stripped[0].isupper() and 3 < len(line_stripped) < 50:
            if not any(keyword in line_stripped.lower() for keyword in ['job', 'position', 'role', 'description', 'qualification', 'requirement', 'intern', 'engineer', 'developer', 'manager']):
                return line_stripped
    
    return "Not specified"

def extract_location(text):
    location_pattern = r'\b(?:Remote|Hybrid|On-site|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2})\b'
    match = re.search(location_pattern, text)
    return match.group(0) if match else "Not specified"

def extract_jd_data(file_path):
    text = extract_text(file_path)
    
    return {
        "job_title": extract_job_title(text),
        "company": extract_company_name(text),
        "location": extract_location(text),
        "required_skills": extract_required_skills(text),
        "experience_required": extract_experience_required(text),
        "qualifications": extract_qualifications(text),
        "responsibilities": extract_responsibilities(text),
        "raw_text": text[:500]
    }
