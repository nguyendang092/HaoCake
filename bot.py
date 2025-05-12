from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("APP_URL")  # VD: https://your-app-name.onrender.com

CAKE_TOPICS = {
    "🎂 Sinh nhật": "birthday",
    "💍 Kỷ niệm cưới": "anniversary",
    "💘 Valentine / Tình yêu": "love",
    "👨‍👩‍👧 Ngày của mẹ / cha": "parents",
    "🎓 Tốt nghiệp": "graduation",
    "🏢 Khai trương / Công ty": "opening",
    "🎄 Giáng sinh / Tết / Trung thu": "holiday",
}
CAKE_DIR = "cakes"

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

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).webhook_url(f"{APP_URL}/webhook").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_webhook(listen="0.0.0.0", port=int(os.environ.get("PORT", 8080)), webhook_url=f"{APP_URL}/webhook")
