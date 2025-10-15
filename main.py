from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import google.generativeai as genai
import os
import shutil
from pathlib import Path
from parsers.resume_parser import extract_resume_data
from parsers.jd_parser import extract_jd_data
from llm_scorer import get_match_score, get_detailed_analysis, get_detailed_score
from pydantic import BaseModel
from typing import Dict, Any

load_dotenv()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class MatchRequest(BaseModel):
    resume_data: Dict[str, Any]
    jd_data: Dict[str, Any]

class ScoreRequest(BaseModel):
    resume_path: str
    jd_path: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    from database import get_db_client, close_db_client
    
    db_client = get_db_client()
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        genai.configure(api_key=gemini_key)
    
    yield
    
    close_db_client(db_client)

app = FastAPI(lifespan=lifespan)

# Create API router with /api prefix
from fastapi import APIRouter
api_router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "https://smart-resume-backend.onrender.com", "https://smart-resume-screener-jee0.onrender.com", "https://smart-resume-screener.vercel.app", "https://smart-resume-screener-kappa.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the API router with /api prefix
app.mount("/api", api_router)

@app.get("/")
def root():
    return {"message": "Smart Resume Screener API running"}

@api_router.get("/")
def api_root():
    return {"message": "Smart Resume Screener API running"}

@app.post("/parse_resume")
async def parse_resume(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    file_path = UPLOAD_DIR / file.filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        parsed_data = extract_resume_data(str(file_path))
        
        return {
            "status": "success",
            "filename": file.filename,
            "data": parsed_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")
    
    finally:
        if file_path.exists():
            file_path.unlink()

@app.post("/parse_jd")
async def parse_jd(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    file_path = UPLOAD_DIR / file.filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        parsed_data = extract_jd_data(str(file_path))
        
        return {
            "status": "success",
            "filename": file.filename,
            "data": parsed_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing job description: {str(e)}")
    
    finally:
        if file_path.exists():
            file_path.unlink()

@app.post("/match")
async def match_resume_jd(request: MatchRequest):
    try:
        if not request.resume_data or not request.jd_data:
            raise HTTPException(status_code=400, detail="Both resume_data and jd_data are required")
        
        result = get_match_score(request.resume_data, request.jd_data)
        
        return {
            "status": "success",
            "score": result["score"],
            "justification": result["justification"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error matching resume: {str(e)}")

@app.post("/analyze")
async def analyze_candidate(request: MatchRequest):
    try:
        if not request.resume_data or not request.jd_data:
            raise HTTPException(status_code=400, detail="Both resume_data and jd_data are required")
        
        analysis = get_detailed_analysis(request.resume_data, request.jd_data)
        
        return {
            "status": "success",
            "analysis": analysis
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing candidate: {str(e)}")

@app.post("/score")
async def score_resume_jd(request: ScoreRequest):
    try:
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise HTTPException(status_code=401, detail="Gemini API key not configured")
        
        resume_file = Path(request.resume_path)
        jd_file = Path(request.jd_path)
        
        if not resume_file.exists():
            raise HTTPException(status_code=422, detail=f"Resume file not found: {request.resume_path}")
        
        if not jd_file.exists():
            raise HTTPException(status_code=422, detail=f"Job description file not found: {request.jd_path}")
        
        if not resume_file.suffix.lower() == '.pdf':
            raise HTTPException(status_code=422, detail="Resume must be a PDF file")
        
        if not jd_file.suffix.lower() == '.pdf':
            raise HTTPException(status_code=422, detail="Job description must be a PDF file")
        
        resume_data = extract_resume_data(str(resume_file))
        jd_data = extract_jd_data(str(jd_file))
        
        detailed_score = get_detailed_score(resume_data, jd_data)
        
        return {
            "status": "success",
            "candidate_name": resume_data.get('name', 'Unknown'),
            "job_title": jd_data.get('job_title', 'Not specified'),
            "skills_match": detailed_score["skills_match"],
            "experience_relevance": detailed_score["experience_relevance"],
            "education_fit": detailed_score["education_fit"],
            "overall_fit": detailed_score["overall_fit"],
            "justification": detailed_score["justification"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scoring resume: {str(e)}")

@app.post("/score_files")
async def score_uploaded_files(resume: UploadFile = File(...), jd: UploadFile = File(...)):
    from database import save_resume, save_job_description, save_score
    
    try:
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise HTTPException(status_code=401, detail="Gemini API key not configured")
        
        if not resume.filename.endswith('.pdf'):
            raise HTTPException(status_code=422, detail="Resume must be a PDF file")
        
        if not jd.filename.endswith('.pdf'):
            raise HTTPException(status_code=422, detail="Job description must be a PDF file")
        
        resume_path = UPLOAD_DIR / resume.filename
        jd_path = UPLOAD_DIR / jd.filename
        
        try:
            with open(resume_path, "wb") as buffer:
                shutil.copyfileobj(resume.file, buffer)
            
            with open(jd_path, "wb") as buffer:
                shutil.copyfileobj(jd.file, buffer)
            
            resume_data = extract_resume_data(str(resume_path))
            jd_data = extract_jd_data(str(jd_path))
            
            detailed_score = get_detailed_score(resume_data, jd_data)
            
            resume_id = save_resume(resume_data, resume.filename)
            jd_id = save_job_description(jd_data, jd.filename)
            
            score_data = {
                "name": resume_data.get('name', 'Unknown'),
                "job_title": jd_data.get('job_title', 'Not specified'),
                "skills_match": detailed_score["skills_match"],
                "experience_relevance": detailed_score["experience_relevance"],
                "education_fit": detailed_score["education_fit"],
                "overall_fit": detailed_score["overall_fit"],
                "justification": detailed_score["justification"]
            }
            
            score_id = save_score(resume_id, jd_id, score_data, resume.filename, jd.filename)
            
            return {
                "status": "success",
                "score_id": score_id,
                "resume_id": resume_id,
                "jd_id": jd_id,
                "candidate_name": resume_data.get('name', 'Unknown'),
                "job_title": jd_data.get('job_title', 'Not specified'),
                "skills_match": detailed_score["skills_match"],
                "experience_relevance": detailed_score["experience_relevance"],
                "education_fit": detailed_score["education_fit"],
                "overall_fit": detailed_score["overall_fit"],
                "justification": detailed_score["justification"]
            }
        
        finally:
            if resume_path.exists():
                resume_path.unlink()
            if jd_path.exists():
                jd_path.unlink()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scoring files: {str(e)}")

@app.post("/score_with_existing_jd")
async def score_with_existing_jd(resume: UploadFile = File(...), jd_id: str = Body(...)):
    from database import save_resume, save_score, get_job_description_by_id
    
    try:
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise HTTPException(status_code=401, detail="Gemini API key not configured")
        
        if not resume.filename.endswith('.pdf'):
            raise HTTPException(status_code=422, detail="Resume must be a PDF file")
        
        # Get JD data from database
        jd_doc = get_job_description_by_id(jd_id)
        if not jd_doc:
            raise HTTPException(status_code=404, detail="Job description not found")
        
        resume_path = UPLOAD_DIR / resume.filename
        
        try:
            with open(resume_path, "wb") as buffer:
                shutil.copyfileobj(resume.file, buffer)
            
            resume_data = extract_resume_data(str(resume_path))
            
            # Convert JD document to the format expected by scorer
            jd_data = {
                "job_title": jd_doc.get("job_title", "Unknown"),
                "company": jd_doc.get("company", ""),
                "location": jd_doc.get("location", ""),
                "required_skills": jd_doc.get("required_skills", []),
                "experience_required": jd_doc.get("experience_required", ""),
                "qualifications": jd_doc.get("qualifications", []),
                "responsibilities": jd_doc.get("responsibilities", [])
            }
            
            detailed_score = get_detailed_score(resume_data, jd_data)
            
            resume_id = save_resume(resume_data, resume.filename)
            
            score_data = {
                "name": resume_data.get('name', 'Unknown'),
                "job_title": jd_data.get('job_title', 'Not specified'),
                "skills_match": detailed_score["skills_match"],
                "experience_relevance": detailed_score["experience_relevance"],
                "education_fit": detailed_score["education_fit"],
                "overall_fit": detailed_score["overall_fit"],
                "justification": detailed_score["justification"]
            }
            
            score_id = save_score(resume_id, jd_id, score_data, resume.filename, jd_doc.get("filename", ""))
            
            return {
                "status": "success",
                "score_id": score_id,
                "resume_id": resume_id,
                "jd_id": jd_id,
                "candidate_name": resume_data.get('name', 'Unknown'),
                "job_title": jd_data.get('job_title', 'Not specified'),
                "skills_match": detailed_score["skills_match"],
                "experience_relevance": detailed_score["experience_relevance"],
                "education_fit": detailed_score["education_fit"],
                "overall_fit": detailed_score["overall_fit"],
                "justification": detailed_score["justification"]
            }
        
        finally:
            if resume_path.exists():
                resume_path.unlink()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scoring with existing JD: {str(e)}")

@app.get("/analytics")
async def get_analytics():
    from database import get_analytics_data
    
    try:
        analytics = get_analytics_data()
        
        if not analytics:
            raise HTTPException(status_code=500, detail="Unable to fetch analytics data")
        
        return {
            "status": "success",
            "data": analytics
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")

@api_router.get("/db_status")
async def check_db_status():
    from database import get_db_status, cleanup_orphaned_scores
    
    try:
        cleanup_orphaned_scores()
        status = get_db_status()
        return {
            "status": "success",
            "data": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking database status: {str(e)}")

@api_router.get("/resumes")
async def get_resumes():
    from database import get_all_resumes
    
    try:
        resumes = get_all_resumes()
        return {
            "status": "success",
            "count": len(resumes),
            "data": resumes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching resumes: {str(e)}")

@api_router.get("/scores")
async def get_scores():
    from database import get_all_scores
    
    try:
        scores = get_all_scores()
        return {
            "status": "success",
            "count": len(scores),
            "data": scores
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching scores: {str(e)}")

@api_router.get("/job_descriptions")
async def get_job_descriptions():
    from database import get_all_job_descriptions
    
    try:
        jds = get_all_job_descriptions()
        return {
            "status": "success",
            "count": len(jds),
            "data": jds
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching job descriptions: {str(e)}")

@app.get("/resumes/{resume_id}/scores")
async def get_resume_scores(resume_id: str):
    from database import get_resume_scores
    
    try:
        scores = get_resume_scores(resume_id)
        return {
            "status": "success",
            "count": len(scores),
            "data": scores
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching resume scores: {str(e)}")

@app.delete("/resumes/{resume_id}")
async def delete_resume(resume_id: str):
    from database import delete_resume
    
    try:
        success = delete_resume(resume_id)
        if not success:
            raise HTTPException(status_code=404, detail="Resume not found or unable to delete")
        
        return {
            "status": "success",
            "message": "Resume deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting resume: {str(e)}")

@app.delete("/scores/{score_id}")
async def delete_score(score_id: str):
    from database import delete_score
    
    try:
        success = delete_score(score_id)
        if not success:
            raise HTTPException(status_code=404, detail="Score not found or unable to delete")
        
        return {
            "status": "success",
            "message": "Score deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting score: {str(e)}")

@app.post("/clear_database")
async def clear_database():
    from database import clear_all_data
    
    try:
        success = clear_all_data()
        if not success:
            raise HTTPException(status_code=500, detail="Unable to clear database")
        
        return {
            "status": "success",
            "message": "All data cleared successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing database: {str(e)}")
