# escalation_engine.py
from models import TicketClassification, CustomerProfile, EscalationResult

def evaluate_escalation(ticket: TicketClassification, customer: CustomerProfile) -> EscalationResult:
    if ticket.sentiment_score < 0.3 or ticket.intent == 'legal_threat' or customer.is_repeat_complaint:
        return EscalationResult(queue='SUPERVISOR_QUEUE', priority='CRITICAL')
    elif customer.tier == 'VIP':
        return EscalationResult(queue='SENIOR_AGENT_QUEUE', priority='HIGH')
    elif ticket.urgency_level == 'HIGH':
        return EscalationResult(queue='STANDARD_QUEUE', priority='HIGH')
    return EscalationResult(queue='AUTO_RESOLVE', priority='NORMAL')
