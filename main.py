from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler
)
from config import TELEGRAM_TOKEN
from db.database import init_db
from core.collector import collect_all_jobs
from core.matcher import notify_users
from core.scheduler import start_scheduler
from bot.handlers import (
    start, update_prefs, search, profile,
    stats, help_cmd, cancel,
    on_skill_chosen, on_company_chosen,
    PICK_SKILL, PICK_COMPANY
)


async def post_init(application):
    await init_db()
    print("✅ Database ready")
    print("🤖 Bot started!")

    print("🔍 Running first job fetch...")
    await collect_all_jobs()

    await notify_users(application.bot)
    start_scheduler(application.bot)
    print("🚀 All systems running!")


def main():
    app = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("update", update_prefs),
        ],
        states={
            PICK_SKILL: [
                CallbackQueryHandler(on_skill_chosen, pattern="^skill\\|")
            ],
            PICK_COMPANY: [
                CallbackQueryHandler(on_company_chosen, pattern="^company\\|")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("search",  search))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("stats",   stats))
    app.add_handler(CommandHandler("help",    help_cmd))

    print("📡 Polling...")
    app.run_polling()


if __name__ == "__main__":
    main()