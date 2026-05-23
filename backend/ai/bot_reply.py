from groq import Groq
import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROMPTS = {
    "ESCALATE": """You are a empathetic customer service bot. 
The customer is angry or frustrated. 
Apologize sincerely, acknowledge their problem, and tell them a human agent will help them shortly and a ticket has been auto-created.
Reply in the same language as the customer (Hindi or English).
Keep it under 2 sentences.""",

    "NORMAL": """You are a helpful customer service bot.
The customer has a normal query.
Answer helpfully and professionally using the conversation context if needed.
Reply in the same language as the customer (Hindi or English).
Keep it under 2 sentences.""",

    "UPSELL": """You are a friendly sales bot.
The customer is happy and satisfied.
Thank them warmly and offer them a special discount or upgrade.
Reply in the same language as the customer (Hindi or English).
Keep it under 2 sentences."""
}

def generate_reply(message: str, action: str, history: List[Dict[str, str]] = None) -> str:
    prompt = PROMPTS.get(action, PROMPTS["NORMAL"])
    
    messages = [{"role": "system", "content": prompt}]
    
    if history:
        # history structure: [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi"}]
        # Take up to last 10 messages for context
        messages.extend(history[-10:])
        
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# Test
if __name__ == "__main__":
    tests = [
        ("Yeh bakwaas service hai!", "ESCALATE"),
        ("Mera order status kya hai?", "NORMAL"),
        ("Bahut acha service hai shukriya!", "UPSELL"),
    ]
    for msg, action in tests:
        reply = generate_reply(msg, action)
        print(f"\n[{action}] Customer: {msg}")
        print(f"Bot: {reply}")