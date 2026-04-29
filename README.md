# 🧾 Oilaviy Eslatmalar Telegram Boti

Bir nechta foydalanuvchilar uchun umumiy eslatmalar boti.

## 🚀 O'rnatish

### 1. Virtual muhit yaratish

```bash
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows
```

### 2. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 3. .env faylini sozlash

```bash
cp .env.example .env
```

`.env` faylini oching va to'ldiring:

```env
BOT_TOKEN=your_bot_token_here      # @BotFather dan olingan token
ADMIN_IDS=123456789,987654321      # Admin Telegram ID-lari (vergul bilan)
DATABASE_URL=sqlite+aiosqlite:///./reminders.db
TIMEZONE=Asia/Tashkent
```

### 4. Botni ishga tushirish

```bash
python main.py
```

---

## 📋 Buyruqlar

| Buyruq | Tavsif |
|--------|--------|
| `/start` | Botni boshlash va ro'yxatdan o'tish |
| `/add` | Yangi eslatma qo'shish |
| `/list` | Barcha kelajakdagi eslatmalarni ko'rish |
| `/delete` | Eslatmani o'chirish (ID orqali) |
| `/cancel` | Joriy amalni bekor qilish |
| `/help` | Yordam |

---

## 🏗 Arxitektura

```
reminder_bot/
├── main.py                          # Asosiy kirish nuqtasi
├── requirements.txt
├── .env.example
└── bot/
    ├── config.py                    # Sozlamalar
    ├── handlers/
    │   ├── states.py               # FSM holatlari
    │   ├── start.py                # /start
    │   ├── add_reminder.py         # /add
    │   ├── list_reminders.py       # /list
    │   └── delete_reminder.py      # /delete
    ├── services/
    │   ├── user_service.py         # Foydalanuvchi operatsiyalari
    │   └── reminder_service.py     # Eslatma operatsiyalari
    ├── models/
    │   ├── models.py               # SQLAlchemy modellari
    │   └── database.py             # DB engine va session
    ├── scheduler/
    │   └── reminder_scheduler.py   # APScheduler (har 60 soniya)
    └── middlewares/
        └── access.py               # Kirish nazorati
```

---

## 🔐 Admin qo'shish

`.env` faylidagi `ADMIN_IDS` ga Telegram ID qo'shing:

```env
ADMIN_IDS=123456789,987654321,111222333
```

Admin imkoniyatlari:
- Ixtiyoriy eslatmani o'chira oladi
- Boshqa userlarni boshqarish (kelajak versiyada)

---

## ⚙️ Muhit o'zgaruvchilari

| O'zgaruvchi | Majburiy | Tavsif |
|-------------|----------|--------|
| `BOT_TOKEN` | ✅ | Telegram bot tokeni |
| `ADMIN_IDS` | ✅ | Admin Telegram ID-lari |
| `DATABASE_URL` | ❌ | SQLite yo'li (default: `reminders.db`) |
| `TIMEZONE` | ❌ | Vaqt zonasi (default: `Asia/Tashkent`) |
