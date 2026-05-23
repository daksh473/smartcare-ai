import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import save_conversation_message, get_conversation_history, create_ticket
from ai.sentiment_classifier import analyze_sentiment, decide_action
from ai.bot_reply import generate_reply

router = APIRouter(prefix="/conversation", tags=["Conversation"])

class StartSessionResponse(BaseModel):
    session_id: str

class MessageRequest(BaseModel):
    session_id: str
    message: str

@router.post("/start", response_model=StartSessionResponse)
def start_session():
    return {"session_id": str(uuid.uuid4())}

@router.post("/message")
def send_message(req: MessageRequest):
    # Retrieve history for context
    db_history = get_conversation_history(req.session_id)
    history_formatted = []
    for msg in db_history:
        history_formatted.append({"role": msg["role"], "content": msg["message"]})

    # AI Processing
    result = analyze_sentiment(req.message)
    action = decide_action(result["score"])
    
    # Generate bot reply with history
    reply = generate_reply(req.message, action, history_formatted)
    
    # Save user message
    save_conversation_message(
        session_id=req.session_id,
        role="user",
        message=req.message,
        sentiment_score=result["score"],
        emotion=result["emotion"],
        action=action
    )
    
    # Save bot reply
    save_conversation_message(
        session_id=req.session_id,
        role="assistant",
        message=reply,
        sentiment_score=result["score"],
        emotion=result["emotion"],
        action=action
    )

    # Auto-create ticket if ESCALATE
    ticket_created = False
    if action == "ESCALATE":
        create_ticket(
            customer_name=f"Session {req.session_id[:8]}", 
            issue=req.message,
            score=result["score"]
        )
        ticket_created = True

    return {
        "score": result["score"],
        "emotion": result["emotion"],
        "reply": reply,
        "action": action,
        "ticket_created": ticket_created
    }

@router.get("/{session_id}")
def get_session(session_id: str):
    history = get_conversation_history(session_id)
    return {"session_id": session_id, "messages": history}
