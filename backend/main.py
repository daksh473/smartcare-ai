from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai.sentiment_classifier import analyze_sentiment, decide_action
from ai.bot_reply import generate_reply
from database import init_db, save_conversation, get_all_conversations
from dotenv import load_dotenv
import json

load_dotenv()
init_db()  # DB start pe initialize hoga

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    message: str

@app.post("/analyze")
def analyze(req: MessageRequest):
    result = analyze_sentiment(req.message)
    action = decide_action(result["score"])
    reply  = generate_reply(req.message, action)
    save_conversation(req.message, result["score"], result["emotion"], action, reply)
    return {
        "message": req.message,
        "score":   result["score"],
        "emotion": result["emotion"],
        "action":  action,
        "reply":   reply
    }

@app.get("/history")
def history():
    return get_all_conversations()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected!")
    try:
        while True:
            data = await websocket.receive_text()
            result = analyze_sentiment(data)
            action = decide_action(result["score"])
            reply  = generate_reply(data, action)
            save_conversation(data, result["score"], result["emotion"], action, reply)
            response = {
                "message": data,
                "score":   result["score"],
                "emotion": result["emotion"],
                "action":  action,
                "reply":   reply
            }
            await websocket.send_text(json.dumps(response))
    except Exception as e:
        print(f"Client disconnected: {e}")