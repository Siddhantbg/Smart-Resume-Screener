"""
Test script for the new intelligent scoring system
"""
import sys
sys.path.insert(0, '.')

from llm_scorer import (
    infer_seniority_level,
    calculate_skill_match_score,
    calculate_experience_score,
    calculate_education_score,
    compute_weighted_score,
    get_detailed_score
)

# Test Case 1: Entry-Level Position
print("=" * 80)
print("TEST 1: Entry-Level Junior Developer")
print("=" * 80)

jd_entry = {
    'job_title': 'Junior Software Developer',
    'experience_required': '0-1 years',
    'required_skills': ['Python', 'JavaScript', 'React', 'HTML', 'CSS'],
    'qualifications': ['Bachelor in Computer Science'],
    'responsibilities': ['Write clean code', 'Learn new technologies']
}

resume_entry = {
    'name': 'John Doe',
    'skills': ['Python', 'JavaScript', 'React', 'HTML', 'CSS', 'Git'],
    'experience': '6 months internship at Tech Company',
    'education': 'B.Tech in Computer Science, CGPA: 8.5/10'
}

result1 = get_detailed_score(resume_entry, jd_entry)
print(f"\nCandidate: {resume_entry['name']}")
print(f"Seniority Detected: {result1['seniority_level']}")
print(f"Skills Match: {result1['skills_match']}/10")
print(f"Experience: {result1['experience_relevance']}/10")
print(f"Education: {result1['education_fit']}/10")
print(f"Overall Score: {result1['overall_fit']}/10")
print(f"Shortlisted: {'YES ✅' if result1['is_shortlisted'] else 'NO ❌'}")
print(f"\nWeights Applied:")
print(f"  Skills: {result1['weights']['skills']*100}%")
print(f"  Experience: {result1['weights']['experience']*100}%")
print(f"  Education: {result1['weights']['education']*100}%")
print(f"\nSkill Details:")
print(f"  Matched: {result1['details']['skills']['matched']}")
print(f"  Missing: {result1['details']['skills']['missing']}")
print(f"  Match Ratio: {result1['details']['skills']['match_ratio']}%")

# Test Case 2: Senior Position
print("\n" + "=" * 80)
print("TEST 2: Senior Backend Engineer")
print("=" * 80)

jd_senior = {
    'job_title': 'Senior Backend Engineer',
    'experience_required': '5+ years in backend development',
    'required_skills': ['Java', 'Spring Boot', 'Microservices', 'AWS', 'Docker', 'Kubernetes'],
    'qualifications': ['Bachelor degree in CS or related field'],
    'responsibilities': ['Lead backend architecture', 'Mentor junior developers', 'Design scalable systems']
}

resume_senior_good = {
    'name': 'Jane Smith',
    'skills': ['Java', 'Spring Boot', 'Microservices', 'AWS', 'Docker', 'Kubernetes', 'PostgreSQL'],
    'experience': '7 years of experience in backend development at Fortune 500 companies',
    'education': 'Master of Science in Computer Engineering, Percentage: 85%'
}

result2 = get_detailed_score(resume_senior_good, jd_senior)
print(f"\nCandidate: {resume_senior_good['name']}")
print(f"Seniority Detected: {result2['seniority_level']}")
print(f"Skills Match: {result2['skills_match']}/10")
print(f"Experience: {result2['experience_relevance']}/10")
print(f"Education: {result2['education_fit']}/10")
print(f"Overall Score: {result2['overall_fit']}/10")
print(f"Shortlisted: {'YES ✅' if result2['is_shortlisted'] else 'NO ❌'}")
print(f"\nWeights Applied:")
print(f"  Skills: {result2['weights']['skills']*100}%")
print(f"  Experience: {result2['weights']['experience']*100}%")
print(f"  Education: {result2['weights']['education']*100}%")

# Test Case 3: Unqualified Candidate (Should be rejected)
print("\n" + "=" * 80)
print("TEST 3: Unqualified Candidate (Different Tech Stack)")
print("=" * 80)

resume_bad = {
    'name': 'Bob Johnson',
    'skills': ['PHP', 'jQuery', 'MySQL', 'HTML', 'CSS'],
    'experience': '1 year at small startup',
    'education': 'BCA, 65%'
}

result3 = get_detailed_score(resume_bad, jd_senior)
print(f"\nCandidate: {resume_bad['name']}")
print(f"Seniority Detected: {result3['seniority_level']}")
print(f"Skills Match: {result3['skills_match']}/10")
print(f"Experience: {result3['experience_relevance']}/10")
print(f"Education: {result3['education_fit']}/10")
print(f"Overall Score: {result3['overall_fit']}/10")
print(f"Shortlisted: {'YES ✅' if result3['is_shortlisted'] else 'NO ❌'}")
print(f"\nSkill Details:")
print(f"  Matched: {result3['details']['skills']['matched']}")
print(f"  Missing: {result3['details']['skills']['missing']}")
print(f"  Critical Missing: {result3['details']['skills']['critical_missing']}")

# Test Case 4: Mid-Level Position
print("\n" + "=" * 80)
print("TEST 4: Mid-Level Full Stack Developer")
print("=" * 80)

jd_mid = {
    'job_title': 'Full Stack Developer',
    'experience_required': '3-5 years',
    'required_skills': ['React', 'Node.js', 'MongoDB', 'TypeScript', 'REST API'],
    'qualifications': ['Bachelor degree'],
    'responsibilities': ['Develop features', 'Code reviews', 'Work with team']
}

resume_mid = {
    'name': 'Alice Williams',
    'skills': ['React', 'Node.js', 'MongoDB', 'JavaScript', 'Express', 'Git'],
    'experience': '4 years at tech companies',
    'education': 'B.Tech in Information Technology, CGPA: 7.8'
}

result4 = get_detailed_score(resume_mid, jd_mid)
print(f"\nCandidate: {resume_mid['name']}")
print(f"Seniority Detected: {result4['seniority_level']}")
print(f"Skills Match: {result4['skills_match']}/10")
print(f"Experience: {result4['experience_relevance']}/10")
print(f"Education: {result4['education_fit']}/10")
print(f"Overall Score: {result4['overall_fit']}/10")
print(f"Shortlisted: {'YES ✅' if result4['is_shortlisted'] else 'NO ❌'}")
print(f"\nWeights Applied:")
print(f"  Skills: {result4['weights']['skills']*100}%")
print(f"  Experience: {result4['weights']['experience']*100}%")
print(f"  Education: {result4['weights']['education']*100}%")

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Test 1 (Entry-Level): {result1['overall_fit']:.1f}/10 - {'PASS ✅' if result1['is_shortlisted'] else 'FAIL ❌'}")
print(f"Test 2 (Senior Qualified): {result2['overall_fit']:.1f}/10 - {'PASS ✅' if result2['is_shortlisted'] else 'FAIL ❌'}")
print(f"Test 3 (Unqualified): {result3['overall_fit']:.1f}/10 - {'PASS ✅' if not result3['is_shortlisted'] else 'FAIL ❌'} (Should be rejected)")
print(f"Test 4 (Mid-Level): {result4['overall_fit']:.1f}/10 - {'PASS ✅' if result4['is_shortlisted'] else 'FAIL ❌'}")
print("\nAll tests completed!")
