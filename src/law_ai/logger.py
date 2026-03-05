import sqlite3
import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "data", "audit_trail.db")

def init_db():
    """Creates the SQLite database and table if it doesn't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Added user_id, case_id, and title for sidebar management
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS query_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            case_id TEXT,
            title TEXT,
            timestamp TEXT,
            user_query TEXT,
            ai_response TEXT,
            sources TEXT,
            confidence_score REAL,
            inference_time_sec REAL,
            veracity_status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_interaction(query: str, response: str, sources: list, confidence: float, duration: float, status: str, user_id: str = "anonymous", case_id: str = None, title: str = "New Case"):
    """Silently logs the AI interaction to the local database attached to a specific case."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sources_json = json.dumps(sources)

        cursor.execute('''
            INSERT INTO query_logs
            (user_id, case_id, title, timestamp, user_query, ai_response, sources, confidence_score, inference_time_sec, veracity_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, case_id, title, timestamp, query, response, sources_json, confidence, duration, status))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Telemetry Warning: Could not log to audit database. {e}")

def get_user_cases(user_id: str):
    """Fetches unique cases for the frontend sidebar."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get the most recent interaction for each case
        cursor.execute('''
            SELECT case_id, title, MAX(timestamp) as last_updated
            FROM query_logs
            WHERE user_id = ? AND case_id IS NOT NULL
            GROUP BY case_id
            ORDER BY last_updated DESC
        ''', (user_id,))

        cases = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return cases
    except Exception as e:
        print(f"⚠️ Could not fetch cases. {e}")
        return []

def get_case_history(case_id: str, limit: int = 2) -> str:
    """Fetches past conversation for a specific case to feed into the LLM context."""
    if not case_id:
        return ""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_query, ai_response
            FROM query_logs
            WHERE case_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (case_id, limit))

        # Reverse to get chronological order (oldest first)
        rows = cursor.fetchall()[::-1]
        conn.close()

        history_str = ""
        for user_q, ai_resp in rows:
            history_str += f"User: {user_q}\nAssistant: {ai_resp}\n"
        return history_str
    except Exception as e:
        print(f"⚠️ Could not fetch case history. {e}")
        return ""


def get_case_messages(case_id: str):
    """Fetches the full conversation for the UI when a case is clicked."""
    if not case_id:
        return []
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Fetch all messages for this case in chronological order
        cursor.execute('''
            SELECT user_query, ai_response, veracity_status, confidence_score
            FROM query_logs
            WHERE case_id = ?
            ORDER BY timestamp ASC
        ''', (case_id,))

        rows = cursor.fetchall()
        conn.close()

        messages = []
        for row in rows:
            # Add user question
            messages.append({"role": "user", "content": row["user_query"], "status": None, "confidence": None})
            # Add AI answer
            messages.append({
                "role": "ai",
                "content": row["ai_response"],
                "status": row["veracity_status"],
                "confidence": row["confidence_score"]
            })
        return messages
    except Exception as e:
        print(f"⚠️ Could not fetch case messages. {e}")
        return []

def delete_case(case_id: str):
    """Deletes all messages associated with a specific case."""
    if not case_id:
        return False
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Delete all rows matching the case_id
        cursor.execute('DELETE FROM query_logs WHERE case_id = ?', (case_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ Could not delete case. {e}")
        return False
