from fastapi import FastAPI, UploadFile, File, HTTPException
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import google.generativeai as genai
import os
import shutil
from pathlib import Path
from parsers.resume_parser import extract_resume_data
from parsers.jd_parser import extract_jd_data

load_dotenv()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

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
