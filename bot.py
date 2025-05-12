import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request
import asyncio
import threading

# Lấy token và URL từ biến môi trường
TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("APP_URL")  # VD: https://your-app-name.onrender.com
CAKE_DIR = "cakes"

# Chủ đề bánh
CAKE_TOPICS = {
    "🎂 Sinh nhật": "birthday",
    "💍 Kỷ niệm cưới": "anniversary",
    "💘 Valentine / Tình yêu": "love",
    "👨‍👩‍👧 Ngày của mẹ / cha": "parents",
    "🎓 Tốt nghiệp": "graduation",
    "🏢 Khai trương / Công ty": "opening",
    "🎄 Giáng sinh / Tết / Trung thu": "holiday",
}

flask_app = Flask(__name__)
application = ApplicationBuilder().token(TOKEN).build()

# Route cho trang chủ
@flask_app.route('/')
def home():
    return "Bot đang chạy!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(text, callback_data=text)] for text in CAKE_TOPICS]
    markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("🎂 Chọn chủ đề bánh kem:", reply_markup=markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("🎂 Chọn chủ đề bánh kem:", reply_markup=markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = query.data
    if topic == "🔙 Quay lại menu":
        await start(update, context)
        return

    folder = CAKE_TOPICS.get(topic)
    folder_path = os.path.join(CAKE_DIR, folder)
    if not os.path.exists(folder_path):
        await query.message.reply_text("Không tìm thấy ảnh chủ đề này.")
        return

    files = [f for f in os.listdir(folder_path) if f.endswith((".jpg", ".jpeg", ".png"))]
    media = [InputMediaPhoto(open(os.path.join(folder_path, f), "rb")) for f in files[:10]]
    if media:
        await query.message.reply_media_group(media)
    else:
        await query.message.reply_text("Chưa có ảnh nào.")

    back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Quay lại menu", callback_data="🔙 Quay lại menu")]])
    await query.message.reply_text("Bạn có muốn chọn chủ đề khác?", reply_markup=back_btn)

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "OK"

# Đặt webhook khi Flask app khởi động
async def set_webhook():
    webhook_url = f"{APP_URL}/webhook"
    await application.bot.set_webhook(webhook_url)
    print(f"✅ Đã đặt webhook: {webhook_url}")

# Dùng thread để chạy set_webhook mà không chặn main thread của Flask
threading.Thread(target=lambda: asyncio.run(set_webhook())).start()

# Flask app sẽ được Gunicorn gọi
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
