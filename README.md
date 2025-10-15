# Smart Resume Screener

An AI-powered application that parses resumes, extracts key information, and semantically matches candidates to job descriptions using Google's Gemini API. The system automates candidate shortlisting by generating match scores (1–10) with justifications, helping recruiters identify the most relevant applicants efficiently.

## Table of Contents

- [Objective](#objective)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [System Architecture Diagram](#system-architecture-diagram)
- [LLM Usage Guidance](#llm-usage-guidance)
- [API Endpoints](#api-endpoints)
- [Database Collections](#database-collections)
- [Weighted Scoring Logic](#weighted-scoring-logic)
- [Setup Instructions](#setup-instructions)
- [Workflow](#workflow)
- [Deliverables](#deliverables)
- [Evaluation Criteria](#evaluation-criteria)
- [Future Enhancements](#future-enhancements)

## Objective

- Parse PDF or text-based resumes and job descriptions
- Extract structured data such as skills, experience, and education using NLP
- Use Gemini LLM for semantic matching and scoring
- Store parsed data and results in MongoDB
- Display shortlisted candidates with match explanations

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| Database | MongoDB |
| LLM Integration | Gemini API (google-generativeai) |
| Parsing & NLP | pdfminer.six, spaCy, regex |
| Frontend (optional) | React.js |
| Environment Management | python-dotenv |

## Architecture

### Folder Structure

```
smart-resume-screener/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── llm_scorer.py
│   ├── parsers/
│   │   ├── resume_parser.py
│   │   └── jd_parser.py
├── frontend/ (optional)
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.jsx
│   │   │   └── Home.jsx
│   ├── App.jsx
│   ├── index.js
├── .env
├── requirements.txt
└── README.md
```

## System Architecture Diagram

<img width="1536" height="1024" alt="architecture" src="https://github.com/user-attachments/assets/b3c9909c-60c1-4955-8d57-da1d0d5ed6e9" />

**Flow:** Resume & JD Upload → Parsing Engine → Gemini LLM → Scoring Engine → MongoDB → Frontend Dashboard

## LLM Usage Guidance

Smart Resume Screener exclusively uses **Google Gemini API** for semantic evaluation and scoring.

### Function

- Interprets job descriptions and resumes semantically, beyond keyword matching
- Computes a relevance score (1–10)
- Provides a short, human-readable justification for each candidate

### Example Prompt

```
Compare the following resume and job description.
Rate the candidate's fit from 1–10 and justify briefly.
Return a JSON response: { "score": <number>, "justification": "<text>" }

Resume: {resume_json}
Job Description: {jd_json}
```

## API Endpoints

| Route | Method | Description |
|-------|--------|-------------|
| `/upload_resume` | POST | Upload and parse a resume |
| `/upload_jd` | POST | Upload and parse a job description |
| `/match` | POST | Use Gemini API to generate match score and justification |
| `/shortlist` | GET | Retrieve shortlisted candidates sorted by score |

## Database Collections

| Collection | Purpose |
|------------|---------|
| `resumes` | Stores parsed resume data |
| `job_descriptions` | Stores uploaded job descriptions |
| `results` | Stores Gemini-generated scores and justifications |

## Weighted Scoring Logic

| Factor | Weight |
|--------|--------|
| Skill Match | 0.5 |
| Experience | 0.3 |
| Education & Role Alignment | 0.2 |

> **Note:** Resumes with less than 40% total alignment or missing essential skills are automatically rejected.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create a .env File

```env
GEMINI_API_KEY=your_gemini_api_key
MONGO_URI=your_mongo_connection_string
DB_NAME=resume_db
```

### 3. Run the FastAPI Server

```bash
uvicorn main:app --reload
```

## Workflow

1. Upload resumes and job descriptions
2. The system parses the content and extracts skills, education, and experience
3. Parsed data is passed to Gemini API for semantic comparison
4. Gemini returns a match score and justification
5. The results are stored in MongoDB and displayed via API or dashboard

## Deliverables

- GitHub repository with structured commits
- README (this document)
- 2–3 minute demonstration video of the working system
- Architecture diagram
- Example Gemini LLM prompts

## Evaluation Criteria

| Category | Description |
|----------|-------------|
| Code Quality | Modularity, readability, and structure |
| Data Extraction | Accuracy of skills and experience parsing |
| LLM Prompt Quality | Clarity, precision, and output consistency |
| Output Clarity | Relevance and justification accuracy |

## Future Enhancements

- Advanced analytics on candidate–JD matches
- Expanded resume parsing for different formats (DOCX, LinkedIn exports)
- Dashboard filtering and visual reporting
- Role-based access for HR and recruiters

---

**License:** MIT
