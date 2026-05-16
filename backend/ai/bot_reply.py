from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROMPTS = {
    "ESCALATE": """You are a empathetic customer service bot. 
The customer is angry or frustrated. 
Apologize sincerely, acknowledge their problem, and tell them a human agent will help them shortly.
Reply in the same language as the customer (Hindi or English).
Keep it under 2 sentences.""",

    "NORMAL": """You are a helpful customer service bot.
The customer has a normal query.
Answer helpfully and professionally.
Reply in the same language as the customer (Hindi or English).
Keep it under 2 sentences.""",

    "UPSELL": """You are a friendly sales bot.
The customer is happy and satisfied.
Thank them warmly and offer them a special discount or upgrade.
Reply in the same language as the customer (Hindi or English).
Keep it under 2 sentences."""
}

def generate_reply(message: str, action: str) -> str:
    prompt = PROMPTS.get(action, PROMPTS["NORMAL"])
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": message}
        ],
        max_tokens=100,
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