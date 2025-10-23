import asyncio
import random
import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "8496126499:AAG9tbOqLRlO8fYejC3rfcSY24SZ4-MYknA"

VIDEOS = [
    "https://www.youtube.com/watch?v=Z1W-ZeszTMw",
    "https://www.youtube.com/watch?v=JwEbnUPP0ik&t=220s",
    "https://www.youtube.com/watch?v=FUJeG5BQoHA"
]

group_ids = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ["group", "supergroup"]:
        group_ids.add(chat.id)
        print(f"Guruh qo‘shildi: {chat.title} (ID: {chat.id})")
    await update.message.reply_text(
        "Salom! Bot ishga tushdi. Siz qo‘shgan guruhlarga avtomatik video yuboriladi."
    )

async def send_video_task(app):
    while True:
        if group_ids:
            video = random.choice(VIDEOS)
            for gid in group_ids:
                try:
                    await app.bot.send_message(chat_id=gid, text=f"📹 Video: {video}")
                    print(f"Video yuborildi: {gid} → {video}")
                except Exception as e:
                    print(f"Xatolik {gid} ga yuborishda: {e}")
        else:
            print("Hozircha guruh yo'q.")
        await asyncio.sleep(50)

async def main_async():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    asyncio.create_task(send_video_task(app))
    await app.initialize()
    await app.start()
    print("🤖 Bot ishga tushdi! /start buyrug‘ini yuboring.")
    await app.updater.start_polling()
    await asyncio.Event().wait()

# === Flask server (Render uchun) ===
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))  # Render avtomatik port beradi
    flask_app.run(host="0.0.0.0", port=port)

# Flask serverni alohida threadda ishga tushirish
Thread(target=run_flask, daemon=True).start()

if __name__ == "__main__":
    # asyncio loopni to‘g‘ri ishga tushirish
    try:
        asyncio.run(main_async())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to‘xtatildi.")
