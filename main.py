from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import google.generativeai as genai
import os
import shutil
from pathlib import Path
from parsers.resume_parser import extract_resume_data
from parsers.jd_parser import extract_jd_data
from llm_scorer import get_match_score, get_detailed_analysis
from pydantic import BaseModel
from typing import Dict, Any

load_dotenv()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class MatchRequest(BaseModel):
    resume_data: Dict[str, Any]
    jd_data: Dict[str, Any]

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
