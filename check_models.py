import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    print("Available Gemini models:")
    print("-" * 50)
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"Model: {model.name}")
            print(f"Display Name: {model.display_name}")
            print(f"Description: {model.description}")
            print("-" * 50)
else:
    print("GEMINI_API_KEY not found in .env")
