import os
import telebot
import requests
import time

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8978262524:AAHxalzAL8ddAbZ_hpZMce0lkjtid1KZtyI")
SE_USER = "783342603"
SE_SECRET = "iLwAvFrBJuuZar9E7v9KwHvJaHc2LSCw"

bot = telebot.TeleBot(BOT_TOKEN)

BAD_WORDS = ["حبوب", "كبتاجون", "ترامادول", "ليريكا", "كلاشنكوف", "مسدس", "سلاح", "مخدرات", "حشيش", "بودرة", "كوكايين", "هيروين"]

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
        print(f"SightEngine response: {j}")
        if j.get('gore',{}).get('prob',0) > 0.3: return True
        if j.get('weapon',0) > 0.3: return True
        if j.get('drugs',0) > 0.3: return True
        if j.get('violence',0) > 0.3: return True
        if j.get('nudity',{}).get('raw',0) > 0.4: return True
        if j.get('offensive',{}).get('prob',0) > 0.6: return True
        # لو الصورة فيها مخدرات واضحة، حتى لو النسبة قليلة احذف
        if j.get('drugs',0) > 0.15: 
            print(f"Drugs detected low score: {j.get('drugs')}")
            return True
        return False
    except Exception as e:
        print(f"SightEngine error: {e}")
        # لو فشل الـ API لا تحذف الصور العادية - بس الممنوعات
        return False

@bot.message_handler(commands=['start','help'])
def on_start(m):
    # يرد بالخاص فقط، بالقروب يسكت حتى لا يسوي سبام
    if m.chat.type == 'private':
        bot.send_message(m.chat.id, 
            "👋 هلا بيك بـ REIGN Guard\n"
            "✅ البوت شغال 24/7\n"
            "🛡️ يحذف: مخدرات، سلاح، حبوب، صور مخالفة\n\n"
            "ضيفني بقروبك كأدمن وفعل صلاحية حذف الرسائل"
        )

@bot.message_handler(content_types=['text'])
def on_text(m):
    if m.text and m.text.startswith('/'):
        return
    bad = contains_bad_word(m.text)
    if bad:
        try:
            bot.delete_message(m.chat.id, m.message_id)
            print(f"Deleted text with bad word: {bad}")
        except Exception as e:
            print(f"Delete failed (not admin?): {e}")

@bot.message_handler(content_types=['photo', 'document'])
def on_photo(m):
    try:
        # افحص الكابشن اول
        caption = m.caption or ""
        if contains_bad_word(caption):
            try:
                bot.delete_message(m.chat.id, m.message_id)
                print(f"Deleted photo with bad caption")
                return
            except: pass

        # نزل الصورة وافحصها
        if m.content_type == 'photo':
            file_id = m.photo[-1].file_id
        else:
            file_id = m.document.file_id
            
        file_info = bot.get_file(file_id)
        data = bot.download_file(file_info.file_path)
        
        if check_image_ai(data):
            try:
                bot.delete_message(m.chat.id, m.message_id)
                bot.send_message(m.chat.id, "🚫 تم حذف صورة مخالفة - REIGN Security")
                print("Deleted violating image")
            except Exception as e:
                print(f"Failed to delete image (no admin permission?): {e}")
        else:
            print("Image clean")
    except Exception as e:
        print(f"on_photo error: {e}")

print("✅ Reign Guard Bot Started - 24/7 Mode")
while True:
    try:
        bot.infinity_polling(timeout=90, long_polling_timeout=90)
    except Exception as e:
        print(f"Restarting: {e}")
        time.sleep(5)
