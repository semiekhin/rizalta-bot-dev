# PROJECT.md — RIZALTA AI SYSTEM

## 🤖 CLAUDE: СТАРТ СЕССИИ

**При открытии этого файла:**
1. Прочитай секцию QUICK INFO — пойми что за проект
2. Прочитай HANDOFF — пойми где остановились
3. Загрузи файлы из секции КЛЮЧЕВЫЕ ФАЙЛЫ если нужно
4. Скажи что понял и спроси задачу

**Контрольные слова:**
- `актуализируем` → обновить документацию, commit, push (оба репо)
- `переходим в новый чат` → актуализация + выдать ссылку на этот файл

**Стандарт разработки:**
https://raw.githubusercontent.com/semiekhin/developer-standards/main/DEV_STANDARD.md

---

## 📋 QUICK INFO

| Параметр | Значение |
|----------|----------|
| Проект | RIZALTA AI SYSTEM — AI-консультант для риэлторов |
| Продукт | Инвестиционная недвижимость RIZALTA Resort Belokurikha (Алтай) |
| Версия DEV | 2.1.1 |
| Версия PROD | 2.1.1 |
| Стек | Python 3.12 · FastAPI · OpenAI GPT-4o-mini · Whisper · SQLite |
| Prod бот | @RealtMeAI_bot |
| Dev бот | @rizaltatestdevop_bot |

**Репозитории:**
- Dev: https://github.com/semiekhin/rizalta-bot-dev
- Prod: https://github.com/semiekhin/rizalta-bot

**Сервер:**
```bash
ssh -p 2222 root@72.56.64.91
```

**Пути:**
- `/opt/bot` — prod (webhook, порт 8000)
- `/opt/bot-dev` — dev (polling)

---

## 🔐 СЕКРЕТЫ

| Переменная | Где лежит | Назначение |
|------------|-----------|------------|
| TELEGRAM_BOT_TOKEN | /opt/bot/.env | Prod бот токен |
| TELEGRAM_BOT_TOKEN_DEV | /opt/bot-dev/.env | Dev бот токен |
| OPENAI_API_KEY | .env | GPT-4o-mini, Whisper |
| ADMIN_CHAT_ID | .env | Telegram ID админа (512319063) |

**Правило:** токены НИКОГДА не коммитить, только в .env на сервере.

---

## 🏗️ АРХИТЕКТУРА
```
rizalta-bot/
├── app.py                 # Webhook, GPT Intent Router, startup_event
├── run_polling.py         # Dev режим (polling, reminder_loop, monitoring_loop)
├── handlers/              # Обработчики команд
│   ├── menu.py            # Главное меню
│   ├── ai_chat.py         # AI диалоги (GPT + Whisper)
│   ├── kp.py              # КП + универсальная навигация + пагинация
│   ├── secretary.py       # AI-Секретарь + timezone (v2.1.1)
│   ├── media.py           # Презентации, видео
│   ├── compare.py         # Сравнение депозит vs RIZALTA
│   ├── booking_fixation.py # Фиксация клиентов
│   └── news.py            # Инвест-дайджест
├── services/              # Бизнес-логика
│   ├── intent_router.py   # GPT Intent Router
│   ├── monitoring.py      # Мониторинг нагрузки (NEW v2.1.1)
│   ├── secretary_ai.py    # GPT парсинг задач
│   ├── secretary_db.py    # SQLite + timezone (v2.1.1)
│   ├── telegram.py        # Telegram API
│   ├── kp_pdf_generator.py # Генератор PDF КП
│   ├── calc_universal.py  # Расчёты рассрочки 12/18 мес
│   ├── units_db.py        # БД 348 лотов (v2.1.0)
│   └── rclick_service.py  # Интеграция ri.rclick.ru
├── data/                  # Данные
│   ├── rizalta_knowledge_base.txt # База знаний AI
│   └── units.json         # Квартиры
├── properties.db          # 348 лотов (v2.1.0)
├── secretary.db           # Задачи + users (timezone)
├── monitoring.db          # Статистика запросов (v2.1.1)
├── presentations/         # 6 PDF презентаций
└── videos/                # 9 видео про Алтай
```

---

## ⚙️ УПРАВЛЕНИЕ

**Dev:**
```bash
cd /opt/bot-dev
source venv/bin/activate
systemctl restart rizalta-bot-dev
journalctl -u rizalta-bot-dev -f
```

**Prod:**
```bash
cd /opt/bot
source venv/bin/activate
systemctl restart rizalta-bot
journalctl -u rizalta-bot -f
```

**Деплой (dev → prod):**
```bash
# 1. Тест в dev, потом:
cd /opt/bot-dev
git add -A && git commit -m "vX.X.X: описание" && git push

# 2. Копировать изменённые файлы
cp /opt/bot-dev/[файлы] /opt/bot/

# 3. Исправить пути
sed -i 's|/opt/bot-dev|/opt/bot|g' /opt/bot/[файл]

# 4. Проверка + коммит prod
cd /opt/bot
python3 -c "import app; print('OK')"
systemctl restart rizalta-bot
git add -A && git commit -m "vX.X.X: описание" && git push
```

---

## 📊 МЕТРИКИ

| Метрика | Значение |
|---------|----------|
| Лотов в базе | 348 (было 69) |
| Корпус 1 Family | 244 лота |
| Корпус 2 Business | 104 лота |
| Дублей кодов | 70 |
| Типов КП | 3 (100%, 12 мес, 12+18 мес) |
| Часовых поясов | 11 (UTC+2 — UTC+12) |
| Презентаций | 6 |
| Видео | 9 |
| Intent'ов GPT | 15+ |

---

## 🚨 МОНИТОРИНГ (v2.1.1)

| Алерт | Порог |
|-------|-------|
| Запросы/мин | >30 → уведомление |
| RAM | >50% → уведомление |
| Отчёт | Ежедневно 20:00 |
```bash
# Проверка статистики
sqlite3 /opt/bot/monitoring.db "SELECT COUNT(*) FROM stats"
```

---

## 📝 TASKS

### Следующие задачи
- [ ] Кеширование GPT ответов (узкое место OpenAI API)
- [ ] Redis при >500 активных users
- [ ] PostgreSQL при >2000 users
- [ ] Специалисты для календаря (реальные ФИО, telegram_id)
- [ ] UptimeRobot (внешний мониторинг)

### Сделано (v2.1.x)
- [x] 348 лотов вместо 69
- [x] Универсальная навигация Корпус → Этаж → Лоты
- [x] Пагинация "Показать ещё N лотов"
- [x] Обработка 70 дублей кодов
- [x] Поиск по бюджету ±10%
- [x] Рассрочка 12/18 месяцев
- [x] Часовые пояса (11 зон России)
- [x] Напоминания через фоновую задачу (не cron)
- [x] Мониторинг нагрузки с алертами
- [x] Убрана массовая генерация КП

### Сделано (v2.0.x)
- [x] GPT Intent Router — голосовые из любого меню
- [x] AI-Секретарь — личный планировщик задач

---

## 📜 CHANGELOG

**v2.1.1 (24.12.2025) — ЗАДЕПЛОЕНО В PROD**
- Мониторинг нагрузки (services/monitoring.py)
- Алерты: >30 req/min, RAM >50%, ежедневный отчёт 20:00
- 11 часовых поясов России (UTC+2 — UTC+12)
- Таблица users с timezone в secretary.db
- Кнопка "🕐 Часовой пояс" в меню секретаря
- Напоминания через фоновую задачу (reminder_loop)
- Убрана массовая генерация КП (кнопка "Все КП этажа")

**v2.1.0 (24.12.2025) — ЗАДЕПЛОЕНО В PROD**
- 348 лотов вместо 69 (полная база с сайта)
- Универсальная навигация: Корпус → Этаж → Лоты
- Пагинация "Показать ещё N лотов" с кешем _search_cache
- Обработка 70 дублей кодов (выбор корпуса)
- Поиск по бюджету ±10% от суммы
- Рассрочка 12 и 18 месяцев (было 12 и 24)
- GPT Intent Router с правилами приоритетов

**v2.0.0 (23.12.2025)**
- GPT Intent Router — единая классификация всех сообщений
- AI-Секретарь — личный планировщик с голосовым вводом
- Голосовые команды работают из любого меню бота

**v1.9.6 (19.12.2025)**
- Презентации проекта: 6 документов
- Видео про Алтай: 9 видео
- КП 100%: новый двухколоночный дизайн

---

## 🔄 HANDOFF

### Последняя сессия: 24.12.2025

**Что сделали:**

1. **Полная база 348 лотов (v2.1.0)**
   - get_lots_filtered() без лимита
   - Навигация Корпус → Этаж → Лоты
   - Пагинация через _search_cache[chat_id]
   - 70 дублей кодов с выбором корпуса

2. **Часовые пояса (v2.1.1)**
   - 11 зон России (UTC+2 — UTC+12)
   - Таблица users в secretary.db
   - Кнопка смены в меню секретаря
   - reminder_loop() учитывает timezone каждого пользователя

3. **Мониторинг (v2.1.1)**
   - services/monitoring.py
   - Алерты: >30 req/min, RAM >50%
   - Ежедневный отчёт 20:00
   - log_request() в webhook handler

4. **Убрана массовая генерация КП**
   - Кнопка "📦 Все КП этажа" удалена
   - Снижена нагрузка на сервер

5. **Напоминания через фоновую задачу**
   - Убран cron
   - asyncio.create_task(reminder_loop()) в startup_event
   - За 15 минут до события со звуком

**Текущее состояние:**
- ✅ Dev v2.1.1 — работает
- ✅ Prod v2.1.1 — работает
- ✅ DEV/PROD синхронизированы
- ✅ Мониторинг активен
- ✅ Git синхронизирован

**Что нужно сделать:**
1. Кеширование GPT ответов (узкое место при масштабировании)
2. Redis при >500 users
3. PostgreSQL при >2000 users

---

## 📎 ССЫЛКИ НА ФАЙЛЫ

**Документация:**
- https://raw.githubusercontent.com/semiekhin/rizalta-bot-dev/main/PROJECT.md
- https://raw.githubusercontent.com/semiekhin/rizalta-bot-dev/main/CLAUDE.md
- https://raw.githubusercontent.com/semiekhin/rizalta-bot/main/RIZALTA_PROJECT.md
- https://raw.githubusercontent.com/semiekhin/rizalta-bot/main/RIZALTA_CURRENT_TASK.md
- https://raw.githubusercontent.com/semiekhin/rizalta-bot/main/RIZALTA_KNOWLEDGE.md

**Ключевые файлы v2.1.x:**
- https://raw.githubusercontent.com/semiekhin/rizalta-bot/main/app.py
- https://raw.githubusercontent.com/semiekhin/rizalta-bot-dev/main/run_polling.py
- https://raw.githubusercontent.com/semiekhin/rizalta-bot/main/services/monitoring.py
- https://raw.githubusercontent.com/semiekhin/rizalta-bot/main/handlers/kp.py
- https://raw.githubusercontent.com/semiekhin/rizalta-bot/main/handlers/secretary.py
- https://raw.githubusercontent.com/semiekhin/rizalta-bot/main/services/secretary_db.py
- https://raw.githubusercontent.com/semiekhin/rizalta-bot/main/services/units_db.py

**Секретарь и Intent Router:**
- https://raw.githubusercontent.com/semiekhin/rizalta-bot/main/services/intent_router.py
- https://raw.githubusercontent.com/semiekhin/rizalta-bot/main/services/secretary_ai.py

**КП и расчёты:**
- https://raw.githubusercontent.com/semiekhin/rizalta-bot/main/services/kp_pdf_generator.py
- https://raw.githubusercontent.com/semiekhin/rizalta-bot/main/services/calc_universal.py
- https://raw.githubusercontent.com/semiekhin/rizalta-bot/main/services/calculations.py
