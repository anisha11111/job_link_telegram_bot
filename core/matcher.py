"""
core/matcher.py — Sends job alerts to users based on skill + company
"""

from telegram import Bot
from db.database import get_all_users, get_unnotified_jobs, mark_notified


async def notify_users(bot: Bot):
    """Check all users for new matching jobs and send alerts."""
    async with __import__('aiosqlite').connect(__import__('config').DB_NAME) as db:
        rows = await db.execute_fetchall(
            "SELECT chat_id, skill, company FROM users"
        )
    users = [{"chat_id": r[0], "skill": r[1], "company": r[2]} for r in rows]

    print(f"[Matcher] Checking {len(users)} users for new matches...")

    for user in users:
        chat_id = user["chat_id"]
        skill   = user["skill"]
        company = user["company"]

        new_jobs = await get_unnotified_jobs(chat_id, skill, company)

        for job in new_jobs:
            msg = (
                f"🔔 *New Job Alert!*\n\n"
                f"🏢 *{job['company']}*\n"
                f"💼 {job['title']}\n"
                f"📍 {job['location']}\n\n"
                f"[👉 Apply Here]({job['apply_link']})"
            )
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=msg,
                    parse_mode="Markdown",
                    disable_web_page_preview=False
                )
                await mark_notified(chat_id, job["id"])
            except Exception as e:
                print(f"[Matcher] Failed to notify {chat_id}: {e}")