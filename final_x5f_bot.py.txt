"""
REIGN Guard Bot - جاهز للرفع - التوكن مضاف
"""
import os
import logging
import requests
from io import BytesIO
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

BOT_TOKEN = "7974047848:AAGKJ4JHTEkz-9Q0T28z1yJSo5v4X6dJbOs"
SIGHTENGINE_USER = ""  # بعدين ضيفه من sightengine.com
SIGHTENGINE_SECRET = ""

BANNED_WORDS = ["حبوب","مخدرات","حشيش","كبتاجون","ترامادول","كرستال","هيروين","كلاشنكوف","مسدس","قاذفه","تفجير","ارهاب","داعش","بيع سلاح","بيع حبوب"]

def check_image_sightengine(image_bytes):
    if not SIGHTENGINE_USER or not SIGHTENGINE_SECRET:
        return False, "no_api"
    try:
        url = "https://api.sightengine.com/1.0/check.json"
        params = {'models': 'weapon,drugs,gore,offensive,violence', 'api_user': SIGHTENGINE_USER, 'api_secret': SIGHTENGINE_SECRET}
        files = {'media': image_bytes}
        r = requests.post(url, files=files, data=params, timeout=15)
        data = r.json()
        reasons = []
        if data.get('weapon',0) > 0.5: reasons.append("سلاح")
        if data.get('drugs',0) > 0.5: reasons.append("مخدرات")
        if data.get('gore',{}).get('prob',0) > 0.6: reasons.append("دم/عنف")
        if data.get('violence',0) > 0.7: reasons.append("عنف")
        if reasons: return True, ", ".join(reasons)
        return False, "clean"
    except Exception as e:
        return False, str(e)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ REIGN Guard شغال 24/7\nارفعني ادمن بصلاحية حذف الرسائل\n/start - تشغيل\n/status - حالة")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"AI Vision: {'✅' if SIGHTENGINE_USER else '⚠️ يحتاج تفعيل sightengine.com'}\nكلمات محظورة: {len(BANNED_WORDS)}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    try:
        m = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        if m.status in ['administrator','creator']: return
    except: pass
    text = update.message.text.lower()
    for w in BANNED_WORDS:
        if w in text:
            try:
                await update.message.delete()
                await context.bot.send_message(update.effective_chat.id, f"⚠️ حذف رسالة من {update.effective_user.mention_html()} - كلمة محظورة: {w}", parse_mode='HTML')
                return
            except: pass

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    try:
        m = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        if m.status in ['administrator','creator']: return
    except: pass
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_bytes = BytesIO()
        await file.download_to_memory(image_bytes)
        image_bytes.seek(0)
        is_banned, reason = check_image_sightengine(image_bytes)
        if is_banned:
            await update.message.delete()
            await context.bot.send_message(update.effective_chat.id, f"🚫 حذف صورة ممنوعة من {update.effective_user.mention_html()}\nالسبب: {reason}", parse_mode='HTML')
    except Exception as e:
        logging.error(e)

app = Flask(__name__)
@app.route('/')
def home(): return "REIGN Guard Bot Running 24/7"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def main():
    logging.basicConfig(level=logging.INFO)
    Thread(target=run_flask, daemon=True).start()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(CommandHandler("status", status_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.IMAGE, handle_photo))
    print("Bot started - REIGN Guard 24/7")
    application.run_polling()

if __name__ == '__main__':
    main()
