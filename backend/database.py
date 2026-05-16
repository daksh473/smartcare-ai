import sqlite3
import json
from datetime import datetime

DB_PATH = "smartcare.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            message   TEXT NOT NULL,
            score     REAL NOT NULL,
            emotion   TEXT NOT NULL,
            action    TEXT NOT NULL,
            reply     TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_conversation(message, score, emotion, action, reply):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO conversations (message, score, emotion, action, reply, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (message, score, emotion, action, reply, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_all_conversations():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM conversations ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r[0], "message": r[1], "score": r[2],
            "emotion": r[3], "action": r[4], "reply": r[5], "timestamp": r[6]
        }
        for r in rows
    ]

# Test
if __name__ == "__main__":
    init_db()
    save_conversation("Test message", 0.5, "neutral", "NORMAL", "Test reply")
    data = get_all_conversations()
    print(f"DB mein {len(data)} conversation(s) saved!")
    print(data[0])