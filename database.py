"""
SF CHAI - SQLite Database Module
Handles session persistence for the application.
"""

import sqlite3
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional


# Database file location
DB_PATH = Path(__file__).parent / "sessions.db"
SESSIONS_DIR = Path(__file__).parent / "sessions"


def init_database() -> None:
    """
    Initialize the SQLite database and create sessions table if it doesn't exist.
    """
    # Ensure sessions directory exists
    SESSIONS_DIR.mkdir(exist_ok=True)
    
    # Create database connection
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            csv_filename TEXT,
            png_filename TEXT,
            chart_json TEXT,
            summary_text TEXT,
            chat_history TEXT,
            data_json TEXT
        )
    """)
    
    conn.commit()
    conn.close()


def get_session_dir(session_id: str) -> Path:
    """Get the session directory, create if doesn't exist."""
    session_dir = SESSIONS_DIR / session_id
    session_dir.mkdir(exist_ok=True)
    return session_dir


def save_session(
    session_id: str,
    name: str,
    csv_file=None,
    png_file=None,
    csv_data=None,
    chart_json: Optional[dict] = None,
    summary_text: Optional[str] = None,
    chat_history: Optional[list] = None,
    data_json: Optional[dict] = None
) -> None:
    """
    Save or update a session in the database with files.
    
    Args:
        session_id: Unique session identifier
        name: Session name
        csv_file: Streamlit uploaded file for CSV
        png_file: Streamlit uploaded file for PNG
        csv_data: pandas DataFrame (for data_json)
        chart_json: ECharts chart configuration as dict
        summary_text: Executive summary text
        chat_history: List of chat messages
        data_json: Additional session data as dict
    """
    session_dir = get_session_dir(session_id)
    
    csv_filename = None
    png_filename = None
    
    # Save CSV file
    if csv_file is not None:
        csv_filename = csv_file.name
        csv_path = session_dir / csv_filename
        with open(csv_path, "wb") as f:
            f.write(csv_file.getbuffer())
    
    # Save PNG file
    if png_file is not None:
        png_filename = png_file.name
        png_path = session_dir / png_filename
        with open(png_path, "wb") as f:
            f.write(png_file.getbuffer())
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    # Convert dicts to JSON strings
    chart_json_str = json.dumps(chart_json) if chart_json else None
    chat_history_str = json.dumps(chat_history) if chat_history else None
    
    # Prepare data_json
    session_data = data_json or {}
    if csv_data is not None:
        session_data["csv_columns"] = list(csv_data.columns)
        session_data["csv_rows"] = len(csv_data)
    
    data_json_str = json.dumps(session_data)
    
    # Use INSERT OR REPLACE to update if exists
    cursor.execute("""
        INSERT OR REPLACE INTO sessions 
        (id, name, created_at, updated_at, csv_filename, png_filename, 
         chart_json, summary_text, chat_history, data_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id, 
        name, 
        now,  # created_at (will be overwritten if exists)
        now,  # updated_at
        csv_filename,
        png_filename,
        chart_json_str,
        summary_text,
        chat_history_str,
        data_json_str
    ))
    
    conn.commit()
    conn.close()


def load_session(session_id: str) -> Optional[dict]:
    """
    Load a session from the database.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Session data as dict or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        return None
    
    # Convert row to dict and parse JSON fields
    session = dict(row)
    
    # Parse JSON fields
    if session.get('chart_json'):
        session['chart_json'] = json.loads(session['chart_json'])
    if session.get('chat_history'):
        session['chat_history'] = json.loads(session['chat_history'])
    if session.get('data_json'):
        session['data_json'] = json.loads(session['data_json'])
    
    # Add file paths
    session_dir = SESSIONS_DIR / session_id
    if session.get('csv_filename'):
        session['csv_path'] = session_dir / session['csv_filename']
    if session.get('png_filename'):
        session['png_path'] = session_dir / session['png_filename']
    
    return session


def list_sessions() -> list[dict]:
    """
    List all saved sessions.
    
    Returns:
        List of session metadata (id, name, created_at, updated_at)
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, created_at, updated_at, csv_filename, png_filename 
        FROM sessions 
        ORDER BY updated_at DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def delete_session(session_id: str) -> bool:
    """
    Delete a session from the database.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        True if deleted, False if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    # Also delete the session folder if it exists
    session_dir = SESSIONS_DIR / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir)
    
    return deleted


# Initialize database on module import
init_database()
