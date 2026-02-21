"""
bot/handlers.py — Skill + Company flow (location removed)
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from db.database import save_user, get_user, search_jobs, get_stats
from bot.keyboards import skill_keyboard, company_keyboard

PICK_SKILL, PICK_COMPANY = range(2)

SOURCE_BADGE = {
    "Greenhouse": "🌿",
    "Lever":      "🎯",
    "Remotive":   "🌐",
    "The Muse":   "💡",
}


# ─────────────────────────────────────────────────────
# HELPER — fetch and send jobs to user
# ─────────────────────────────────────────────────────
async def send_jobs(chat_id: int, skill: str, company: str, ctx: ContextTypes.DEFAULT_TYPE):
    jobs = await search_jobs(skill=skill, company=company, limit=8)

    if not jobs:
        await ctx.bot.send_message(
            chat_id=chat_id,
            text=(
                "😕 No matching jobs found right now.\n\n"
                "I'll automatically alert you the moment new ones are posted!\n"
                "Try /update to change your skill or company."
            )
        )
        return

    company_label = f" at *{company}*" if company != "Any" else ""
    await ctx.bot.send_message(
        chat_id=chat_id,
        text=f"✅ Found *{len(jobs)}* *{skill}* jobs{company_label}:",
        parse_mode="Markdown"
    )

    for job in jobs:
        badge = SOURCE_BADGE.get(job["source"], "📋")
        msg = (
            f"{badge} *{job['company']}*\n"
            f"💼 {job['title']}\n"
            f"📍 {job['location']}\n"
            f"🏷️ {job['category']}  •  _{job['source']}_\n\n"
            f"[👉 Apply Here]({job['apply_link']})"
        )
        try:
            await ctx.bot.send_message(
                chat_id=chat_id,
                text=msg,
                parse_mode="Markdown",
                disable_web_page_preview=False
            )
        except Exception as e:
            print(f"[send_jobs] Error: {e}")


# ─────────────────────────────────────────────────────
# /start
# ─────────────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update.effective_chat.id)
    if user:
        await update.message.reply_text(
            f"👋 Welcome back!\n\n"
            f"💼 Skill: *{user['skill']}*\n"
            f"🏢 Company: *{user['company']}*\n\n"
            f"Use /search to find jobs or /update to change preferences.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "👋 Welcome to *Job Aggregator Bot!*\n\n"
        "I fetch jobs from Greenhouse, Lever, Remotive & The Muse "
        "and alert you instantly when new ones match.\n\n"
        "📌 *Step 1:* Choose your skill:",
        parse_mode="Markdown",
        reply_markup=skill_keyboard()
    )
    return PICK_SKILL


# ─────────────────────────────────────────────────────
# /update
# ─────────────────────────────────────────────────────
async def update_prefs(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔄 Update your preferences.\n\n📌 Choose your skill:",
        reply_markup=skill_keyboard()
    )
    return PICK_SKILL


# ─────────────────────────────────────────────────────
# Callback: skill button
# ─────────────────────────────────────────────────────
async def on_skill_chosen(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    skill = query.data.split("|")[1]
    ctx.user_data["skill"] = skill

    await query.edit_message_text(
        f"✅ Skill: *{skill}*\n\n🏢 *Step 2:* Choose a company to track:",
        parse_mode="Markdown",
        reply_markup=company_keyboard()
    )
    return PICK_COMPANY


# ─────────────────────────────────────────────────────
# Callback: company button → save + show jobs
# ─────────────────────────────────────────────────────
async def on_company_chosen(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query   = update.callback_query
    await query.answer()

    company  = query.data.split("|")[1]
    skill    = ctx.user_data.get("skill", "Any")
    chat_id  = query.from_user.id
    username = query.from_user.username or "user"

    await save_user(chat_id, username, skill, company)

    company_label = f"*{company}*" if company != "Any" else "all companies"
    await query.edit_message_text(
        f"✅ *Profile saved!*\n\n"
        f"💼 Skill: *{skill}*\n"
        f"🏢 Company: *{company}*\n\n"
        f"🔍 Fetching matching jobs from {company_label}...",
        parse_mode="Markdown"
    )

    await send_jobs(chat_id, skill, company, ctx)
    return ConversationHandler.END


# ─────────────────────────────────────────────────────
# /search
# ─────────────────────────────────────────────────────
async def search(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update.effective_chat.id)
    if not user:
        await update.message.reply_text("Use /start first to set your preferences.")
        return

    await update.message.reply_text(
        f"🔍 Searching *{user['skill']}* jobs at *{user['company']}*...",
        parse_mode="Markdown"
    )
    await send_jobs(update.effective_chat.id, user["skill"], user["company"], ctx)


# ─────────────────────────────────────────────────────
# /profile
# ─────────────────────────────────────────────────────
async def profile(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update.effective_chat.id)
    if not user:
        await update.message.reply_text("No profile found. Use /start to register.")
        return
    await update.message.reply_text(
        f"👤 *Your Profile*\n\n"
        f"💼 Skill: *{user['skill']}*\n"
        f"🏢 Company: *{user['company']}*\n\n"
        f"/search — find jobs now\n"
        f"/update — change preferences",
        parse_mode="Markdown"
    )


# ─────────────────────────────────────────────────────
# /stats
# ─────────────────────────────────────────────────────
async def stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    job_count, user_count = await get_stats()
    await update.message.reply_text(
        f"📊 *Bot Stats*\n\n"
        f"📋 Jobs in DB: *{job_count}*\n"
        f"👥 Registered Users: *{user_count}*\n\n"
        f"_Refreshes every hour automatically._",
        parse_mode="Markdown"
    )


# ─────────────────────────────────────────────────────
# /help
# ─────────────────────────────────────────────────────
async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Commands*\n\n"
        "/start — Register & set preferences\n"
        "/search — Find matching jobs now\n"
        "/profile — View your profile\n"
        "/update — Change skill or company\n"
        "/stats — DB stats\n"
        "/help — This message",
        parse_mode="Markdown"
    )


# ─────────────────────────────────────────────────────
# /cancel
# ─────────────────────────────────────────────────────
async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END