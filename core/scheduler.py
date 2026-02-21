"""
core/scheduler.py — Runs collector + matcher on a timer
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.collector import collect_all_jobs
from core.matcher import notify_users
from config import FETCH_INTERVAL_MINUTES


def start_scheduler(bot):
    scheduler = AsyncIOScheduler()

    async def tick():
        print("[Scheduler] Tick: collecting jobs...")
        await collect_all_jobs()
        await notify_users(bot)

    scheduler.add_job(
        tick,
        trigger="interval",
        minutes=FETCH_INTERVAL_MINUTES,
        id="main_tick",
        replace_existing=True
    )
    scheduler.start()
    print(f"[Scheduler] Running every {FETCH_INTERVAL_MINUTES} minutes.")
    return scheduler