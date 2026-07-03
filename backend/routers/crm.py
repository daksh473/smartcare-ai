from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import (
    get_customers, get_customer, create_customer, update_customer, delete_customer,
    log_activity, get_customer_timeline, get_customer_full_profile,
    get_deals, create_deal, update_deal, delete_deal, get_crm_stats,
    upsert_customer_from_chat
)
from ai.customer_extractor import extract_customer_info
from ai.crm_ai import calculate_risk_score, generate_forecast, generate_customer_summary

router = APIRouter(prefix="/crm", tags=["CRM"])

class CustomerRequest(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    source: Optional[str] = "manual"
    notes: Optional[str] = None
    session_id: Optional[str] = None

class ChatSyncRequest(BaseModel):
    session_id: str
    message: str
    sentiment_score: Optional[float] = None

class CustomerUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class DealRequest(BaseModel):
    customer_id: int
    title: str
    value: float
    stage: str = "lead"
    probability: int = 50
    expected_close: str
    notes: Optional[str] = None

class DealUpdateRequest(BaseModel):
    title: Optional[str] = None
    value: Optional[float] = None
    stage: Optional[str] = None
    probability: Optional[int] = None
    expected_close: Optional[str] = None
    notes: Optional[str] = None

class AutoCreateRequest(BaseModel):
    name: str
    email: str
    source: str
    type_str: str
    description: str
    sentiment_score: Optional[float] = None

class CustomerNotesRequest(BaseModel):
    notes: str

class CustomerTagsRequest(BaseModel):
    tags: str

# --- CUSTOMERS ---

@router.get("/customers")
def list_customers():
    return get_customers()

@router.post("/customers")
def new_customer(req: CustomerRequest):
    if req.session_id:
        extracted = {
            "name": req.name if req.name and req.name != "Chat User" else None,
            "email": req.email,
            "phone": req.phone,
            "company": req.company,
        }
        result = upsert_customer_from_chat(
            req.session_id, extracted, message_snippet=req.notes or "Manual CRM update via chat session"
        )
        return result

    cid = create_customer(req.name, req.email, req.phone, req.company, req.source, req.notes)
    log_activity(cid, "note", "Customer profile created manually")
    return {"id": cid, "customer_id": cid, "created": True}

@router.post("/customers/from-chat")
def sync_from_chat(req: ChatSyncRequest):
    """Extract customer info from a chat message and create/update CRM profile."""
    extracted = extract_customer_info(req.message)
    result = upsert_customer_from_chat(
        req.session_id, extracted, req.sentiment_score, req.message
    )
    return result

@router.get("/customers/{cid}")
def fetch_customer(cid: int):
    c = get_customer(cid)
    if not c: raise HTTPException(404, "Not found")
    return c

@router.put("/customers/{cid}")
def modify_customer(cid: int, req: CustomerUpdateRequest):
    update_customer(cid, req.model_dump(exclude_unset=True))
    return {"success": True}

@router.delete("/customers/{cid}")
def remove_customer(cid: int):
    delete_customer(cid)
    return {"success": True}

@router.get("/customers/{cid}/profile")
def full_profile(cid: int):
    p = get_customer_full_profile(cid)
    if not p: raise HTTPException(404, "Not found")
    return p

@router.get("/customers/{cid}/timeline")
def timeline(cid: int):
    return get_customer_timeline(cid)

@router.post("/customers/{cid}/risk-score")
def risk_score(cid: int):
    c = get_customer(cid)
    t = get_customer_timeline(cid)
    result = calculate_risk_score(c, t)
    
    # Update DB
    if "risk_score" in result:
        update_customer(cid, {"risk_score": result["risk_score"]})
        log_activity(cid, "note", f"AI Risk Update: {result.get('reason', '')}")
        
    return result

@router.post("/customers/{cid}/recalculate-risk")
def recalculate_risk(cid: int):
    return risk_score(cid)

@router.post("/customers/{cid}/summary")
def summary(cid: int):
    c = get_customer(cid)
    t = get_customer_timeline(cid)
    return generate_customer_summary(c, t)

@router.post("/customers/{cid}/update-notes")
def update_notes(cid: int, req: CustomerNotesRequest):
    update_customer(cid, {"notes": req.notes})
    return {"success": True}

@router.post("/customers/{cid}/update-tags")
def update_tags(cid: int, req: CustomerTagsRequest):
    update_customer(cid, {"tags": req.tags})
    return {"success": True}

@router.post("/customers/auto-create")
def auto_create(req: AutoCreateRequest):
    """Called by other modules (Email, LiveChat) to link activity."""
    customers = get_customers()
    existing = next((c for c in customers if c['email'] == req.email), None)
    
    if existing:
        cid = existing['id']
    else:
        cid = create_customer(req.name, req.email, None, None, req.source, "")
        log_activity(cid, "note", f"Auto-created from {req.source}")
        
    log_activity(cid, req.type_str, req.description, req.sentiment_score)
    return {"customer_id": cid}

# --- DEALS ---

@router.get("/deals")
def list_deals():
    return get_deals()

@router.post("/deals")
def new_deal(req: DealRequest):
    did = create_deal(req.customer_id, req.title, req.value, req.stage, req.probability, req.expected_close, req.notes)
    log_activity(req.customer_id, "deal", f"Deal created: {req.title} (${req.value})", deal_id=did)
    return {"id": did}

@router.put("/deals/{did}")
def modify_deal(did: int, req: DealUpdateRequest):
    update_deal(did, req.model_dump(exclude_unset=True))
    return {"success": True}

@router.delete("/deals/{did}")
def remove_deal(did: int):
    delete_deal(did)
    return {"success": True}

@router.get("/pipeline")
def pipeline():
    deals = get_deals()
    stages = ["lead", "qualified", "proposal", "negotiation", "won", "lost"]
    res = {s: {"total_value": 0, "deals": []} for s in stages}
    
    for d in deals:
        s = d['stage']
        if s not in res: continue
        res[s]["deals"].append(d)
        res[s]["total_value"] += d['value']
        
    return res

# --- STATS & FORECAST ---

@router.get("/stats")
def stats():
    return get_crm_stats()

@router.post("/forecast")
def forecast():
    deals = get_deals()
    return generate_forecast(deals)
