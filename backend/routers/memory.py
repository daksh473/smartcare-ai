from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import store_memory, get_memories_for_customer, backfill_memories_from_db
from ai.memory_ai import (
    build_memory_context, summarize_customer, get_customer_profile_for_dashboard
)

router = APIRouter(prefix="/memory", tags=["Memory"])


class StoreMemoryRequest(BaseModel):
    customer_identifier: str
    memory_type: str
    key: str
    value: str
    importance: float = 0.5
    session_id: Optional[str] = None


@router.post("/store")
def store_memory_endpoint(req: StoreMemoryRequest):
    result = store_memory(
        req.session_id or "",
        req.customer_identifier,
        req.memory_type,
        req.key,
        req.value,
        req.importance
    )
    return {"success": True, "memory": result}


@router.get("/profile/{customer_identifier}")
def get_profile(customer_identifier: str):
    return get_customer_profile_for_dashboard(customer_identifier)


@router.get("/{customer_identifier}")
def get_memories(customer_identifier: str):
    memories = get_memories_for_customer(customer_identifier)
    return {"customer_identifier": customer_identifier, "memories": memories, "count": len(memories)}


@router.post("/summarize/{customer_identifier}")
def summarize(customer_identifier: str):
    summary = summarize_customer(customer_identifier)
    if not summary:
        raise HTTPException(status_code=404, detail="No data to summarize")
    return summary


@router.post("/context/{customer_identifier}")
def get_context(customer_identifier: str):
    context, count = build_memory_context(customer_identifier)
    return {"customer_identifier": customer_identifier, "context": context, "memory_count": count}


@router.post("/backfill")
def backfill():
    return backfill_memories_from_db()
