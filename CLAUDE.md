# RIZALTA BOT — Контекст для Claude

## ⛔ ОСОБО ВАЖНО
- **PROD (`/opt/bot`) — НЕ ТРОГАТЬ.** Никогда не редактировать, не копировать в, не рестартовать
- **Работаем ТОЛЬКО в `/opt/bot-dev`**
- Перед задачей: `git status` + `git pull`
- После задачи: `git add -A && git commit && git push`
- Деплой DEV→PROD делает ЧЕЛОВЕК, не Claude Code

## Проект

Telegram-бот AI-консультант для риэлторов RIZALTA Resort Belokurikha (Алтай). Помогает подбирать инвестиционные апартаменты, генерировать КП (коммерческие предложения), рассчитывать доходность (ROI), рассрочку, ипотеку, сравнивать с депозитом, бронировать показы, фиксировать клиентов в CRM (ri.rclick.ru). Версия 2.7.2. DEV бот: @rizaltatestdevop_bot (polling). PROD бот: @RealtMeAI_bot (webhook :8000).

## Инфраструктура

- **Сервер:** Timeweb, 4 vCPU, 8 GB RAM
- **DEV:** `/opt/bot-dev` — polling через run_polling.py
- **PROD:** `/opt/bot` — webhook через app.py (FastAPI, uvicorn :8000)
- **WebApp DEV:** `/opt/webapp-dev` (отдельный проект, не трогать)
- **WebApp PROD:** `/opt/webapp` (отдельный проект, не трогать)
- **Mini App:** Vercel (rizalta-miniapp.vercel.app), DEV с `?env=dev`

## Сервисы (systemd)

| Сервис | Среда | Что делает |
|--------|-------|-----------|
| rizalta-bot-dev.service | DEV | Telegram бот (polling) — можно рестартовать |
| rizalta-dev-api.service | DEV | API uvicorn :8002 (Mini App) — можно рестартовать |
| rizalta-dev-tunnel.service | DEV | Cloudflare Named Tunnel |
| rizalta-bot.service | PROD | Telegram бот (webhook :8000) — **НЕ ТРОГАТЬ** |
| rizalta-bot-max.service | — | RIZALTA MAX Bot (polling) |
| rizalta-watchdog.service | PROD | Мониторинг — не трогать |
| rizalta-webchat.service | — | WebChat Маргарита AI |

**Рестарт DEV:**
```bash
systemctl restart rizalta-bot-dev
systemctl restart rizalta-dev-api  # если менялся API
```

## Стек

Python 3, FastAPI, SQLite (WAL), OpenAI API (gpt-4o-mini), Telegram Bot API, wkhtmltopdf (HTML→PDF), PyPDF2 (склейка PDF), Pillow (сжатие изображений), openpyxl (Excel), aiohttp, python-dotenv, Cloudflare Tunnels

## Архитектура

### Entry Points

- **app.py** — PROD: FastAPI webhook + API endpoints (/api/lots, /api/miniapp-action, /telegram/webhook)
- **run_polling.py** — DEV: long polling, импортирует обработчики из app.py

### Потоки данных

1. **Сообщение пользователя** → run_polling.py → GPT Intent Router (services/intent_router.py) → handler
2. **Callback кнопка** → app.py/run_polling.py → callback router → handler (handlers/*.py)
3. **Голосовое сообщение** → Whisper STT (services/speech.py) → GPT Intent Router → handler
4. **Генерация КП** → handlers/kp.py → lot из units_db.py → kp_pdf_generator.py (HTML→wkhtmltopdf) → PDF
5. **Расчёт ROI** → handlers/calc_dynamic.py → services/calc_universal.py → текст или Excel (calc_xlsx_generator.py)
6. **Бронирование** → handlers/booking_calendar.py → SQLite → уведомление в группу (SHOWS_GROUP_ID)

### handlers/ — обработчики команд

| Файл | Что делает |
|------|-----------|
| menu.py | Навигация, /start, главное меню, WebApp кнопка (DEV) |
| kp.py | КП: навигация по лотам (building/floor/area/budget), пагинация, карточка лота, генерация PDF |
| ai_chat.py | Свободный текст → GPT intent → роутинг на нужный handler |
| calc_dynamic.py | Динамические расчёты ROI/рассрочки для любого лота |
| compare.py | Сравнение депозита vs RIZALTA (1/3/5/11 лет, 3 сценария, PDF) |
| units.py | Статические ROI/финансы для 3 флагманских юнитов (A209, B210, A305) |
| booking.py | Запись на онлайн-показ (контакт → уведомление менеджерам) |
| booking_calendar.py | Календарное бронирование (timezone, Mon-Sat 10-16, SQLite) |
| booking_fixation.py | Фиксация клиента на ri.rclick.ru (state machine: phone→password→client) |
| secretary.py | AI-секретарь: задачи/напоминания с датой, приоритетом, голосовым вводом |
| mortgage.py | Ипотека Совкомбанк 4.4% (ПВ 30-50%, grace period, PDF) |
| tranche_mortgage.py | Траншевая ипотека (3 транша × 8 мес, 20 лет, PDF) |
| mgp.py | МГП калькулятор (номерной + коммерческий, PDF) |
| compare.py | Депозит vs RIZALTA (3 сценария, налоги, PDF) |
| media.py | Презентации (6 PDF) и видео (9 файлов) |
| docs.py | Документы: ДДУ + договор аренды (PDF) |
| news.py | Дайджест: курсы ЦБ, погода Белокуриха, авиабилеты, RSS-новости |
| corp3.py | Корпус 3 whitelist (legacy, К3 теперь в штатном режиме) |
| domoplaner.py | Парсинг domoplaner.ru подборок → генерация КП |

### services/ — бизнес-логика

| Файл | Что делает |
|------|-----------|
| units_db.py | SQLite интерфейс к properties.db: лоты, этажи, фильтры, hidden buildings |
| intent_router.py | GPT-классификатор интентов (20+ типов) из текста/голоса |
| ai_chat.py | OpenAI Function Calling: Q&A + роутинг на функции бота |
| kp_pdf_generator.py | HTML→PDF через wkhtmltopdf: КП с планировкой, ценой, рассрочкой |
| calc_universal.py | Универсальный калькулятор ROI (11 лет) + рассрочка (12м/18м) |
| installment_calculator.py | **SSoT рассрочки:** 12м (0%), 18м (9%/7%/4% по ПВ), сервисный сбор 150K |
| mortgage_calculator.py | Совкомбанк: аннуитет 20/30 лет, grace period, ПВ 30-50% |
| tranche_mortgage_calculator.py | 3-транша × 8 мес, ставки по диапазонам цен |
| investment_calc.py | 11-летний инвестанализ (аренда + рост цены, occupancy) |
| deposit_calculator.py | Банковский депозит: 3 сценария, налог 13%/15%, прогноз ставок ЦБ |
| investment_compare.py | Сравнение: депозит vs RIZALTA (ROI, преимущество, таблица) |
| calc_xlsx_generator.py | Excel: 8-летний прогноз прибыли (2028-2035), pre-rent рост |
| kp_search.py | Поиск JPG планировок по коду/площади/бюджету |
| mgp_calculator.py | МГП: номерной (42717.4 м²) + коммерческий (42000 м²), 15 лет |
| compare_pdf_generator.py | PDF сравнение депозит vs RIZALTA |
| mortgage_pdf_generator.py | PDF ипотечный расчёт |
| tranche_mortgage_pdf_generator.py | PDF траншевая ипотека |
| data_loader.py | Загрузка JSON конфигов (units, finance, instructions, knowledge) |
| telegram.py | Telegram API обёртка (send_message, send_document, callbacks) |
| notifications.py | Уведомления: Telegram группа + email менеджерам |
| speech.py | OpenAI Whisper STT (ogg/mp3/wav/m4a → текст) |
| parser_rclick.py | Парсер ri.rclick.ru: HTML→units (code, building, floor, area, price) |
| rclick_service.py | API ri.rclick.ru: авторизация, токены (90 дней), отправка фиксаций |
| user_profiles.py | Профили риэлторов (имя, телефон, timezone MSK/Altai) |
| secretary_db.py | SQLite: задачи секретаря (текст, дата, время, приоритет, статус) |
| monitoring.py | Мониторинг нагрузки (req/min, RAM, алерты) |
| domoplaner_parser.py | Парсер domoplaner.ru подборок |
| calculations.py | Утилиты: fmt_rub, normalize_unit_code, портфельные сценарии |

## БД

### properties.db (SQLite WAL) — лоты К1+К2+К3

Заполняется парсером (cron DEV 06:00, PROD 03:00). DELETE + INSERT для К1+К2+К3.

| Поле | Тип | Описание |
|------|-----|----------|
| code | TEXT | Код лота (В713, A209) |
| building | INTEGER | Корпус (1=Family, 2=Business, 3=Digital) |
| floor | INTEGER | Этаж |
| rooms | TEXT | Тип (студия, 1к, 2к) |
| area_m2 | REAL | Площадь м² |
| price_rub | INTEGER | Цена ₽ |
| status | TEXT | available / sold |
| layout_url | TEXT | URL планировки |

### bot.db — бронирования и секретарь

| Таблица | Ключевые поля |
|---------|---------------|
| bookings | id, chat_id, date, time, timezone, status (pending/taken/confirmed), realtor_name, realtor_phone |
| tasks | id, chat_id, task_text, due_date, due_time, priority (urgent/high/normal/low), status (done/pending), client_name |
| user_profiles | chat_id PK, name, phone, timezone |

### corp3_access.db — whitelist К3

| Таблица | Поля |
|---------|------|
| corp3_whitelist | chat_id INTEGER PK |

### Конфиги (data/)

| Файл | Назначение |
|------|-----------|
| installment_config.json | Параметры рассрочки (ПВ %, ставки, сроки) |
| mortgage_config.json | Параметры ипотеки Совкомбанк |
| tranche_mortgage_config.json | Параметры траншевой ипотеки |
| rizalta_finance.json | Финансовые данные: defaults, units, programs |
| hidden_buildings.json | Скрытые корпуса {"hidden": [2]} |
| corp3_units.json | Старая база К3 (в .gitignore, legacy) |

## Корпуса

- **К1 «Family»:** ~256 лотов (building=1) — штатный режим
- **К2 «Business»:** ~104 лота (building=2) — **скрыт** (ценовая пауза)
- **К3 «Digital»:** ~116 available (building=3) — штатный режим

## Правила

- `/opt/bot/` — PROD. НИКОГДА не трогать без явной команды
- app.py НЕ копировать целиком в PROD (hardcoded пути /opt/bot-dev/)
- После деплоя: `grep -rn "/opt/bot-dev" /opt/bot/ --include="*.py"` — должно быть пусто
- Callback data: max 64 байта → кодирование area10 = int(area_m2 * 10)
- Inline buttons: max 100 кнопок → пагинация (PAGE_SIZE=50, MAX_BUTTONS=20)
- installment_calculator.py — **Single Source of Truth** для рассрочки

### Уроки из ошибок

- **DB_PATH баг (11.02):** PROD читал DEV данные — 7 файлов с hardcoded /opt/bot-dev/. Фикс: sed по всем файлам
- **Custom Installment баг (01.03):** коды В327/В615 совпадали между К1 и К3 — лоты К3 получали ограниченное КП. Фикс: проверка building==1
- **status=available баг (01.03):** только 1 из 9 SQL-запросов фильтровал по status. Фикс: AND status='available' во все запросы
- **Парсер DELETE (известная особенность):** parser_rclick.py делает DELETE перед INSERT — если корпус убран с сайта, пропадёт из БД
- **Клон сервера (29.01):** перехватывал webhook запросы. Решение: остановка клона

## .env ключи

| Ключ | Назначение |
|------|-----------|
| TELEGRAM_BOT_TOKEN | Telegram Bot API (разные боты DEV/PROD!) |
| OPENAI_API_KEY | OpenAI API |
| OPENAI_MODEL | Модель (gpt-4o-mini) |
| OPENAI_MAX_TOKENS | Лимит токенов (800) |
| MANAGER_CHAT_ID | ID менеджеров через запятую |
| MANAGER_EMAIL | Email менеджеров |
| BOT_EMAIL | Email отправителя |
| SMTP_HOST / SMTP_PORT / SMTP_USER / SMTP_PASSWORD | SMTP для email |
| VECTOR_STORE_ID | Не используется (можно удалить) |
| ASSISTANT_ID | Не используется (можно удалить) |
| TIMEWEB_API_TOKEN | API Timeweb |

## Docs (справочники)

- `docs/RIZALTA_CURRENT.md` — текущий статус, что сделано
- `docs/RIZALTA_ARCHITECTURE.md` — карта проекта для LLM
- `docs/RIZALTA_KNOWLEDGE.md` — бизнес-логика, формулы, решения
- `docs/RIZALTA_TASKS.md` — задачи и бэклог
- `docs/RIZALTA_CALLBACKS.md` — индекс ~120 callback паттернов
- `docs/RIZALTA_CONTEXT.md` — контекст системы и конфигурация
- `docs/OLLAMA_RIZALTA.md` — контекст для локальной модели (инциденты, диагностика)
- `SESSION_LOG.md` — последние 3 сессии (компактно)
- `BACKLOG.md` — невыполненные задачи по приоритетам

## Workflow

- **Claude.ai** = архитектор (планирование, исследование)
- **Claude Code** = исполнитель (кодинг, деплой в DEV)
- Деплой в PROD: только по явной команде человека
- Рестарт DEV: `systemctl restart rizalta-bot-dev`
- Health check: `curl localhost:8002/` (DEV API)
- Парсер: cron DEV 06:00, PROD 03:00 (`services/parser_rclick.py`)

## Промпты для Claude Code

Каждый промпт для Claude Code должен заканчиваться блоком:

```
Задача готова когда:
1. [проверяемое условие]
2. [проверяемое условие]
...
```

Правила формулировки:
- Каждый критерий проверяемый: "при X происходит Y", не "работает правильно"
- 3–6 критериев на задачу, не больше
- Включать: happy path, основной edge case, логирование если релевантно
- Не включать: очевидное (код запускается, нет синтаксических ошибок)
