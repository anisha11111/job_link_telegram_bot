"""
db/database.py — Skill + Company filtering
"""

import aiosqlite
from config import DB_NAME, COMPANY_ALIASES

# ─────────────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────────────
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id  INTEGER PRIMARY KEY,
            username TEXT,
            skill    TEXT,
            company  TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id         TEXT PRIMARY KEY,
            title      TEXT,
            company    TEXT,
            location   TEXT,
            category   TEXT,
            apply_link TEXT,
            source     TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS notified (
            chat_id INTEGER,
            job_id  TEXT,
            PRIMARY KEY(chat_id, job_id)
        )""")
        await db.commit()


# ─────────────────────────────────────────────────────
# USERS
# ─────────────────────────────────────────────────────
async def save_user(chat_id, username, skill, company):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users(chat_id, username, skill, company) VALUES(?,?,?,?)",
            (chat_id, username, skill, company)
        )
        await db.commit()


async def get_user(chat_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT chat_id, username, skill, company FROM users WHERE chat_id=?",
            (chat_id,)
        )
        row = await cursor.fetchone()
        if not row:
            return None
        return {"chat_id": row[0], "username": row[1], "skill": row[2], "company": row[3]}


async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT chat_id, skill, company FROM users")
        rows = await cursor.fetchall()
        return [{"chat_id": r[0], "skill": r[1], "company": r[2]} for r in rows]


# ─────────────────────────────────────────────────────
# JOBS
# ─────────────────────────────────────────────────────
async def save_job(job):
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            await db.execute(
                "INSERT INTO jobs(id,title,company,location,category,apply_link,source) VALUES(?,?,?,?,?,?,?)",
                (job["id"], job["title"], job["company"], job["location"],
                 job["category"], job["apply_link"], job["source"])
            )
            await db.commit()
            return True
        except:
            return False


# ─────────────────────────────────────────────────────────────────────────────
# SKILL KEYWORDS
# Problem: jobs stored as "Software Engineer" or "Software Developer" in title
# but user searches "Full Stack" or "Backend" — no match.
# Fix: each skill now includes ALL common job title variations that belong to it.
# ─────────────────────────────────────────────────────────────────────────────
SKILL_KEYWORDS = {
    "Python": [
        "python",
        "software engineer", "software developer", "sde ", "swe ",
        "backend engineer", "backend developer",
    ],
    "Java": [
        "java", "spring", "spring boot", "kotlin",
        "software engineer", "software developer", "sde ", "swe ",
        "backend engineer", "backend developer",
    ],
    "JavaScript": [
        "javascript", "typescript",
        "software engineer", "software developer",
        "frontend engineer", "frontend developer", "web developer",
    ],
    "React": [
        "react", "next.js", "nextjs", "react native",
        "frontend engineer", "frontend developer",
        "ui engineer", "software engineer",
    ],
    "Node.js": [
        "node.js", "nodejs", "node", "express",
        "backend engineer", "backend developer",
        "software engineer", "software developer",
    ],
    "Data Science": [
        "data scientist", "data science", "data analyst",
        "analytics engineer", "business analyst",
        "data engineer", "research scientist",
    ],
    "ML/AI": [
        "machine learning", "deep learning", "nlp", "llm",
        "ai engineer", "ml engineer", "research engineer",
        "applied scientist", "research scientist", "artificial intelligence",
    ],
    "DevOps": [
        "devops", "site reliability", "sre",
        "platform engineer", "infrastructure engineer",
        "cloud engineer", "kubernetes", "docker",
        "software engineer", "systems engineer",
    ],
    "Testing/QA": [
        "qa engineer", "quality assurance", "test engineer",
        "sdet", "automation engineer", "qa analyst",
        "software engineer in test",
    ],
    "Android": [
        "android", "android developer", "android engineer",
        "mobile developer", "mobile engineer",
        "software engineer", "software developer",
    ],
    "iOS": [
        "ios", "ios developer", "ios engineer",
        "swift developer", "swift engineer",
        "mobile developer", "mobile engineer",
        "software engineer", "software developer",
    ],
    "Full Stack": [
        "full stack", "fullstack", "full-stack",
        "software engineer", "software developer",
        "sde", "swe", "web developer", "web engineer",
        "developer", "engineer",                        # ← catches "Software Developer", "Software Engineer"
    ],
    "Frontend": [
        "frontend", "front-end", "front end",
        "ui engineer", "ui developer",
        "web developer", "web engineer",
        "software engineer", "software developer",
    ],
    "Backend": [
        "backend", "back-end", "back end",
        "server engineer", "api engineer",
        "software engineer", "software developer",
        "sde", "swe", "systems engineer",
        "developer", "engineer",
    ],
    "Any": [],
}


def _skill_filter(skill: str):
    """Build SQL WHERE clause for skill — searches both title and category."""
    if skill == "Any":
        return "1=1", []

    keywords = SKILL_KEYWORDS.get(skill, [skill.lower()])
    if not keywords:
        return "1=1", []

    parts, params = [], []
    for kw in keywords:
        parts.append("LOWER(title) LIKE ?")
        params.append(f"%{kw}%")
        parts.append("LOWER(category) LIKE ?")
        params.append(f"%{kw}%")

    return "(" + " OR ".join(parts) + ")", params


def _company_filter(company: str):
    """Build SQL WHERE clause for company name matching."""
    if company == "Any":
        return "1=1", []
    aliases = COMPANY_ALIASES.get(company, [company.lower()])
    parts  = ["LOWER(company) LIKE ?"] * len(aliases)
    params = [f"%{a}%" for a in aliases]
    return "(" + " OR ".join(parts) + ")", params


# ─────────────────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────────────────
async def search_jobs(skill: str, company: str, limit: int = 8):
    async with aiosqlite.connect(DB_NAME) as db:

        skill_sql,   skill_params   = _skill_filter(skill)
        company_sql, company_params = _company_filter(company)

        # Primary: skill + company
        query = f"""
            SELECT title, company, location, category, apply_link, source
            FROM jobs
            WHERE {skill_sql} AND {company_sql}
            ORDER BY rowid DESC
            LIMIT ?
        """
        cursor = await db.execute(query, skill_params + company_params + [limit])
        rows   = await cursor.fetchall()

        # Fallback: if specific company has no match, search skill across all companies
        if not rows and company != "Any":
            print(f"[search] No '{skill}' at {company} — showing all companies")
            cursor = await db.execute(
                f"SELECT title, company, location, category, apply_link, source FROM jobs WHERE {skill_sql} ORDER BY rowid DESC LIMIT ?",
                skill_params + [limit]
            )
            rows = await cursor.fetchall()

        return [
            {"title": r[0], "company": r[1], "location": r[2],
             "category": r[3], "apply_link": r[4], "source": r[5]}
            for r in rows
        ]


# ─────────────────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────────────────
async def get_unnotified_jobs(chat_id: int, skill: str, company: str):
    async with aiosqlite.connect(DB_NAME) as db:
        skill_sql,   skill_params   = _skill_filter(skill)
        company_sql, company_params = _company_filter(company)

        query = f"""
            SELECT id, title, company, location, apply_link
            FROM jobs
            WHERE id NOT IN (SELECT job_id FROM notified WHERE chat_id=?)
              AND {skill_sql} AND {company_sql}
            ORDER BY rowid DESC
            LIMIT 5
        """
        cursor = await db.execute(query, [chat_id] + skill_params + company_params)
        rows   = await cursor.fetchall()
        return [{"id": r[0], "title": r[1], "company": r[2],
                 "location": r[3], "apply_link": r[4]} for r in rows]


async def mark_notified(chat_id: int, job_id: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO notified(chat_id, job_id) VALUES(?,?)",
            (chat_id, job_id)
        )
        await db.commit()


# ─────────────────────────────────────────────────────
# STATS
# ─────────────────────────────────────────────────────
async def get_stats():
    async with aiosqlite.connect(DB_NAME) as db:
        job_count  = await db.execute_fetchone("SELECT COUNT(*) FROM jobs")
        user_count = await db.execute_fetchone("SELECT COUNT(*) FROM users")
        return job_count[0], user_count[0]