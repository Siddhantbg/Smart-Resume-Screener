from pdfminer.high_level import extract_text
import re

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text.strip()

def extract_name(text):
    lines = text.split('\n')
    for line in lines[:5]:
        line = line.strip()
        if len(line) > 0 and len(line.split()) <= 4 and not any(char.isdigit() for char in line):
            if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', line):
                return line
    return "Unknown"

def extract_email(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None

def extract_phone(text):
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else None

def extract_skills(text):
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

def extract_education(text):
    education_keywords = ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'mba', 'bca', 'mca', 'b.e', 'm.e']
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in education_keywords):
            education_info = line.strip()
            if i + 1 < len(lines):
                education_info += ' ' + lines[i + 1].strip()
            return clean_text(education_info)
    
    return "Not specified"

def extract_experience(text):
    exp_pattern = r'(\d+)\+?\s*(years?|yrs?)'
    match = re.search(exp_pattern, text.lower())
    
    if match:
        return f"{match.group(1)} years"
    
    exp_keywords = ['experience', 'worked', 'developer', 'engineer']
    lines = text.split('\n')
    
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in exp_keywords):
            return clean_text(line[:100])
    
    return "Fresher"

def extract_projects(text):
    projects = []
    lines = text.split('\n')
    
    in_project_section = False
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        if 'project' in line_lower and len(line.strip()) < 30:
            in_project_section = True
            continue
        
        if in_project_section and line.strip():
            if line.strip().startswith('-') or line.strip().startswith('•'):
                project_name = re.sub(r'^[-•]\s*', '', line.strip())
                projects.append(project_name[:50])
            elif len(line.strip()) < 50 and not any(char.isdigit() for char in line[:3]):
                projects.append(line.strip())
            
            if len(projects) >= 5:
                break
    
    return projects[:5]

def extract_resume_data(file_path):
    text = extract_text(file_path)
    
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "projects": extract_projects(text),
        "raw_text": text[:500]
    }
