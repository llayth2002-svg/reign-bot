import os, requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
SE_USER = os.getenv("SIGHTENGINE_USER")
SE_SECRET = os.getenv("SIGHTENGINE_SECRET")

BANNED_WORDS = ["مخدرات","حشيش","كريستال","سلاح","مسدس","كلاشنكوف","ارهاب","داعش","قتل"]

def check_image_ai(img_bytes: bytes) -> bool:
    if not SE_USER or not SE_SECRET:
        return False
    try:
        r = requests.post(
            "https://api.sightengine.com/1.0/check.json",
            data={"models": "weapon,drugs,gore,violence", "api_user": SE_USER, "api_secret": SE_SECRET},
            files={"media": img_bytes},
            timeout=20
        )
        d = r.json()
        weapon = d.get("weapon", 0)
        drugs = d.get("drugs", 0)
        gore = d.get("gore", {}).get("prob", 0)
        violence = d.get("violence", 0)
        if isinstance(violence, dict):
            violence = violence.get("prob", 0)
        print(f"check: w={weapon} d={drugs} g={gore} v={violence}")
        return weapon > 0.5 or drugs > 0.5 or gore > 0.5 or violence > 0.5
    except Exception as e:
        print(f"error {e}")
        return False

async def delete_bad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    text = (update.message.text or update.message.caption or "").lower()
    if "http" in text or "t.me/" in text or "www." in text:
        try:
            await update.message.delete()
        except:
            pass
        return
    for w in BANNED_WORDS:
        if w in text:
            try:
                await update.message.delete()
            except:
                pass
            return

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_bad(update, context)
    if not update.message or not update.message.photo:
        return
    try:
        file = await context.bot.get_file(update.message.photo[-1].file_id)
        img_bytes = bytes(await file.download_as_bytearray())
        if check_image_ai(img_bytes):
            await update.message.delete()
            await context.bot.send_message(update.effective_chat.id, "🚫 تم حذف صورة ممنوعة (سلاح/مخدرات/عنف/ارهاب)")
    except Exception as e:
        print(e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ بوت رين V2 شغال - يفحص الصور الممنوعة")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, delete_bad))
    print("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
