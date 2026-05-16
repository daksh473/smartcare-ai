# 🤖 SentimentAI — Real-time Emotion Intelligence Bot

> **Zint AI Hackathon 2026** | Built by Daksh Pareek, Priyanshu Sharma, Sannidhi Paul

A real-time AI-powered customer sentiment analysis platform that detects customer emotions, auto-routes conversations, generates intelligent replies, and alerts human agents — all in milliseconds.

---

## 🚀 Live Demo Flow

```
Customer types message
        ↓
AI detects emotion (score 0.0 → 1.0)
        ↓
   Score < 0.3        Score 0.3–0.7       Score > 0.7
      ↓                    ↓                   ↓
🚨 ESCALATE            💬 NORMAL            🎁 UPSELL
Human Agent Alert    Normal Bot Reply    Special Offer Sent
        ↓                    ↓                   ↓
   Saved to DB          Saved to DB         Saved to DB
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 Real-time Sentiment Analysis | Detects emotion score 0.0–1.0 per message |
| 🤖 AI Bot Reply | Context-aware reply in Hindi or English |
| 🚨 Escalation Alert | Dramatic popup when customer is frustrated |
| 🎁 Upsell Trigger | Auto-offer when customer is happy |
| 📊 Live Emotion Graph | Real-time area chart with emotion history |
| 💾 Conversation History | SQLite DB stores all conversations |
| 🌐 Bilingual UI | Full Hindi + English support |
| ⚡ WebSocket | True real-time, no page refresh needed |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Model | Groq API — LLaMA 3.3 70B |
| Backend | Python FastAPI + WebSocket |
| Frontend | React + Vite + Recharts |
| Database | SQLite |
| Styling | Inline CSS (no framework) |

---

## 📁 Project Structure

```
smartcare-ai/
├── backend/
│   ├── main.py                  # FastAPI server + WebSocket
│   ├── database.py              # SQLite init + save + fetch
│   ├── ai/
│   │   ├── sentiment_classifier.py  # Emotion score + action
│   │   └── bot_reply.py             # AI reply generator
│   ├── .env                     # API keys (not committed)
│   └── requirements.txt
├── frontend/
│   └── src/
│       └── App.jsx              # Full React dashboard
└── README.md
```

---

## ⚙️ Setup & Run

### Backend
```bash
cd backend
pip install fastapi uvicorn groq python-dotenv
# Add GROQ_API_KEY in .env file
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Open
```
http://localhost:5173
```

---

## 🎯 Evaluation Criteria Match

| Criteria | How We Address It |
|----------|------------------|
| Innovation & Creativity | Predictive emotion routing — not just a chatbot |
| Real-World Problem Solving | SME businesses lose customers due to poor support |
| Technical Architecture | WebSocket + FastAPI + React + SQLite + Groq AI |
| Scalability | Multi-tenant ready, stateless API design |
| Documentation & Presentation | Full README, architecture doc, live demo |

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Analyze a message (REST) |
| GET | `/history` | Get all conversations from DB |
| WS | `/ws` | Real-time WebSocket connection |

---

## 🏆Zint AI Hackathon 2026

Built for the FlowZint AI Hackathon 2026 — National Level Innovation Challenge.

**Focus areas addressed:** Innovation · Scalability · AI Automation · Customer Engagement · Intelligent Workflows
