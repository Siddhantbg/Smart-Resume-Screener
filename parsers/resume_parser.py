from pdfminer.high_level import extract_text
import re
import os
import google.generativeai as genai

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text.strip()

def extract_name(text):
    lines = text.split('\n')
    
    for line in lines[:10]:  
        line = line.strip()
        
        if not line or '@' in line or 'http' in line.lower() or 'www' in line.lower():
            continue
        
        if any(char.isdigit() for char in line):
            continue
            
        skip_words = ['resume', 'curriculum', 'vitae', 'cv', 'profile', 'summary', 'objective', 
                      'education', 'experience', 'skills', 'projects', 'contact', 'software', 
                      'engineer', 'developer', 'analyst', 'intern', 'internship', 'manager']
        if any(word in line.lower() for word in skip_words):
            continue
        
        words = line.split()
        if 2 <= len(words) <= 5: 
            
            if all(word[0].isupper() or word.isupper() for word in words if len(word) > 0):
                letter_count = sum(c.isalpha() or c.isspace() for c in line)
                if letter_count / len(line) > 0.8:  # At least 80% letters/spaces
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
    education_keywords = [
        'bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'mba', 'bca', 'mca', 
        'b.e', 'm.e', 'b.sc', 'm.sc', 'btech', 'mtech', 'undergraduate', 'graduate',
        'engineering', 'computer science', 'information technology', 'electrical',
        'matriculation', 'intermediate', '10th', '12th', 'icse', 'isc', 'cbse'
    ]
    
    lines = text.split('\n')
    education_blocks = []
    
    # Enhanced grade patterns to catch more formats
    grade_patterns = [
        r'CGPA\s*[\-:=]?\s*(\d+\.?\d*)\s*[/oO]?\s*10',
        r'CGPA\s*[\-:=]?\s*(\d+\.?\d*)',
        r'GPA\s*[\-:=]?\s*(\d+\.?\d*)\s*[/oO]?\s*[14]',
        r'GPA\s*[\-:=]?\s*(\d+\.?\d*)',
        r'(\d{2,3}\.\d+)\s*%',
        r'(\d{2,3})\s*%',
        r'Percentage\s*[\-:=]?\s*(\d{2,3}\.?\d*)',
        r'Marks\s*[\-:=]?\s*(\d{2,3}\.?\d*)',
        r'10th.*?[\-:=]?\s*(\d{2,3}\.?\d*)%?',
        r'12th.*?[\-:=]?\s*(\d{2,3}\.?\d*)%?',
        r'X\s*[\-:=]?\s*(\d{2,3}\.?\d*)%?',
        r'XII\s*[\-:=]?\s*(\d{2,3}\.?\d*)%?',
        r'Aggregate\s*[\-:=]?\s*(\d{2,3}\.?\d*)',
    ]
    
    grades_found = []
    for pattern in grade_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            grades_found.append(match.group(0))
    
    in_education_section = False
    education_lines = []
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        
        if 'education' in line_lower and len(line_stripped) < 30:
            in_education_section = True
            continue
        
        if in_education_section and any(sec in line_lower for sec in ['summary', 'experience', 'project', 'skill', 'achievement', 'certification']) and len(line_stripped) < 30:
            break
        
        if in_education_section and line_stripped:
            education_lines.append(line_stripped)
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in education_keywords):
            context = []
            for j in range(max(0, i-1), min(len(lines), i+6)):
                if lines[j].strip():
                    context.append(lines[j].strip())
            
            education_block = ' | '.join(context[:8])
            education_blocks.append(education_block)
    
    all_education_parts = []
    
    if education_lines:
        all_education_parts.append(' | '.join(education_lines[:20]))
    
    if education_blocks:
        all_education_parts.extend(education_blocks[:3])
    
    if grades_found:
        all_education_parts.append('Grades: ' + ', '.join(set(grades_found)))
    
    if all_education_parts:
        result = ' || '.join(all_education_parts)
        return clean_text(result)[:800]  # Increased from 500 to capture more context
    
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

def enhance_education_with_gemini(education_text, full_text):
    """Use Gemini to extract additional education details if available."""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return education_text
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""Extract education details from this resume text. Focus on:
1. Degree names (B.Tech, M.Tech, Bachelor's, Master's, etc.)
2. Field of study (Computer Science, IT, Engineering, etc.)
3. CGPA or Percentage scores (be very precise with numbers)
4. University/College names
5. Year of graduation

Return ONLY the extracted information in a concise format. Include ALL CGPA/percentage scores found.

Resume excerpt:
{full_text[:1500]}

Current extracted education: {education_text}

Enhanced education details:"""
        
        response = model.generate_content(prompt)
        enhanced = response.text.strip()
        
        # Combine original and enhanced, keeping both
        if enhanced and len(enhanced) > 20 and enhanced.lower() != 'not specified':
            return f"{education_text} || Gemini Enhanced: {enhanced}"
        
        return education_text
        
    except Exception as e:
        print(f"Gemini enhancement failed: {e}")
        return education_text

def extract_resume_data(file_path):
    text = extract_text(file_path)
    
    education_basic = extract_education(text)
    
    # Try to enhance with Gemini if available
    education_enhanced = enhance_education_with_gemini(education_basic, text)
    
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": education_enhanced,
        "experience": extract_experience(text),
        "projects": extract_projects(text),
        "raw_text": text[:500]
    }
