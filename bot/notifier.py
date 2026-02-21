from telegram import Bot
from config import TELEGRAM_TOKEN
# from db.database import get_all_users
from db.database import get_all_users, get_unnotified_jobs, mark_notified

bot = Bot(token=TELEGRAM_TOKEN)

async def notify_users(title, company, location, link):
    users = await get_all_users()

    if not users:
        print("No subscribed users")
        return

    message = f"""
🚀 *New Job Alert*

💼 {title}
🏢 {company}
📍 {location}

🔗 Apply Here:
{link}
"""

    for user in users:
        try:
            await bot.send_message(
                chat_id=user,
                text=message,
                parse_mode="Markdown"
            )
        except Exception as e:
            print("Failed sending to", user, e)