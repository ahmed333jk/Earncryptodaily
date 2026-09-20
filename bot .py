import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is missing.")

# Simple in-memory data for the starter version.
# For production, replace this with SQLite/PostgreSQL.
users = {}
referrals = {}


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 Tasks", callback_data="tasks"),
         InlineKeyboardButton("👥 Referrals", callback_data="referrals")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance"),
         InlineKeyboardButton("🎁 Rewards", callback_data="rewards")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    users.setdefault(user_id, {"points": 0})

    # /start ref_123456789
    if context.args:
        arg = context.args[0]
        if arg.startswith("ref_"):
            try:
                referrer_id = int(arg.replace("ref_", "", 1))
                if referrer_id != user_id and user_id not in referrals:
                    referrals[user_id] = referrer_id
                    if referrer_id in users:
                        users[referrer_id]["points"] += 10
            except ValueError:
                pass

    await update.message.reply_text(
        f"Welcome to EarnCryptoDaily, {user.first_name}! 🚀\n\n"
        "Complete tasks, invite friends, collect points and check rewards.",
        reply_markup=main_menu(),
    )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    users.setdefault(user_id, {"points": 0})

    if query.data == "tasks":
        text = (
            "🎯 TASKS\n\n"
            "1. Join the official community\n"
            "2. Follow the project's social page\n"
            "3. Share the campaign\n\n"
            "Task verification and rewards can be added next."
        )
    elif query.data == "referrals":
        bot = await context.bot.get_me()
        link = f"https://t.me/{bot.username}?start=ref_{user_id}"
        count = sum(1 for ref in referrals.values() if ref == user_id)
        text = (
            "👥 REFERRALS\n\n"
            f"Your referrals: {count}\n"
            "Reward: 10 points per referred user.\n\n"
            f"Your referral link:\n{link}"
        )
    elif query.data == "balance":
        text = f"💰 Your balance: {users[user_id]['points']} points"
    else:
        text = (
            "🎁 REWARDS\n\n"
            "Rewards can be configured here.\n"
            "For crypto payouts, add secure wallet and payout verification "
            "logic before enabling real withdrawals."
        )

    await query.edit_message_text(text, reply_markup=main_menu())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Open the bot\n"
        "/help - Show help\n\n"
        "Use the buttons to view tasks, referrals, balance and rewards."
    )


def run():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(menu_callback))
    print("EarnCryptoDaily bot is running...")
    app.run_polling()


if __name__ == "__main__":
    run()
