from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId
import os

load_dotenv()

db_client = None
db = None

def get_db_client():
    global db_client, db
    if db_client is not None:
        return db_client
    
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("MongoDB URI not configured")
        return None
    
    try:
        db_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
        db_client.admin.command('ping')
        db_name = os.getenv("DB_NAME", "smart_resume_screener")
        db = db_client[db_name]
        print("MongoDB connected")
        return db_client
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return None

def get_database():
    global db
    if db is None:
        get_db_client()
    return db

def close_db_client(client=None):
    global db_client, db
    if client:
        try:
            client.close()
        except:
            pass
    if db_client:
        try:
            db_client.close()
            db_client = None
            db = None
        except:
            pass

def save_resume(resume_data, filename):
    db = get_database()
    if db is None:
        return None
    
    try:
        resume_doc = {
            "filename": filename,
            "name": resume_data.get("name", "Unknown"),
            "email": resume_data.get("email", ""),
            "phone": resume_data.get("phone", ""),
            "skills": resume_data.get("skills", []),
            "education": resume_data.get("education", []),
            "experience": resume_data.get("experience", []),
            "projects": resume_data.get("projects", []),
            "timestamp": datetime.utcnow()
        }
        result = db.resumes.insert_one(resume_doc)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error saving resume: {e}")
        return None

def save_job_description(jd_data, filename):
    db = get_database()
    if db is None:
        return None
    
    try:
        jd_doc = {
            "filename": filename,
            "job_title": jd_data.get("job_title", "Unknown"),
            "company": jd_data.get("company", ""),
            "location": jd_data.get("location", ""),
            "required_skills": jd_data.get("required_skills", []),
            "experience_required": jd_data.get("experience_required", ""),
            "qualifications": jd_data.get("qualifications", []),
            "responsibilities": jd_data.get("responsibilities", []),
            "timestamp": datetime.utcnow()
        }
        result = db.job_descriptions.insert_one(jd_doc)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error saving job description: {e}")
        return None

def save_score(resume_id, jd_id, score_data, resume_filename, jd_filename):
    db = get_database()
    if db is None:
        return None
    
    try:
        score_doc = {
            "resume_id": resume_id,
            "jd_id": jd_id,
            "resume_filename": resume_filename,
            "jd_filename": jd_filename,
            "candidate_name": score_data.get("name", "Unknown"),
            "job_title": score_data.get("job_title", "Unknown"),
            "skills_match": score_data.get("skills_match", 0),
            "experience_relevance": score_data.get("experience_relevance", 0),
            "education_fit": score_data.get("education_fit", 0),
            "overall_fit": score_data.get("overall_fit", 0),
            "justification": score_data.get("justification", ""),
            "is_shortlisted": score_data.get("is_shortlisted", False),
            "seniority_level": score_data.get("seniority_level", "unknown"),
            "weights": score_data.get("weights", {"skills": 0.5, "experience": 0.3, "education": 0.2}),
            "details": score_data.get("details", {}),
            "timestamp": datetime.utcnow()
        }
        result = db.scores.insert_one(score_doc)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error saving score: {e}")
        return None

def get_db_status():
    db = get_database()
    if db is None:
        return {"connected": False, "error": "Database not configured"}
    
    try:
        db.command('ping')
        return {
            "connected": True,
            "database": db.name,
            "collections": {
                "resumes": db.resumes.count_documents({}),
                "job_descriptions": db.job_descriptions.count_documents({}),
                "scores": db.scores.count_documents({})
            }
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}

def get_all_resumes():
    db = get_database()
    if db is None:
        return []
    
    try:
        resumes = list(db.resumes.find().sort("timestamp", -1).limit(100))
        for resume in resumes:
            resume["_id"] = str(resume["_id"])
        return resumes
    except Exception as e:
        print(f"Error fetching resumes: {e}")
        return []

def get_all_scores():
    db = get_database()
    if db is None:
        return []
    
    try:
        scores = list(db.scores.find().sort("timestamp", -1).limit(100))
        for score in scores:
            score["_id"] = str(score["_id"])
        return scores
    except Exception as e:
        print(f"Error fetching scores: {e}")
        return []

def get_all_job_descriptions():
    db = get_database()
    if db is None:
        return []
    
    try:
        jds = list(db.job_descriptions.find().sort("timestamp", -1).limit(100))
        for jd in jds:
            jd["_id"] = str(jd["_id"])
        return jds
    except Exception as e:
        print(f"Error fetching job descriptions: {e}")
        return []

def get_job_description_by_id(jd_id):
    db = get_database()
    if db is None:
        return None
    
    try:
        jd = db.job_descriptions.find_one({"_id": ObjectId(jd_id)})
        if jd:
            jd["_id"] = str(jd["_id"])
        return jd
    except Exception as e:
        print(f"Error fetching job description: {e}")
        return None

def delete_resume(resume_id):
    db = get_database()
    if db is None:
        return False
    
    try:
        resume_result = db.resumes.delete_one({"_id": ObjectId(resume_id)})
        
        if resume_result.deleted_count > 0:
            scores_result = db.scores.delete_many({"resume_id": resume_id})
            print(f"Deleted resume {resume_id} and {scores_result.deleted_count} associated scores")
            return True
        
        return False
    except Exception as e:
        print(f"Error deleting resume: {e}")
        return False

def delete_score(score_id):
    db = get_database()
    if db is None:
        return False
    
    try:
        result = db.scores.delete_one({"_id": ObjectId(score_id)})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting score: {e}")
        return False

def delete_job_description(jd_id):
    db = get_database()
    if db is None:
        return False
    
    try:
        jd_result = db.job_descriptions.delete_one({"_id": ObjectId(jd_id)})
        
        if jd_result.deleted_count > 0:
            scores_result = db.scores.delete_many({"jd_id": jd_id})
            print(f"Deleted job description {jd_id} and {scores_result.deleted_count} associated scores")
            return True
        
        return False
    except Exception as e:
        print(f"Error deleting job description: {e}")
        return False

def cleanup_orphaned_scores():
    db = get_database()
    if db is None:
        return 0
    
    try:
        resume_ids = set([str(r["_id"]) for r in db.resumes.find({}, {"_id": 1})])
        jd_ids = set([str(j["_id"]) for j in db.job_descriptions.find({}, {"_id": 1})])
        
        orphaned_count = 0
        for score in db.scores.find():
            if score["resume_id"] not in resume_ids or score["jd_id"] not in jd_ids:
                db.scores.delete_one({"_id": score["_id"]})
                orphaned_count += 1
        
        if orphaned_count > 0:
            print(f"Cleaned up {orphaned_count} orphaned scores")
        
        return orphaned_count
    except Exception as e:
        print(f"Error cleaning orphaned scores: {e}")
        return 0

def clear_all_data():
    db = get_database()
    if db is None:
        return False
    
    try:
        resumes_count = db.resumes.delete_many({}).deleted_count
        jds_count = db.job_descriptions.delete_many({}).deleted_count
        scores_count = db.scores.delete_many({}).deleted_count
        print(f"Cleared {resumes_count} resumes, {jds_count} job descriptions, {scores_count} scores")
        return True
    except Exception as e:
        print(f"Error clearing data: {e}")
        return False

def get_resume_scores(resume_id):
    db = get_database()
    if db is None:
        return []
    
    try:
        scores = list(db.scores.find({"resume_id": resume_id}).sort("timestamp", -1))
        for score in scores:
            score["_id"] = str(score["_id"])
        return scores
    except Exception as e:
        print(f"Error fetching resume scores: {e}")
        return []

def get_analytics_data():
    db = get_database()
    if db is None:
        return None
    
    try:
        total_resumes = db.resumes.count_documents({})
        total_scores = db.scores.count_documents({})
        
        avg_fit_pipeline = [
            {"$group": {
                "_id": None,
                "avg_skills": {"$avg": "$skills_match"},
                "avg_experience": {"$avg": "$experience_relevance"},
                "avg_education": {"$avg": "$education_fit"},
                "avg_overall": {"$avg": "$overall_fit"}
            }}
        ]
        avg_result = list(db.scores.aggregate(avg_fit_pipeline))
        avg_scores = avg_result[0] if avg_result else {}
        
        skills_pipeline = [
            {"$unwind": "$skills"},
            {"$group": {"_id": "$skills", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_skills = list(db.resumes.aggregate(skills_pipeline))
        
        roles_pipeline = [
            {"$group": {"_id": "$job_title", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_roles = list(db.job_descriptions.aggregate(roles_pipeline))
        
        submissions_pipeline = [
            {"$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}},
            {"$limit": 30}
        ]
        submissions_over_time = list(db.scores.aggregate(submissions_pipeline))
        
        fit_by_role_pipeline = [
            {"$group": {
                "_id": "$job_title",
                "avg_fit": {"$avg": "$overall_fit"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"avg_fit": -1}},
            {"$limit": 10}
        ]
        fit_by_role = list(db.scores.aggregate(fit_by_role_pipeline))
        
        return {
            "total_resumes": total_resumes,
            "total_scores": total_scores,
            "average_scores": {
                "skills_match": round(avg_scores.get("avg_skills", 0), 2),
                "experience_relevance": round(avg_scores.get("avg_experience", 0), 2),
                "education_fit": round(avg_scores.get("avg_education", 0), 2),
                "overall_fit": round(avg_scores.get("avg_overall", 0), 2)
            },
            "top_skills": [{"skill": s["_id"], "count": s["count"]} for s in top_skills],
            "most_requested_roles": [{"role": r["_id"], "count": r["count"]} for r in top_roles],
            "submissions_over_time": [{"date": s["_id"], "count": s["count"]} for s in submissions_over_time],
            "fit_by_role": [{"role": f["_id"], "avg_fit": round(f["avg_fit"], 2), "count": f["count"]} for f in fit_by_role]
        }
    except Exception as e:
        print(f"Error getting analytics: {e}")
        return None
