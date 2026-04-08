import sqlite3
import os
from datetime import datetime

#All data is stored in this single file
DB_PATH = 'fitness_ai.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            age         INTEGER,
            weight_kg   REAL,
            height_cm   REAL,
            goal        TEXT,
            activity    TEXT,
            created_at  TEXT

        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id          TEXT PRIMARY KEY,
            user_id     TEXT NOT NULL,
            content     TEXT NOT NULL,
            category    TEXT,
            created_at  TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()
def save_user(user_id: str, name: str, age: int, weight_kg: float,
               height_cm: float, goal: str, activity: str):
    """Insert or update a user profile."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (id, name, age, weight_kg, height_cm, goal, activity, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            age=excluded.age,
            weight_kg=excluded.weight_kg,
            height_cm=excluded.height_cm,
            goal=excluded.goal,
            activity=excluded.activity
    ''', (user_id, name, age, weight_kg, height_cm, goal, activity,
          datetime.now().isoformat()))
    conn.commit()
    conn.close()
def get_user(user_id: str) -> dict | None:
    """Retrieve a user profile by ID. Returns None if not found."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_note(note_id: str, user_id: str, content: str, category: str = 'general'):
    """Save a new note for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO notes (id, user_id, content, category, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (note_id, user_id, content, category, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_recent_notes(user_id: str, limit: int = 20) -> list[dict]:
    """Retrieve the most recent notes for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM notes
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_note(note_id: str, user_id: str):
    """Delete a note by ID (only if it belongs to the user)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'DELETE FROM notes WHERE id = ? AND user_id = ?',
        (note_id, user_id)
    )
    conn.commit()
    conn.close()
