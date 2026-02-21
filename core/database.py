import sqlite3
from datetime import datetime

DB_NAME = "jobs.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # USERS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER UNIQUE,
        skill TEXT,
        location TEXT
    )
    """)

    # JOBS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        company TEXT,
        location TEXT,
        link TEXT UNIQUE,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database ready")


# ---------- USER ----------
def save_user(chat_id, skill, location):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO users(chat_id, skill, location)
    VALUES(?,?,?)
    """, (chat_id, skill, location))

    conn.commit()
    conn.close()


def get_all_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT chat_id, skill, location FROM users")
    users = cur.fetchall()
    conn.close()
    return users


# ---------- JOB ----------
def add_job(title, company, location, link):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO jobs(title, company, location, link, created_at)
        VALUES(?,?,?,?,?)
        """, (title, company, location, link, datetime.now().isoformat()))
        conn.commit()
        print(f"Saved: {title}")
        return True
    except sqlite3.IntegrityError:
        # duplicate job
        return False
    finally:
        conn.close()


def get_recent_jobs(limit=20):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT title, company, location, link
    FROM jobs
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))
    jobs = cur.fetchall()
    conn.close()
    return jobs