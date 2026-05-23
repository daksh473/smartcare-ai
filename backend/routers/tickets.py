from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import create_ticket, get_all_tickets, get_ticket, resolve_ticket, get_tickets_stats

router = APIRouter(prefix="/tickets", tags=["Tickets"])

class TicketCreateRequest(BaseModel):
    customer_name: str
    issue: str
    sentiment_score: float

@router.post("/create")
def create_new_ticket(req: TicketCreateRequest):
    ticket = create_ticket(req.customer_name, req.issue, req.sentiment_score)
    return {"message": "Ticket created successfully", "ticket": ticket}

@router.get("")
def list_tickets():
    return get_all_tickets()

@router.patch("/{ticket_id}/resolve")
def resolve_existing_ticket(ticket_id: int):
    ticket = resolve_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"message": "Ticket resolved", "ticket": ticket}

@router.get("/stats")
def tickets_stats():
    return get_tickets_stats()
