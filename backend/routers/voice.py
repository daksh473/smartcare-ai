import os
import io
import tempfile
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from groq import Groq
from ai.sentiment_classifier import analyze_sentiment, decide_action
from ai.bot_reply import generate_reply
from database import save_conversation_message, save_voice_metadata
from dotenv import load_dotenv
import uuid

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

router = APIRouter(prefix="/voice", tags=["Voice"])

class SpeakRequest(BaseModel):
    text: str
    language: str = "en"

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe audio using Groq Whisper API"""
    try:
        # Read audio bytes
        audio_bytes = await file.read()
        
        # Write to a temp file (Groq SDK expects a file-like object with a name)
        suffix = ".webm"
        if file.filename:
            if file.filename.endswith(".wav"):
                suffix = ".wav"
            elif file.filename.endswith(".mp3"):
                suffix = ".mp3"
        
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(audio_bytes)
        tmp.flush()
        tmp.close()

        with open(tmp.name, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                response_format="verbose_json"
            )

        os.unlink(tmp.name)

        return {
            "transcript": transcription.text,
            "language": getattr(transcription, "language", "en"),
            "confidence": round(getattr(transcription, "duration", 1.0) and 0.92, 2)  # Whisper doesn't return confidence directly
        }
    except Exception as e:
        print(f"Transcription error: {e}")
        return {
            "transcript": "",
            "language": "en",
            "confidence": 0.0,
            "error": str(e)
        }

@router.post("/speak")
def speak_text(req: SpeakRequest):
    """Return text for browser-side TTS (Web Speech API handles actual speech)"""
    return {
        "text": req.text,
        "language": req.language
    }

@router.post("/process")
async def full_voice_pipeline(file: UploadFile = File(...)):
    """Full pipeline: audio → transcribe → sentiment → bot reply"""
    try:
        # Step 1: Transcribe
        audio_bytes = await file.read()
        
        suffix = ".webm"
        if file.filename:
            if file.filename.endswith(".wav"):
                suffix = ".wav"
            elif file.filename.endswith(".mp3"):
                suffix = ".mp3"
        
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(audio_bytes)
        tmp.flush()
        tmp.close()

        with open(tmp.name, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                response_format="verbose_json"
            )

        os.unlink(tmp.name)

        transcript = transcription.text
        language = getattr(transcription, "language", "en")
        confidence = getattr(transcription, "duration", 1.0) and 0.92  # Mock confidence for now

        if not transcript or not transcript.strip():
            return {
                "transcript": "",
                "sentiment": {"score": 0.5, "emotion": "neutral", "action": "NORMAL"},
                "bot_reply": "I couldn't hear you clearly. Please try again.",
                "language": language,
                "error": "Empty transcription"
            }

        # Step 2: Sentiment Analysis
        result = analyze_sentiment(transcript)
        action = decide_action(result["score"])

        # Step 3: Bot Reply
        reply = generate_reply(transcript, action)

        # Step 4: Save conversation and voice metadata
        session_id = f"voice-{uuid.uuid4().hex[:8]}"
        save_conversation_message(session_id, "user", transcript, result["score"], result["emotion"], action)
        save_conversation_message(session_id, "assistant", reply, result["score"], result["emotion"], action)
        save_voice_metadata(session_id, language, confidence)

        return {
            "transcript": transcript,
            "sentiment": {
                "score": result["score"],
                "emotion": result["emotion"],
                "action": action
            },
            "bot_reply": reply,
            "language": language
        }
    except Exception as e:
        print(f"Voice pipeline error: {e}")
        return {
            "transcript": "",
            "sentiment": {"score": 0.5, "emotion": "neutral", "action": "NORMAL"},
            "bot_reply": "Something went wrong with voice processing. Please try again.",
            "language": "en",
            "error": str(e)
        }
