import logging
from database import save_csat_response

logger = logging.getLogger(__name__)

def dispatch_csat_survey(ticket_id: str):
    logger.info(f"Dispatching CSAT survey for ticket {ticket_id}")
    # In a real app, send an email/sms via a channel API

def record_csat_response(ticket_id: str, rating: int, feedback: str = ""):
    logger.info(f"Recorded CSAT for {ticket_id}: {rating} stars. Feedback: {feedback}")
    save_csat_response(ticket_id, rating, feedback)
