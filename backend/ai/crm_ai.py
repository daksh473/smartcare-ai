import os
import json
from groq import Groq

# Same initialization as other AI files
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "mixtral-8x7b-32768"

def calculate_risk_score(customer_data, timeline):
    """
    Uses Groq to calculate churn risk based on timeline sentiment.
    """
    timeline_summary = "\\n".join([f"[{t['created_at']}] {t['type']}: {t['description']} (Sentiment: {t.get('sentiment_score', 'N/A')})" for t in timeline[-10:]])
    
    prompt = f"""
    Analyze the following customer data and recent interactions to determine their churn risk.
    Customer: {customer_data['name']} (Avg Sentiment: {customer_data['avg_sentiment']})
    
    Recent Timeline:
    {timeline_summary}
    
    Provide your response in JSON format with three keys:
    1. "risk_score": A float between 0.0 (high risk of churn) and 1.0 (very safe/loyal).
    2. "reason": A brief 1-sentence explanation of why they have this score.
    3. "recommendation": A brief 1-sentence recommended action to improve or maintain their status.
    
    Respond ONLY with valid JSON.
    """
    
    try:
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an expert CRM AI that predicts customer churn. Output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        # Clean up if markdown block
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        data = json.loads(content)
        return data
    except Exception as e:
        print(f"Risk Score AI Error: {e}")
        return {"risk_score": 0.5, "reason": "Failed to analyze risk.", "recommendation": "Review manually."}

def generate_forecast(deals):
    """
    Uses Groq to predict revenue and pick top deals.
    """
    deals_summary = "\\n".join([f"[{d['id']}] {d['title']} - Value: ${d['value']} - Stage: {d['stage']} - Expected Close: {d['expected_close']}" for d in deals if d['stage'] not in ('won', 'lost')])
    
    prompt = f"""
    Analyze the following open deals pipeline and generate a revenue forecast.
    
    Active Deals:
    {deals_summary}
    
    Provide your response in JSON format with two keys:
    1. "forecast": An object with keys "30_days", "60_days", "90_days" representing projected revenue (floats).
    2. "top_deals": A list of 3 deal IDs (integers) that are most likely to close based on stage and proximity.
    
    Respond ONLY with valid JSON.
    """
    
    try:
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an expert Sales AI. Output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        data = json.loads(content)
        return data
    except Exception as e:
        print(f"Forecast AI Error: {e}")
        return {
            "forecast": {"30_days": 0, "60_days": 0, "90_days": 0},
            "top_deals": []
        }

def generate_customer_summary(customer_data, timeline):
    """
    Generates a brief overview of the customer relationship.
    """
    timeline_summary = "\\n".join([f"[{t['created_at']}] {t['type']}: {t['description']}" for t in timeline[-10:]])
    
    prompt = f"""
    Write a concise, 2-3 sentence executive summary of the relationship with this customer.
    Customer: {customer_data['name']} (Company: {customer_data['company']})
    
    Recent Activity:
    {timeline_summary}
    """
    
    try:
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful CRM assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Summary AI Error: {e}")
        return "Failed to generate summary."
