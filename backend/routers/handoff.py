from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from database import (
    get_agents, get_agent, create_agent, update_agent_status,
    create_handoff, get_handoffs, accept_handoff, resolve_handoff, transfer_handoff
)
from ai.crm_ai import auto_route_agent

router = APIRouter(prefix="/handoff", tags=["Handoff"])

class AgentCreate(BaseModel):
    name: str
    email: str
    specialization: str = "general"
    max_conversations: int = 3

class AgentStatusUpdate(BaseModel):
    status: str

class HandoffCreate(BaseModel):
    session_id: str
    customer_id: Optional[int] = None
    sentiment_score: Optional[float] = None
    emotion: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = []

class HandoffResolve(BaseModel):
    resolution_notes: str
    customer_rating: Optional[int] = None

class HandoffTransfer(BaseModel):
    new_agent_id: int
    reason: str

class AutoRouteRequest(BaseModel):
    issue_text: str

@router.get("/agents")
def list_agents():
    return get_agents()

@router.post("/agents")
def add_agent(req: AgentCreate):
    aid = create_agent(req.name, req.email, req.specialization, req.max_conversations)
    return {"id": aid}

@router.put("/agents/{agent_id}/status")
def change_agent_status(agent_id: int, req: AgentStatusUpdate):
    if req.status not in ["online", "busy", "offline"]:
        raise HTTPException(400, "Invalid status")
    agent = update_agent_status(agent_id, req.status)
    return {"success": True, "agent": agent}

@router.post("/create")
def new_handoff(req: HandoffCreate):
    # Determine reason/specialization via AI if there is conversation history
    issue_preview = "General inquiry"
    if req.conversation_history:
        issue_preview = req.conversation_history[-1].get("message", "")[:200]
        
    route_info = auto_route_agent(issue_preview)
    specialization = route_info.get("specialization", "general")
    reason = route_info.get("reason", "Needs human assistance")

    # Find best agent
    agents = get_agents()
    # Filter by online and under max load
    available = [a for a in agents if a["status"] == "online" and a["current_conversations"] < a["max_conversations"]]
    
    selected_agent = None
    if available:
        # Prefer matching specialization
        matching = [a for a in available if a["specialization"] == specialization]
        pool = matching if matching else available
        # Pick least busy
        pool.sort(key=lambda x: x["current_conversations"])
        selected_agent = pool[0]

    priority = "medium"
    if req.sentiment_score is not None:
        if req.sentiment_score < 0.2:
            priority = "urgent"
        elif req.sentiment_score < 0.4:
            priority = "high"

    agent_id = selected_agent["id"] if selected_agent else None
    
    hid = create_handoff(
        session_id=req.session_id,
        customer_id=req.customer_id,
        agent_id=agent_id,
        reason=f"[{specialization.upper()}] {reason}",
        sentiment_score=req.sentiment_score,
        emotion=req.emotion,
        priority=priority,
        conversation_history=req.conversation_history
    )

    return {
        "handoff_id": hid,
        "agent": selected_agent,
        "estimated_wait": 0 if selected_agent else 5,
        "priority": priority
    }

@router.post("/accept/{handoff_id}")
def accept_handoff_api(handoff_id: int):
    accept_handoff(handoff_id)
    return {"success": True}

@router.post("/resolve/{handoff_id}")
def resolve_handoff_api(handoff_id: int, req: HandoffResolve):
    resolve_handoff(handoff_id, req.resolution_notes, req.customer_rating)
    return {"success": True}

@router.post("/transfer/{handoff_id}")
def transfer_handoff_api(handoff_id: int, req: HandoffTransfer):
    transfer_handoff(handoff_id, req.new_agent_id, req.reason)
    return {"success": True}

@router.get("/queue")
def queue():
    return get_handoffs(status="pending")

@router.get("/active")
def active():
    return get_handoffs(status="active")

@router.get("/agent/{agent_id}")
def agent_handoffs(agent_id: int):
    return get_handoffs(agent_id=agent_id)

@router.post("/auto-route")
def auto_route_api(req: AutoRouteRequest):
    return auto_route_agent(req.issue_text)
