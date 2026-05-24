import sqlite3
import json
from datetime import datetime

DB_PATH = "smartcare.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS tickets')
    cursor.execute('DROP TABLE IF EXISTS conversations')
    cursor.execute('DROP TABLE IF EXISTS knowledge_base')
    cursor.execute('DROP TABLE IF EXISTS voice_metadata')
    cursor.execute('DROP TABLE IF EXISTS emails')
    cursor.execute('DROP TABLE IF EXISTS customers')
    cursor.execute('DROP TABLE IF EXISTS deals')
    cursor.execute('DROP TABLE IF EXISTS activities')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            issue TEXT NOT NULL,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            created_at TEXT NOT NULL,
            resolved_at TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            sentiment_score REAL NOT NULL,
            emotion TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT NOT NULL,
            usage_count INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            language TEXT,
            confidence REAL,
            timestamp TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT UNIQUE,
            sender TEXT,
            subject TEXT,
            body TEXT,
            sentiment_score REAL,
            emotion TEXT,
            action TEXT,
            ticket_id INTEGER,
            reply_sent TEXT,
            reply_sent_at TEXT,
            received_at TEXT,
            status TEXT DEFAULT 'pending'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            company TEXT,
            source TEXT,
            status TEXT DEFAULT 'lead',
            risk_score REAL DEFAULT 0.5,
            total_conversations INTEGER DEFAULT 0,
            avg_sentiment REAL DEFAULT 0.5,
            total_tickets INTEGER DEFAULT 0,
            revenue_generated REAL DEFAULT 0,
            created_at TEXT,
            last_contact TEXT,
            notes TEXT,
            tags TEXT
        )
    ''')

    try:
        cursor.execute("ALTER TABLE customers ADD COLUMN tags TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            title TEXT,
            value REAL,
            stage TEXT,
            probability INTEGER,
            expected_close TEXT,
            created_at TEXT,
            updated_at TEXT,
            notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            deal_id INTEGER,
            type TEXT,
            description TEXT,
            sentiment_score REAL,
            created_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')
    
    # Seed Knowledge Base
    cursor.execute('SELECT COUNT(*) FROM knowledge_base')
    if cursor.fetchone()[0] == 0:
        faqs = [
            ("What are your shipping times?", "Standard shipping takes 3-5 business days. Expedited takes 1-2 business days.", "shipping"),
            ("Do you ship internationally?", "Yes, we ship to over 50 countries globally. International shipping takes 7-14 days.", "shipping"),
            ("How do I return a product?", "You can return any unused product within 30 days of receipt. Visit your account to print a return label.", "refund"),
            ("When will I get my refund?", "Refunds are processed within 3-5 business days after we receive the returned item.", "refund"),
            ("How do I reset my password?", "Click 'Forgot Password' on the login screen. We will send a reset link to your registered email.", "account"),
            ("Can I change my email address?", "Yes, go to Account Settings > Profile to update your email address.", "account"),
            ("Are your products vegan?", "Yes, all our products are 100% vegan and cruelty-free.", "product"),
            ("Do you offer samples?", "We include 2 free samples with every order above $50.", "product"),
            ("What payment methods do you accept?", "We accept Visa, Mastercard, American Express, PayPal, and Apple Pay.", "payment"),
            ("Why was my card declined?", "Please check your billing address and CVV. If the problem persists, contact your bank.", "payment")
        ]
        cursor.executemany('INSERT INTO knowledge_base (question, answer, category, usage_count) VALUES (?, ?, ?, 0)', faqs)
        
    conn.commit()
    conn.close()

# -----------------
# TICKETS FUNCTIONS
# -----------------
def create_ticket(customer_name: str, issue: str, score: float):
    priority = "LOW"
    if score < 0.3:
        priority = "HIGH"
    elif score <= 0.7:
        priority = "MEDIUM"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tickets (customer_name, issue, status, priority, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (customer_name, issue, "OPEN", priority, datetime.now().isoformat()))
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_ticket(ticket_id)

def get_all_tickets():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tickets ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_ticket(ticket_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def resolve_ticket(ticket_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tickets SET status = "RESOLVED", resolved_at = ? WHERE id = ?
    ''', (datetime.now().isoformat(), ticket_id))
    conn.commit()
    conn.close()
    return get_ticket(ticket_id)

def get_tickets_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM tickets')
    total = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM tickets WHERE status = "OPEN"')
    open_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM tickets WHERE status = "RESOLVED"')
    resolved_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM tickets WHERE priority = "HIGH"')
    high_priority = cursor.fetchone()[0]
    conn.close()
    return {
        "total": total,
        "open": open_count,
        "resolved": resolved_count,
        "high_priority": high_priority
    }

# -----------------------
# CONVERSATION FUNCTIONS
# -----------------------
def save_conversation_message(session_id: str, role: str, message: str, sentiment_score: float, emotion: str, action: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO conversations (session_id, role, message, sentiment_score, emotion, action, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (session_id, role, message, sentiment_score, emotion, action, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Legacy function for backward compatibility
def save_conversation(message: str, score: float, emotion: str, action: str, reply: str):
    save_conversation_message("legacy", "user", message, score, emotion, action)
    save_conversation_message("legacy", "assistant", reply, score, emotion, action)

def get_conversation_history(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM conversations WHERE session_id = ? ORDER BY timestamp ASC', (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Legacy function for backward compatibility
def get_all_conversations():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Mock the old schema by fetching user messages and pairing them (not ideal, but serves legacy UI)
    cursor.execute('SELECT * FROM conversations WHERE role = "user" ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    
    legacy_format = []
    for r in rows:
        legacy_format.append({
            "id": r["id"],
            "message": r["message"],
            "score": r["sentiment_score"],
            "emotion": r["emotion"],
            "action": r["action"],
            "reply": "Reply via legacy", # Simplified for legacy
            "timestamp": r["timestamp"]
        })
    return legacy_format

# -------------------------
# KNOWLEDGE BASE FUNCTIONS
# -------------------------
def get_all_kb_entries():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM knowledge_base ORDER BY usage_count DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_kb_entry(question: str, answer: str, category: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO knowledge_base (question, answer, category, usage_count)
        VALUES (?, ?, ?, 0)
    ''', (question, answer, category))
    conn.commit()
    conn.close()

def increment_kb_usage(kb_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE knowledge_base SET usage_count = usage_count + 1 WHERE id = ?
    ''', (kb_id,))
    conn.commit()
    conn.close()

# -------------------------
# ANALYTICS FUNCTIONS
# -------------------------
def get_analytics_overview():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Total conversations (user messages only)
    cursor.execute('SELECT COUNT(*) FROM conversations WHERE role = "user"')
    total_conversations = cursor.fetchone()[0]

    # Total tickets
    cursor.execute('SELECT COUNT(*) FROM tickets')
    total_tickets = cursor.fetchone()[0]

    # Resolution rate
    cursor.execute('SELECT COUNT(*) FROM tickets WHERE status = "RESOLVED"')
    resolved = cursor.fetchone()[0]
    resolution_rate = round((resolved / total_tickets * 100), 1) if total_tickets > 0 else 0.0

    # Avg sentiment
    cursor.execute('SELECT AVG(sentiment_score) FROM conversations WHERE role = "user"')
    avg_score_row = cursor.fetchone()[0]
    avg_sentiment_score = round(avg_score_row, 3) if avg_score_row else 0.0

    # Escalation rate
    cursor.execute('SELECT COUNT(*) FROM conversations WHERE role = "user" AND action = "ESCALATE"')
    escalations = cursor.fetchone()[0]
    escalation_rate = round((escalations / total_conversations * 100), 1) if total_conversations > 0 else 0.0

    # Upsell rate
    cursor.execute('SELECT COUNT(*) FROM conversations WHERE role = "user" AND action = "UPSELL"')
    upsells = cursor.fetchone()[0]
    upsell_rate = round((upsells / total_conversations * 100), 1) if total_conversations > 0 else 0.0

    # Busiest hour
    cursor.execute("""
        SELECT CAST(strftime('%H', timestamp) AS INTEGER) as hour, COUNT(*) as cnt
        FROM conversations WHERE role = 'user'
        GROUP BY hour ORDER BY cnt DESC LIMIT 1
    """)
    busiest = cursor.fetchone()
    busiest_hour = busiest[0] if busiest else 0

    conn.close()
    return {
        "total_conversations": total_conversations,
        "total_tickets": total_tickets,
        "resolution_rate": resolution_rate,
        "avg_sentiment_score": avg_sentiment_score,
        "avg_response_time_ms": 950,  # Mocked — no real ms tracking in DB
        "escalation_rate": escalation_rate,
        "upsell_rate": upsell_rate,
        "busiest_hour": busiest_hour
    }

def get_sentiment_trend():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DATE(timestamp) as dt, AVG(sentiment_score) as avg_score, COUNT(*) as cnt
        FROM conversations WHERE role = 'user'
        AND DATE(timestamp) >= DATE('now', '-7 days')
        GROUP BY dt ORDER BY dt ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{"date": r[0], "avg_score": round(r[1], 3), "count": r[2]} for r in rows]

def get_emotion_breakdown():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT emotion, COUNT(*) as cnt
        FROM conversations WHERE role = 'user'
        GROUP BY emotion ORDER BY cnt DESC
    """)
    rows = cursor.fetchall()
    total = sum(r[1] for r in rows)
    conn.close()
    return [
        {"emotion": r[0], "count": r[1], "percentage": round(r[1] / total * 100, 1) if total > 0 else 0}
        for r in rows
    ]

def get_action_distribution():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT action, COUNT(*) as cnt
        FROM conversations WHERE role = 'user'
        GROUP BY action
    """)
    rows = cursor.fetchall()
    conn.close()
    result = {"ESCALATE": 0, "NORMAL": 0, "UPSELL": 0}
    for r in rows:
        if r[0] in result:
            result[r[0]] = r[1]
    return result

def get_hourly_activity():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT CAST(strftime('%H', timestamp) AS INTEGER) as hour, COUNT(*) as cnt
        FROM conversations WHERE role = 'user'
        AND DATE(timestamp) = DATE('now')
        GROUP BY hour ORDER BY hour ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{"hour": r[0], "count": r[1]} for r in rows]

def get_all_ticket_issues():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT issue FROM tickets ORDER BY created_at DESC LIMIT 100')
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

def save_voice_metadata(session_id: str, language: str, confidence: float):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO voice_metadata (session_id, language, confidence, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (session_id, language, confidence, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_voice_analytics():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM voice_metadata')
    total_voice = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(confidence) FROM voice_metadata')
    avg_conf_row = cursor.fetchone()[0]
    avg_confidence = round(avg_conf_row, 3) if avg_conf_row else 0.0
    
    cursor.execute('''
        SELECT language, COUNT(*) as cnt FROM voice_metadata
        GROUP BY language ORDER BY cnt DESC LIMIT 1
    ''')
    lang_row = cursor.fetchone()
    most_common_lang = lang_row[0] if lang_row else "N/A"
    
    conn.close()
    return {
        "total_voice_conversations": total_voice,
        "most_common_language": most_common_lang,
        "avg_confidence_score": avg_confidence
    }

def save_email(message_id, sender, subject, body, score, emotion, action, ticket_id, received_at):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO emails (message_id, sender, subject, body, sentiment_score, emotion, action, ticket_id, received_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (message_id, sender, subject, body, score, emotion, action, ticket_id, received_at))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Already exists
    conn.close()

def get_all_emails():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM emails ORDER BY received_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_email_status(email_id, status, reply_sent, reply_sent_at):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE emails SET status = ?, reply_sent = ?, reply_sent_at = ? WHERE id = ?
    ''', (status, reply_sent, reply_sent_at, email_id))
    conn.commit()
    conn.close()

def get_email_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM emails')
    total = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM emails WHERE status = "pending"')
    pending = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM emails WHERE status = "replied"')
    replied = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM emails WHERE action = "ESCALATE"')
    escalated = cursor.fetchone()[0]
    cursor.execute('SELECT AVG(sentiment_score) FROM emails')
    avg_score = cursor.fetchone()[0]
    conn.close()
    return {
        "total_received": total,
        "pending": pending,
        "replied": replied,
        "escalated": escalated,
        "avg_sentiment": round(avg_score, 3) if avg_score else 0.0
    }

# ==========================================
# CRM DATABASE FUNCTIONS
# ==========================================

def get_customers():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM customers ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_customer(customer_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_customer_full_profile(customer_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
    customer_row = cursor.fetchone()
    if not customer_row:
        conn.close()
        return None
        
    customer = dict(customer_row)
    
    # Timeline
    cursor.execute('SELECT * FROM activities WHERE customer_id = ? ORDER BY created_at DESC', (customer_id,))
    timeline = [dict(r) for r in cursor.fetchall()]
    
    # Deals
    cursor.execute('SELECT * FROM deals WHERE customer_id = ? ORDER BY created_at DESC', (customer_id,))
    deals = [dict(r) for r in cursor.fetchall()]
    
    # Emails
    if customer.get('email'):
        cursor.execute('SELECT * FROM emails WHERE sender LIKE ? ORDER BY received_at DESC', (f"%{customer['email']}%",))
        emails = [dict(r) for r in cursor.fetchall()]
        
        # Tickets
        cursor.execute('SELECT * FROM tickets WHERE contact_info = ? ORDER BY timestamp DESC', (customer['email'],))
        tickets = [dict(r) for r in cursor.fetchall()]
    else:
        emails = []
        tickets = []
        
    conn.close()
    
    # Merge activities with emails and tickets for a master timeline
    master_timeline = timeline.copy()
    
    for em in emails:
        master_timeline.append({
            "type": "email",
            "description": f"Email: {em['subject']}",
            "sentiment_score": em['sentiment_score'],
            "created_at": em['received_at']
        })
        
    for tk in tickets:
        master_timeline.append({
            "type": "ticket",
            "description": f"Ticket #{tk['id']} - {tk['issue']}",
            "sentiment_score": tk['sentiment'],
            "created_at": tk['timestamp']
        })
        
    # Sort descending
    master_timeline.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Sentiment trend: last 10 interactions with valid sentiment
    sentiment_trend = [t for t in master_timeline if t.get('sentiment_score') is not None][:10]
    sentiment_trend.reverse() # chronological order for charting
    
    # Interactions count
    total_interactions = len(master_timeline)
    
    return {
        "profile": customer,
        "timeline": master_timeline,
        "deals": deals,
        "emails": emails,
        "tickets": tickets,
        "sentiment_trend": sentiment_trend,
        "total_interactions": total_interactions
    }

def create_customer(name, email, phone, company, source, notes):
    from datetime import datetime
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO customers (name, email, phone, company, source, created_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, phone, company, source, datetime.now().isoformat(), notes))
        conn.commit()
        customer_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        cursor.execute('SELECT id FROM customers WHERE email = ?', (email,))
        customer_id = cursor.fetchone()[0]
    conn.close()
    return customer_id

def update_customer(customer_id, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    fields = []
    values = []
    for k, v in data.items():
        fields.append(f"{k} = ?")
        values.append(v)
    values.append(customer_id)
    cursor.execute(f'''
        UPDATE customers SET {', '.join(fields)} WHERE id = ?
    ''', tuple(values))
    conn.commit()
    conn.close()

def delete_customer(customer_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
    cursor.execute('DELETE FROM activities WHERE customer_id = ?', (customer_id,))
    cursor.execute('DELETE FROM deals WHERE customer_id = ?', (customer_id,))
    conn.commit()
    conn.close()

def log_activity(customer_id, type_str, description, sentiment_score=None, deal_id=None):
    from datetime import datetime
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO activities (customer_id, deal_id, type, description, sentiment_score, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (customer_id, deal_id, type_str, description, sentiment_score, datetime.now().isoformat()))
    
    # Update customer last_contact and re-calculate averages
    cursor.execute('SELECT AVG(sentiment_score), COUNT(*) FROM activities WHERE customer_id = ? AND sentiment_score IS NOT NULL', (customer_id,))
    res = cursor.fetchone()
    avg_sent = res[0] or 0.5
    total_convs = res[1] or 0
    
    cursor.execute('''
        UPDATE customers 
        SET last_contact = ?, avg_sentiment = ?, total_conversations = ?
        WHERE id = ?
    ''', (datetime.now().isoformat(), avg_sent, total_convs, customer_id))
    
    conn.commit()
    conn.close()

def get_customer_timeline(customer_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM activities WHERE customer_id = ? ORDER BY created_at DESC', (customer_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_deal(customer_id, title, value, stage, probability, expected_close, notes):
    from datetime import datetime
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO deals (customer_id, title, value, stage, probability, expected_close, created_at, updated_at, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (customer_id, title, value, stage, probability, expected_close, now, now, notes))
    conn.commit()
    deal_id = cursor.lastrowid
    conn.close()
    return deal_id

def get_deals():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT d.*, c.name as customer_name 
        FROM deals d 
        LEFT JOIN customers c ON d.customer_id = c.id
        ORDER BY d.created_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_deal(deal_id, data):
    from datetime import datetime
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    fields = []
    values = []
    for k, v in data.items():
        fields.append(f"{k} = ?")
        values.append(v)
    
    fields.append("updated_at = ?")
    values.append(datetime.now().isoformat())
    
    values.append(deal_id)
    cursor.execute(f'''
        UPDATE deals SET {', '.join(fields)} WHERE id = ?
    ''', tuple(values))
    conn.commit()
    conn.close()

def delete_deal(deal_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM deals WHERE id = ?', (deal_id,))
    conn.commit()
    conn.close()

def get_crm_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM customers')
    total_customers = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT COUNT(*) FROM customers WHERE risk_score < 0.3')
    at_risk_customers = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT SUM(value) FROM deals')
    total_deals_value = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT SUM(value) FROM deals WHERE stage = "won"')
    won_deals_value = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT COUNT(*) FROM deals WHERE stage = "won"')
    won_count = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT COUNT(*) FROM deals')
    total_deals = cursor.fetchone()[0] or 0
    
    conversion_rate = (won_count / total_deals * 100) if total_deals > 0 else 0
    
    from datetime import datetime, timedelta
    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
    cursor.execute('SELECT COUNT(*) FROM customers WHERE created_at > ?', (thirty_days_ago,))
    new_this_month = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "total_customers": total_customers,
        "new_this_month": new_this_month,
        "total_deals_value": total_deals_value,
        "won_deals_value": won_deals_value,
        "conversion_rate": round(conversion_rate, 1),
        "at_risk_customers": at_risk_customers
    }