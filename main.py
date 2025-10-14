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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
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
        
        finally:
            if resume_path.exists():
                resume_path.unlink()
            if jd_path.exists():
                jd_path.unlink()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scoring files: {str(e)}")
