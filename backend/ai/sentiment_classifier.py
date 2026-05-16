from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a sentiment analyzer. Analyze the user message and return 
ONLY a JSON like this: {"score": 0.2, "emotion": "frustrated"}
Score is 0.0 (very negative) to 1.0 (very positive). Nothing else."""

def analyze_sentiment(message: str) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        max_tokens=50,
        temperature=0
    )
    raw = response.choices[0].message.content.strip()
    return json.loads(raw)

def decide_action(score: float) -> str:
    if score < 0.3:
        return "ESCALATE"    # human agent alert
    elif score > 0.7:
        return "UPSELL"      # offer bhejo
    else:
        return "NORMAL"      # normal reply

# Test
if __name__ == "__main__":
    test_messages = [
        "Yeh kya bakwaas service hai!",
        "Theek hai, chalta hai",
        "Bahut acha experience tha, shukriya!",
        "Mera paisa wapas karo abhi",
        "Mujhe aur products dekhne hain"
    ]
    
    print(f"{'Message':<40} {'Score':<8} {'Emotion':<12} {'Action'}")
    print("-" * 75)
    
    for msg in test_messages:
        result = analyze_sentiment(msg)
        action = decide_action(result["score"])
        print(f"{msg[:38]:<40} {result['score']:<8} {result['emotion']:<12} {action}")