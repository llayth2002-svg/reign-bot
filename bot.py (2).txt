import os
import telebot
import requests
import time

BOT_TOKEN = os.environ.get("BOT_TOKEN", "7974047848:AAGKJ4JHTEkz-9Q0T28z1yJSo5v4X6dJbOs")
SE_USER = "783342603"
SE_SECRET = "v8QfZt3yPqLmKjNhX2bD9cR4aW1eU0oI"

bot = telebot.TeleBot(BOT_TOKEN)

BAD_WORDS = ["حبوب", "كبتاجون", "ترامادول", "ليريكا", "كلاشنكوف", "مسدس", "سلاح", "مخدرات", "حشيش"]

def contains_bad_word(text):
    if not text: return None
    txt = text.lower()
    for w in BAD_WORDS:
        if w in txt:
            return w
    return None

def check_image_ai(img_bytes: bytes) -> bool:
    try:
        r = requests.post(
            "https://api.sightengine.com/1.0/check.json",
            data={
                'models': 'nudity,weapon,gore,drugs,offensive,violence',
                'api_user': SE_USER,
                'api_secret': SE_SECRET
            },
            files={'media': img_bytes},
            timeout=20
        )
        j = r.json()
        if j.get('gore',{}).get('prob',0) > 0.3: return True
        if j.get('weapon',0) > 0.3: return True
        if j.get('drugs',0) > 0.3: return True
        if j.get('violence',0) > 0.3: return True
        if j.get('nudity',{}).get('raw',0) > 0.4: return True
        if j.get('offensive',{}).get('prob',0) > 0.6: return True
        return False
    except Exception as e:
        print(f"SightEngine error: {e}")
        return False

@bot.message_handler(content_types=['text'])
def on_text(m):
    bad = contains_bad_word(m.text)
    if bad:
        try:
            bot.delete_message(m.chat.id, m.message_id)
        except: pass

@bot.message_handler(content_types=['photo'])
def on_photo(m):
    try:
        file_info = bot.get_file(m.photo[-1].file_id)
        data = bot.download_file(file_info.file_path)
        if check_image_ai(data):
            bot.delete_message(m.chat.id, m.message_id)
            bot.send_message(m.chat.id, "🚫 تم حذف صورة مخالفة - REIGN Security")
    except Exception as e:
        print(e)

print("✅ Reign Guard Bot Started - 24/7 Mode")
while True:
    try:
        bot.infinity_polling(timeout=90, long_polling_timeout=90)
    except Exception as e:
        print(f"Restarting: {e}")
        time.sleep(5)
