
import sqlite3
import time
from typing import List, Dict, Optional
from threading import Lock

class RelationalDatabase:
    """
    Blazing Fast SQLite Wrapper for Relational Data.
    Handles Users, Analytics, and Global Config.
    Thread-safe and persistent.
    """
    _instance = None
    _lock = Lock()

    def __new__(cls, db_path="iitu_teacher_platform.db"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(RelationalDatabase, cls).__new__(cls)
                cls._instance.db_path = db_path
                cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        """Initialize schema with best-practice SQLite performance settings."""
        with sqlite3.connect(self.db_path) as conn:
            # Performance Tuning
            conn.execute("PRAGMA journal_mode = WAL;")  # Write-Ahead Logging for concurrency
            conn.execute("PRAGMA synchronous = NORMAL;") # Faster writes, safe enough
            conn.execute("PRAGMA foreign_keys = ON;")
            
            # Users Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at REAL DEFAULT (datetime('now', 'localtime'))
                )
            """)
            
            # Analytics Table (Cost Management)
            # Analytics Table (Cost Management)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id TEXT,
                    query_type TEXT, -- 'chat' or 'search'
                    processing_time_ms REAL,
                    tokens_saved INTEGER,
                    timestamp REAL DEFAULT (datetime('now', 'localtime'))
                )
            """)

            # Shared Chat History (Global Forum)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id TEXT,
                    user_id TEXT,
                    user_name TEXT,
                    question TEXT,
                    answer TEXT,
                    timestamp REAL DEFAULT (datetime('now', 'localtime'))
                )
            """)

    def get_connection(self):
        """Returns a connection for the caller context."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # Dictionary-like access
        return conn

    # --- USER REPOSITORY ---
    def create_user(self, email: str, password_hash: str, name: str, role: str):
        with self.get_connection() as conn:
            try:
                conn.execute(
                    "INSERT INTO users (email, password_hash, name, role) VALUES (?, ?, ?, ?)",
                    (email, password_hash, name, role)
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def get_user(self, email: str) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_users(self) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT email, name, role, created_at FROM users")
            return [dict(row) for row in cursor.fetchall()]

    def delete_user(self, email: str):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM users WHERE email = ?", (email,))
            conn.commit()

    # --- ANALYTICS REPOSITORY ---
    def log_usage(self, course_id: str, query_type: str, time_ms: float, tokens_saved: int = 0):
        """Log system efficiency metrics for cost analysis."""
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO usage_analytics (course_id, query_type, processing_time_ms, tokens_saved) VALUES (?, ?, ?, ?)",
                (course_id, query_type, time_ms, tokens_saved)
            )
            conn.commit()
            
    def get_cost_report(self):
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    SUM(tokens_saved) as total_tokens,
                    AVG(processing_time_ms) as avg_latency
                FROM usage_analytics
            """)
            row = cursor.fetchone()
            return dict(row) if row else {"total_tokens": 0, "avg_latency": 0}

    # --- CHAT FORUM REPOSITORY ---
    def save_chat_message(self, course_id: str, user_email: str, user_name: str, question: str, answer: str):
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO chat_messages (course_id, user_id, user_name, question, answer)
                   VALUES (?, ?, ?, ?, ?)""",
                (course_id, user_email, user_name, question, answer)
            )
            conn.commit()

    def get_chat_history(self, course_id: str, admin_view: bool = False) -> List[Dict]:
        """
        Retrieves shared history. 
        If admin_view=False, anonymizes the user identity.
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM chat_messages WHERE course_id = ? ORDER BY timestamp ASC LIMIT 100", 
                (course_id,)
            )
            rows = [dict(r) for r in cursor.fetchall()]
            
            # Anonymize for public view
            if not admin_view:
                for r in rows:
                    # Logic: Only Admin/Teacher sees real name. 
                    # Students see "Anonymous Student" (or their own? For now keep it simple forum privacy)
                    r['user_name'] = "Anonymous Student" 
                    r['user_id'] = "***" 
            
            return rows

    def search_similar_questions(self, course_id: str, query_keywords: List[str]) -> Optional[Dict]:
        """Simple keyword search for Guests (without vector DB for now to keep it lightweight)."""
        # In a real heavy system we'd use FTS5 or the VectorDB. 
        # For 'Smart Simple', we do a LIKE query on the last 500 messages.
        with self.get_connection() as conn:
            # Construct a query that looks for ANY keyword match
            # This is a basic 'Semantic Proxy' using SQL
            where_clauses = []
            params = [course_id]
            for kw in query_keywords:
                if len(kw) > 3:
                     where_clauses.append("question LIKE ?")
                     params.append(f"%{kw}%")
            
            if not where_clauses:
                return None
                
            sql = f"SELECT * FROM chat_messages WHERE course_id = ? AND ({' OR '.join(where_clauses)}) LIMIT 1"
            cursor = conn.execute(sql, params)
            row = cursor.fetchone()
            return dict(row) if row else None
