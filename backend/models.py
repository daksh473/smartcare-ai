from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

class Channel(str, Enum):
    WHATSAPP = "WHATSAPP"
    WEBCHAT = "WEBCHAT"
    EMAIL = "EMAIL"
    TWITTER = "TWITTER"
    INSTAGRAM = "INSTAGRAM"

class TicketStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class UrgencyLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class UnifiedMessage(BaseModel):
    channel: Channel
    sender_id: str
    content: str
    media_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TicketClassification(BaseModel):
    sentiment_score: float
    emotion: str
    intent: str
    urgency_level: UrgencyLevel
    ai_reply: Optional[str] = None

class EscalationResult(BaseModel):
    queue: str
    priority: str

class KBResult(BaseModel):
    question: str
    answer: str
    score: float

class CustomerTier(str, Enum):
    VIP = "VIP"
    STANDARD = "STANDARD"
    NEW = "NEW"

class SentimentDataPoint(BaseModel):
    timestamp: str
    score: float

class CustomerProfile(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    tier: CustomerTier
    lifetime_value: float = 0.0
    order_count: int = 0
    is_repeat_complaint: bool = False
    sentiment_history: List[SentimentDataPoint] = Field(default_factory=list)

class WorkflowResult(BaseModel):
    status: str
    action_taken: str
    customer_message: str

class TicketResponse(BaseModel):
    id: int
    channel: Channel
    sender_id: str
    content: str
    sentiment_score: float
    emotion: str
    intent: str
    urgency_level: UrgencyLevel
    status: TicketStatus
    assigned_agent: Optional[str] = None
    created_at: str
    resolved_at: Optional[str] = None
    reply: Optional[str] = None
