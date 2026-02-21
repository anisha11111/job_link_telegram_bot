"""
bot/keyboards.py — Skill + Company selection keyboards
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import SKILLS, COMPANIES


def skill_keyboard() -> InlineKeyboardMarkup:
    rows = []
    row = []
    for i, skill in enumerate(SKILLS):
        row.append(InlineKeyboardButton(skill, callback_data=f"skill|{skill}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)


def company_keyboard() -> InlineKeyboardMarkup:
    """Shows all companies as buttons, 2 per row."""
    rows = []
    row = []
    for i, company_name in enumerate(COMPANIES.keys()):
        row.append(InlineKeyboardButton(company_name, callback_data=f"company|{company_name}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)