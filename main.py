from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()

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
