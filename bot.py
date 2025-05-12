from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request
import os
import asyncio

TOKEN = os.environ.get("7928120010:AAE3wYneqTjgOALeGkKmQ5_keinrxPZyY-w")
APP_URL = os.environ.get("https://haocake.onrender.com")  # VD: https://your-app-name.onrender.com
CAKE_DIR = "cakes"

# Các chủ đề bánh
CAKE_TOPICS = {
    "🎂 Sinh nhật": "birthday",
    "💍 Kỷ niệm cưới": "anniversary",
    "💘 Valentine / Tình yêu": "love",
    "👨‍👩‍👧 Ngày của mẹ / cha": "parents",
    "🎓 Tốt nghiệp": "graduation",
    "🏢 Khai trương / Công ty": "opening",
    "🎄 Giáng sinh / Tết / Trung thu": "holiday",
}

# Flask app để nhận webhook từ Telegram
flask_app = Flask(__name__)

# Telegram bot application
application = ApplicationBuilder().token(TOKEN).build()

# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(text, callback_data=text)] for text in CAKE_TOPICS]
    markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("🎂 Chọn chủ đề bánh kem:", reply_markup=markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("🎂 Chọn chủ đề bánh kem:", reply_markup=markup)

# Nút nhấn chọn ảnh
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

# Đăng ký handler
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

# Flask webhook endpoint
@flask_app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "OK"

# Đặt webhook khi Flask khởi động
@flask_app.before_first_request
def set_webhook():
    webhook_url = f"{APP_URL}/webhook"
    asyncio.run(application.bot.set_webhook(webhook_url))

# Gunicorn sẽ gọi flask_app
app = flask_app
