def check_image_ai(img_bytes: bytes) -> bool:
    if not SE_USER or not SE_SECRET:
        return False
    try:
        r = requests.post(
            "https://api.sightengine.com/1.0/check.json",
            data={
                'models': 'nudity,wad,gore,offensive,weapon,drugs',
                'api_user': SE_USER,
                'api_secret': SE_SECRET
            },
            files={'media': img_bytes}
        )
        j = r.json()
        # gore = دم وعنف وقتل
        # weapon = سلاح وارهاب
        # drugs = مخدرات
        # wad = عنف
        if j.get('gore',{}).get('prob',0) > 0.3: return True
        if j.get('weapon',0) > 0.3: return True
        if j.get('drugs',0) > 0.3: return True
        if j.get('violence',0) > 0.3: return True
        if j.get('nudity',{}).get('raw',0) > 0.3: return True
        return False
    except:
        return False
