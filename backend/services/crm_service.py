from models import CustomerProfile, CustomerTier, SentimentDataPoint
from typing import Dict
import random

# Mock CRM Database
MOCK_CUSTOMERS: Dict[str, CustomerProfile] = {
    "CUST001": CustomerProfile(
        id="CUST001",
        name="Alex Smith",
        email="alex.smith@example.com",
        phone="+1234567890",
        tier=CustomerTier.VIP,
        lifetime_value=2500.0,
        order_count=12,
        sentiment_history=[
            SentimentDataPoint(timestamp="2024-05-01T10:00:00", score=0.8),
            SentimentDataPoint(timestamp="2024-05-15T14:30:00", score=0.6),
            SentimentDataPoint(timestamp="2024-05-20T09:15:00", score=0.9),
        ]
    )
}

def fetch_customer_profile(customer_id: str) -> CustomerProfile:
    if customer_id in MOCK_CUSTOMERS:
        return MOCK_CUSTOMERS[customer_id]
    
    # Return a generated profile for unknown users
    return CustomerProfile(
        id=customer_id,
        name=f"Customer {customer_id[-4:]}",
        tier=CustomerTier.STANDARD,
        sentiment_history=[
            SentimentDataPoint(timestamp="2024-05-21T10:00:00", score=random.random())
        ]
    )

def get_sentiment_history(customer_id: str) -> list[SentimentDataPoint]:
    profile = fetch_customer_profile(customer_id)
    return profile.sentiment_history

def update_customer_record(customer_id: str, updates: dict):
    if customer_id in MOCK_CUSTOMERS:
        profile = MOCK_CUSTOMERS[customer_id]
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
