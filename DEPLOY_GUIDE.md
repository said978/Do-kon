# 🚀 DO'KON POS Loyihasini PaaS (Render / Railway) Ga Yuklash Bo'yicha To'liq Qo'llanma

Ushbu qo'llanma yordamida loyihangizni bir necha daqiqada internetga chiqarib, **https://...** manzili ostida 24/7 ishlatishingiz mumkin.

---

## 📦 1-Qadam: Kodni GitHub ga Yuklash

Agar loyihangiz hali GitHub ga yuklanmagan bo'lsa, quyidagi buyruqlarni terminalda bajaring:

```bash
# 1. Git repozitoriyni initsializatsiya qilish
git init

# 2. Barcha tayyorlangan fayllarni qo'shish
git add .

# 3. Birinchi commit qilish
git commit -m "DO'KON POS: PaaS production versiyasi tayyor"

# 4. Asosiy tarmoqni main qilish
git branch -M main

# 5. O'zingizning GitHub repozitoriyangizni ulash:
# (GitHub.com da yangi 'dokon-pos' nomli bo'sh repozitoriy ochib, uning havolasini qo'yasiz)
git remote add origin https://github.com/SIZNING_LOGININGIZ/dokon-pos.git

# 6. Kodni yuklash
git push -u origin main
```

---

## 🌟 2-Qadam: PaaS Platformasida Ishga Tushirish

### 🥇 1-Variant: Render.com da Ishga Tushirish (Tavsiya etiladi — Bepul boshlash mumkin)

Render.com uchun loyihada **`render.yaml`** blueprint fayli tayyorlab qo'yilgan.

1. **[Render.com](https://render.com)** saytiga kiring va GitHub akkountingiz orqali ro'yxatdan o'ting (**Sign Up with GitHub**).
2. Bosh sahifada yuqoridagi **"New +"** tugmasini bosing va **"Blueprint"** ni tanlang.
3. GitHub dagi **`dokon-pos`** repozitoriyangizni tanlang.
4. Render loyiha ichidagi `render.yaml` faylini avtomatik o'qiydi:
   - ✅ **dokon-pos (Web Service)** — Docker orqali ishlaydigan veb-saytingiz.
   - ✅ **dokon-db (PostgreSQL)** — Ma'lumotlar bazangiz.
5. **"Apply"** tugmasini bosing!
6. **Natija:** Render 2-3 daqiqada bazani yaratadi, dasturni quradi, barcha statik fayllarni yig'adi va sizga internetda ishlaydigan xavfsiz havola beradi:
   👉 **`https://dokon-pos-xxxx.onrender.com`**

---

### 🥈 2-Variant: Railway.app da Ishga Tushirish (Juda tezkor)

1. **[Railway.app](https://railway.app)** saytiga kiring va GitHub orqali kiring.
2. **"New Project"** -> **"Deploy from GitHub repo"** -> **`dokon-pos`** repozitoriyangizni tanlang.
3. Loyiha oynasida **"+ Create"** -> **"Database"** -> **"Add PostgreSQL"** tugmasini bosing.
4. PostgreSQL yaratilgach, uning **Variables** bo'limidan `DATABASE_URL` qiymatini oling.
5. Veb-servisingizning **Variables** bo'limiga quyidagilarni kiriting:
   - `DATABASE_URL`: `${{Postgres.DATABASE_URL}}`
   - `DEBUG`: `False`
   - `SECRET_KEY`: `maxfiy-kalit-yozasiz`
6. **Networking** bo'limida **"Generate Domain"** tugmasini bosing.
7. **Natija:** Sizga tayyor domen taqdim etiladi:
   👉 **`https://dokon-pos-production.up.railway.app`**

---

## 👤 3-Qadam: Bulutda Admin (Superuser) Yaratish

Loyiha birinchi marta deploy qilinganda bosh admin akkountini ochish kerak:

* **Render.com da:**
  Veb-servisingiz sahifasiga kiring -> **"Shell"** tabiga o'ting va quyidagi buyruqni yozing:
  ```bash
  python manage.py createsuperuser
  ```
  Ism, email va parol kiriting.

* **Railway.app da:**
  Veb-servis ustiga bosing -> **"Exec"** (yoki **"CLI"**) tugmasini bosing va xuddi shu buyruqni bering.

---

## 🌐 4-Qadam: Shaxsiy Domen (.uz) Ulash (Ixtiyoriy)

Agar o'zingizning masalan `pos.dokon.uz` yoki `mening-dokonim.uz` domeningiz bo'lsa:
1. Render yoki Railway dagi **"Custom Domains"** bo'limiga kiring.
2. O'z domeningizni kiriting.
3. Platforma ko'rsatgan `CNAME` yoki `A record` yozuvini domen provayderingiz (masalan, Eskiz, Regos, Cpanel) sozlamalariga kiriting.
4. Tizim avtomatik ravishda bepul **SSL (HTTPS)** sertifikatini ulab beradi.

---

## 🛡️ Afzalliklari:
- ✅ **Avtomatik yangilanish (CI/CD):** Kelgusida kodga biron o'zgartirish kiritib GitHub ga `git push` qilsangiz, PaaS avtomatik tarzda 1 daqiqada yangi versiyani internetda yangilab qo'yadi.
- ✅ **Ma'lumotlar xavfsizligi:** Baza bulutda saqlanadi, kompyuter o'chib qolsa ham savdolar va hisobotlar saqlanib qoladi.
- ✅ **Barcha qurilmalardan kirish:** Dunyoning istalgan joyidan kompyuter, planshet va telefon orqali kassa va admin panelga kirish mumkin.
