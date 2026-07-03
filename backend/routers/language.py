from fastapi import APIRouter
from pydantic import BaseModel
import sqlite3
from ai.language_ai import translate_text

router = APIRouter(prefix="/languages", tags=["Languages"])

DB_PATH = "smartcare.db"

# Language display map
LANGUAGE_MAP = {
    "hi": "Hindi",
    "hin": "Hinglish",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "kn": "Kannada",
    "ml": "Malayalam",
    "or": "Odia",
    "ur": "Urdu",
    "en": "English"
}

@router.get("/stats")
def get_language_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT language, COUNT(*), AVG(sentiment_score) FROM conversations GROUP BY language")
        rows = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total = cursor.fetchone()[0] or 1
        
        stats = []
        for row in rows:
            code = row[0] if row[0] else "en"
            count = row[1]
            avg_sentiment = row[2] or 0.5
            stats.append({
                "language": code,
                "language_name": LANGUAGE_MAP.get(code, "English"),
                "flag": "🇮🇳" if code != "en" else "🌐",
                "count": count,
                "percentage": round((count / total) * 100, 1),
                "avg_sentiment": round(avg_sentiment, 2)
            })
            
        stats.sort(key=lambda x: x["count"], reverse=True)
        return stats
    finally:
        conn.close()

class TranslateRequest(BaseModel):
    text: str
    target_language_code: str

@router.post("/translate")
def translate_text_endpoint(req: TranslateRequest):
    translated = translate_text(req.text, req.target_language_code)
    return {
        "original": req.text,
        "translated": translated
    }
