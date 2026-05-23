from fastapi import APIRouter
from database import (
    get_analytics_overview, get_sentiment_trend, get_emotion_breakdown,
    get_action_distribution, get_hourly_activity, get_all_ticket_issues,
    get_voice_analytics
)
from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.post("/overview")
def analytics_overview():
    return get_analytics_overview()

@router.post("/sentiment-trend")
def sentiment_trend():
    return get_sentiment_trend()

@router.post("/emotion-breakdown")
def emotion_breakdown():
    return get_emotion_breakdown()

@router.post("/action-distribution")
def action_distribution():
    return get_action_distribution()

@router.post("/hourly-activity")
def hourly_activity():
    return get_hourly_activity()

@router.post("/voice-stats")
def voice_stats():
    return get_voice_analytics()

@router.post("/top-issues")
def top_issues():
    issues = get_all_ticket_issues()
    if not issues:
        return [
            {"issue": "No tickets yet", "count": 0},
        ]
    
    issues_text = "\n".join(issues)
    prompt = f"""Analyze the following customer support ticket issues and identify the top 5 most recurring themes/categories.
For each theme, estimate how many tickets match it.

Ticket issues:
{issues_text}

Return STRICTLY a JSON array (no markdown, no code fences, just raw JSON):
[
  {{"issue": "Theme name", "count": estimated_count}},
  ...
]
Return exactly 5 items, sorted by count descending."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=300,
            temperature=0.0
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
        return json.loads(content)
    except Exception as e:
        print("Top Issues AI Error:", e)
        return [{"issue": "Analysis unavailable", "count": 0}]

@router.post("/customer-health-score")
def customer_health_score():
    overview = get_analytics_overview()
    
    prompt = f"""You are a customer experience analyst. Based on these metrics, compute a Customer Health Score (0-100) and provide insights.

Metrics:
- Total Conversations: {overview['total_conversations']}
- Total Tickets: {overview['total_tickets']}
- Resolution Rate: {overview['resolution_rate']}%
- Average Sentiment Score: {overview['avg_sentiment_score']} (0 = very negative, 1 = very positive)
- Escalation Rate: {overview['escalation_rate']}%
- Upsell Rate: {overview['upsell_rate']}%

Rules:
- Health Score formula: Start with 50. Add points for high sentiment (>0.6), high resolution rate (>70%), high upsell rate. Subtract points for high escalation rate (>20%), low sentiment (<0.4).
- Trend: "improving" if sentiment > 0.6, "declining" if sentiment < 0.35, else "stable".
- Provide exactly 3 short key insights (1 sentence each).

Return STRICTLY a JSON object (no markdown, no code fences, just raw JSON):
{{
  "score": int,
  "trend": "improving" | "declining" | "stable",
  "key_insights": ["insight1", "insight2", "insight3"]
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=300,
            temperature=0.0
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
        return json.loads(content)
    except Exception as e:
        print("Health Score AI Error:", e)
        return {
            "score": 50,
            "trend": "stable",
            "key_insights": [
                "Insufficient data for detailed analysis.",
                "Continue monitoring sentiment trends.",
                "Focus on reducing escalation rate."
            ]
        }
