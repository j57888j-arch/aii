# StudyHelper — Foundation (Phase 1)

O‘zbekiston talabalari, abituriyentlari va ish izlovchilari uchun Telegram AI yordamchi. Ushbu repozitoriy master rejaning **1-bosqichi (Foundation)**ni o‘z ichiga oladi. AI chat, rejimlar, Stars billing, referal mukofotlari va Mini App keyingi alohida bosqichlarda ulanadi.

## Nimalar bor?

- aiogram 3.31 + FastAPI webhook / local polling.
- SQLAlchemy 2.0 async + asyncpg + qo‘lda yozilgan Alembic migration.
- PostgreSQL — doimiy ma'lumotlar manbai; Redis-compatible Key Value — FSM va qisqa muddatli rate limit.
- Uzbek (Latin), Russian, English onboarding.
- Foydalanuvchi upsert'i (birinchi `/start` poygasi uchun PostgreSQL `ON CONFLICT`).
- Admin ID faqat `ADMIN_IDS` env qiymatidan keladi; `users` jadvalida `is_admin` yo‘q.
- `/health` — liveness; `/ready` — PostgreSQL va Redis readiness (muammo bo‘lsa HTTP 503).
- Render Blueprint, Dockerfile, Docker Compose, GitHub Actions va UptimeRobot yo‘riqnomasi.

## Mahalliy ishga tushirish

Talab: Python 3.12, Docker va Docker Compose.

1. `.env.example` faylidan `.env` yarating va `BOT_TOKEN`ni to‘ldiring.
2. `docker compose up --build` buyrug‘ini bajaring.
3. `http://localhost:10000/health` orqali tekshiring; bot Telegram’da `/start` bilan javob beradi.

Yoki lokal Python muhitida:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# .env ichida MODE=polling va kerakli BOT_TOKEN bo‘lsin
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 10000
```

## Render Free deploy

1. Repozitoriyani GitHub’ga push qiling.
2. Render’da **New → Blueprint** tanlab ushbu repozitoriyani ulang. `render.yaml` Web Service, Postgres va Key Value’ni yaratadi.
3. Blueprint so‘ragan `BOT_TOKEN`, `ADMIN_IDS`, `WEBHOOK_SECRET_TOKEN`, `WEBHOOK_PATH_SECRET` qiymatlarini kiriting.
4. `WEBHOOK_BASE_URL`ni service nomi o‘zgargan bo‘lsa Render domeningizga moslang. Standart qiymat `https://studyhelper.onrender.com`.
5. `WEBHOOK_SECRET_TOKEN` va `WEBHOOK_PATH_SECRET` uchun URL-safe tasodifiy qiymat yarating:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Ikki qiymat uchun buyruqni alohida-alohida ishga tushiring. BotFather tokenini hech qachon GitHub’ga joylamang.

Deploy vaqtida `scripts/start.sh` `alembic upgrade head`ni bajaradi, keyin Uvicorn ishga tushadi. Render Postgres va Key Value bilan bir xil `frankfurt` region ishlatiladi; Redis va Postgres ichki connection string orqali ulanadi.

### Render Free haqida production ogohlantirishi

Render hujjatlariga ko‘ra, Free Postgres 1 GB bo‘lib 30 kundan keyin expire bo‘ladi (yana 14 kunlik upgrade grace period bor). Free Key Value 25 MB va persist qilinmaydi; restart bo‘lsa FSM, rate-limit va boshqa Redis ma'lumotlari yo‘qolishi mumkin. Free Web Service 15 daqiqa inbound traffic bo‘lmasa spin down qiladi. Free service'lar uchun oyiga workspace bo‘yicha 750 instance-soat ajratiladi. Shu sababli Render Free — demo, MVP va sinov uchun; pullik foydalanuvchi balanslari va moliyaviy ledger'ni uzoq muddat yuritish uchun Render Free Postgres'ga suyanmang. `DATABASE_URL`ni keyin muddati tugamaydigan boshqariladigan PostgreSQL provayderiga almashtirish mumkin.

## UptimeRobot sozlash

1. UptimeRobot’da **Add New Monitor → HTTP(s)** yarating.
2. Friendly Name: `StudyHelper Render Liveness`.
3. URL: `https://studyhelper.onrender.com/health` (o‘zingizning Render domeningizni kiriting).
4. Monitoring Interval: **5 minutes** (Free plan intervali).
5. Alert contact qo‘shing va monitorni saqlang.

`/health` faqat jarayon tirikligini tekshiradi va 200 qaytaradi. Har 5 daqiqadagi inbound ping Render’ning 15 daqiqalik idle spin-down muddatini odatda oldini oladi. Lekin bu uptime kafolati emas: 750 oylik instance-soat workspace bo‘yicha hisoblanadi, Render servisni restart qilishi mumkin, Free Postgres muddati esa baribir 30 kun. Qo‘shimcha monitoring uchun ikkinchi HTTP(s) monitorni `https://studyhelper.onrender.com/ready`ga qo‘ying; bu Postgres yoki Redis ishlamasa 503 qaytaradi. `/ready`ni Render healthCheckPath sifatida ishlatmang — Redis restartidan keyingi qisqa nosozliklar deploy/health signalini chalkashtirishi mumkin.

## Health endpointlar

- `GET /health` → har doim `200 {"status":"ok"}` (faqat process liveness; dependency tekshirmaydi).
- `GET /ready` → PostgreSQL `SELECT 1` va Redis `PING`; ikkisi ham ishlasa 200, aks holda 503.
- `GET /` → service va phase haqida minimal holat.
- `/docs` production’da o‘chirilgan.

## Muhit o‘zgaruvchilari

| Variable | Vazifasi |
|---|---|
| `BOT_TOKEN` | BotFather tokeni |
| `ADMIN_IDS` | Vergul bilan ajratilgan Telegram numeric ID'lar |
| `MODE` | `webhook` (Render) yoki `polling` (local) |
| `DATABASE_URL` | PostgreSQL URL; `postgres://` avtomatik `postgresql+asyncpg://`ga o‘tadi |
| `REDIS_URL` | Redis/Valkey connection URL |
| `WEBHOOK_BASE_URL` | HTTPS public Render domeni |
| `WEBHOOK_SECRET_TOKEN` | Telegram webhook header secret |
| `WEBHOOK_PATH_SECRET` | Maxfiy webhook URL path qismi |
| `DB_POOL_SIZE` | SQLAlchemy bazaviy pool (Render Free uchun 2) |
| `DB_MAX_OVERFLOW` | Qo‘shimcha DB ulanishlari (Render Free uchun 1) |
| `DB_POOL_TIMEOUT` | DB pool kutish vaqti, soniya |
| `APP_ENV`, `LOG_LEVEL`, `PORT`, `HOST` | Runtime sozlamalari |
| `DEFAULT_LANGUAGE`, `BUSINESS_TIMEZONE` | Til va biznes vaqti zonasi |
| `THROTTLE_LIMIT`, `THROTTLE_WINDOW_SECONDS` | Rate limit |
| `FSM_TTL_SECONDS` | Redis FSM state/data TTL |

## Test va sifat nazorati

```bash
pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest
```

DB migratsiyalarini lokal PostgreSQL bilan tekshirish:

```bash
docker compose up -d postgres redis
alembic upgrade head
alembic downgrade base
alembic upgrade head
```

## GitHub’dan olingan arxitektura ilhomlari

Quyidagi ochiq repozitoriylar stek mosligini va modul ajratish yondashuvini tekshirish uchun ko‘rib chiqildi; bu repozitoriyga ularning fayllari to‘liq ko‘chirilmadi. StudyHelper implementatsiyasi ushbu loyiha talablari uchun alohida yozilgan.

- [arturboyun/AiogramBotTemplate](https://github.com/arturboyun/AiogramBotTemplate) — aiogram, FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis; MIT.
- [bodaue/aiogram_v3_template](https://github.com/bodaue/aiogram_v3_template) — aiogram 3, SQLAlchemy 2, asyncpg, Alembic, Redis; MIT.
- [sm1ck/aiogram-fastapi-starter](https://github.com/sm1ck/aiogram-fastapi-starter) — bot/API/service separation, async SQLAlchemy, Redis, retry patterns; ushbu bosqichda ortiqcha Celery/ChromaDB qismlari qo‘shilmadi.

Amaldagi Telegram webhook, Redis FSM, Render Blueprint va Python paket versiyalari rasmiy hujjatlar asosida tanlandi. Aniq havolalar loyiha kodida emas, ushbu README va ChatGPT javobida berilgan.
