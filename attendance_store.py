import sqlite3
import datetime

DB_PATH = "attendance.db"


def init_db():
    """Crée la table des pointages si elle n'existe pas déjà."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def already_marked_today(name, status):
    """Vérifie si la personne a déjà un pointage de ce type aujourd'hui."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    today = datetime.date.today().isoformat()
    cur.execute("""
        SELECT COUNT(*) FROM attendance
        WHERE name = ? AND status = ? AND date(timestamp) = ?
    """, (name, status, today))
    count = cur.fetchone()[0]
    conn.close()
    return count > 0


def mark_attendance(name, status):
    """Enregistre un pointage et retourne l'horodatage utilisé."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    timestamp = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
    cur.execute(
        "INSERT INTO attendance (name, timestamp, status) VALUES (?, ?, ?)",
        (name, timestamp, status),
    )
    conn.commit()
    conn.close()
    return timestamp


def get_today_records():
    """Retourne la liste (name, timestamp, status) des pointages du jour,
    les plus récents en premier."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    today = datetime.date.today().isoformat()
    cur.execute("""
        SELECT name, timestamp, status FROM attendance
        WHERE date(timestamp) = ?
        ORDER BY timestamp DESC
    """, (today,))
    rows = cur.fetchall()
    conn.close()
    return rows
