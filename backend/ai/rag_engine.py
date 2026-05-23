import json
from models import KBResult
import math

# Mock database of FAQs with pre-computed embeddings
MOCK_FAQ_DB = [
    {
        "id": "faq_1",
        "question": "What is the refund policy?",
        "answer": "You can request a refund within 30 days of purchase.",
        "embedding": [0.1, 0.2, 0.3] # Mock embedding
    },
    {
        "id": "faq_2",
        "question": "How do I track my order?",
        "answer": "You can track your order using the tracking link sent to your email.",
        "embedding": [0.4, 0.5, 0.6]
    }
]

def cosine_similarity(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    if not magnitude1 or not magnitude2:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)

def generate_embedding(text: str) -> list[float]:
    # In a real app, call OpenAI/Groq embedding model here.
    # For now, return a random vector.
    return [0.1, 0.2, 0.3]

def search_knowledge_base(query: str, top_k: int = 3) -> list[KBResult]:
    query_emb = generate_embedding(query)
    results = []
    
    for faq in MOCK_FAQ_DB:
        score = cosine_similarity(query_emb, faq["embedding"])
        results.append(KBResult(question=faq["question"], answer=faq["answer"], score=score))
    
    results.sort(key=lambda x: x.score, reverse=True)
    return results[:top_k]

def inject_context(base_prompt: str, kb_results: list[KBResult]) -> str:
    if not kb_results:
        return base_prompt
        
    context = "\nRelevant FAQ context:\n"
    for idx, res in enumerate(kb_results):
        context += f"{idx+1}. Q: {res.question}\n   A: {res.answer}\n"
        
    return base_prompt + "\n" + context
