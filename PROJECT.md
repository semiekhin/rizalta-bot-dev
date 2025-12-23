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
| Версия DEV | 2.0.1 |
| Версия PROD | 2.0.0 |
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
| ADMIN_CHAT_ID | .env | Telegram ID админа |

**Правило:** токены НИКОГДА не коммитить, только в .env на сервере.

---

## 🏗️ АРХИТЕКТУРА
```
rizalta-bot/
├── app.py                 # Webhook, GPT Intent Router
├── run_polling.py         # Dev режим
├── handlers/              # Обработчики команд
│   ├── menu.py            # Главное меню
│   ├── ai_chat.py         # AI диалоги (GPT + Whisper)
│   ├── kp.py              # Коммерческие предложения
│   ├── secretary.py       # AI-Секретарь (NEW v2.0)
│   ├── media.py           # Презентации, видео
│   ├── compare.py         # Сравнение депозит vs RIZALTA
│   ├── booking_fixation.py # Фиксация клиентов
│   └── news.py            # Инвест-дайджест
├── services/              # Бизнес-логика
│   ├── intent_router.py   # GPT Intent Router (NEW v2.0)
│   ├── secretary_ai.py    # GPT парсинг задач (NEW v2.0)
│   ├── secretary_db.py    # SQLite для задач (NEW v2.0)
│   ├── telegram.py        # Telegram API
│   ├── kp_pdf_generator.py # Генератор PDF КП
│   ├── calc_universal.py  # Расчёты рассрочки
│   ├── calculations.py    # Финансовые расчёты
│   └── rclick_service.py  # Интеграция ri.rclick.ru
├── data/                  # Данные
│   ├── rizalta_knowledge_base.txt # База знаний AI
│   └── units.json         # Квартиры
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

# 3. Коммит prod
cd /opt/bot
git add -A && git commit -m "vX.X.X: описание" && git push
systemctl restart rizalta-bot
```

---

## 📊 МЕТРИКИ

| Метрика | Значение |
|---------|----------|
| Квартир в базе | 369 |
| Типов КП | 3 (100%, 12 мес, 12+18 мес) |
| Презентаций | 6 |
| Видео | 9 |
| Intent'ов GPT | 15+ |
| Uptime | Мониторинг каждые 5 мин |

---

## 🚨 РИСКИ

| Риск | Решение |
|------|---------|
| Prod упал | `systemctl restart rizalta-bot` + проверить логи |
| OpenAI заблокирован | Сервер в EU, обход РКН |
| Telegram недоступен | Cloudflare Tunnel |
| Потеря данных | Git + ежедневные бэкапы на email |

---

## 📝 TASKS

### Сейчас
- [x] GPT Intent Router — голосовые из любого меню ✅
- [x] AI-Секретарь — личный планировщик задач ✅
- [ ] ⚠️ Деплой v2.0.1 в prod (изменения процентов рассрочки)

### Backlog
- [ ] APScheduler для напоминаний секретаря
- [ ] Утренний дайджест (TTS)
- [ ] Специалисты для календаря (реальные ФИО, telegram_id)
- [ ] UptimeRobot (внешний мониторинг)
- [ ] Синхронизация данных между dev/prod

### Сделано (последние)
- [x] v2.0.1: Рассрочка 24→18 мес, проценты: 30%→+9%, 40%→+7%, 50%→+4%
- [x] v2.0.0: GPT Intent Router, AI-Секретарь, голос из любого меню
- [x] v1.9.6: Презентации (6 шт), Видео (9 шт), новый дизайн КП 100%

---

## 📜 CHANGELOG

**v2.0.1 (23.12.2025) — ТОЛЬКО DEV, НЕ ЗАДЕПЛОЕНО В PROD**
- Рассрочка 24 месяца → 18 месяцев
- Новые проценты удорожания: ПВ30%→+9%, ПВ40%→+7%, ПВ50%→+4%
- Обновлены: kp_pdf_generator.py, calc_universal.py, calculations.py
- Файлы КП: _12m_24m → _12m_18m

**v2.0.0 (23.12.2025) — ЗАДЕПЛОЕНО В PROD**
- GPT Intent Router — единая классификация всех сообщений
- Метазнания о боте в services/intent_router.py
- 15+ intent'ов: КП, расчёты, фиксация, шахматка, секретарь, новости
- AI-Секретарь — личный планировщик с голосовым вводом
- Голосовые команды работают из любого меню бота
- Убраны regex паттерны из app.py
- Убран режим секретаря (не нужен с GPT-роутингом)

**v1.9.6 (19.12.2025)**
- Презентации проекта: 6 документов с меню выбора
- Видео про Алтай: 9 видео (сжаты до <50 МБ)
- КП 100%: новый двухколоночный дизайн с блоком выгоды

**v1.9.5 (18.12.2025)**
- КП: 3 варианта (100%, 12 мес, 12+24 мес)
- Фиксация клиентов через ri.rclick.ru
- Сравнение депозит vs RIZALTA (данные ЦБ РФ)

---

## 🔄 HANDOFF

### Последняя сессия: 23.12.2025

**Что сделали:**

1. **GPT Intent Router v2.0.0** (задеплоено в prod)
   - Единая GPT классификация всех сообщений (голос + текст)
   - Метазнания о боте в services/intent_router.py
   - 15+ intent'ов с правилами приоритета
   - Голосовые команды работают из любого меню
   - "открой шахматку" → шахматка (не задача!)
   - Убраны regex паттерны, убран режим секретаря

2. **AI-Секретарь** (задеплоен в prod)
   - handlers/secretary.py — UI
   - services/secretary_ai.py — GPT парсинг задач
   - services/secretary_db.py — SQLite хранение
   - Кнопка "🗓 Секретарь" в главном меню

3. **Рассрочка v2.0.1** (⚠️ ТОЛЬКО DEV, НЕ ЗАДЕПЛОЕНО)
   - 24 месяца → 18 месяцев
   - Проценты: ПВ30%→+9%, ПВ40%→+7%, ПВ50%→+4%
   - Обновлены: kp_pdf_generator.py, calc_universal.py, calculations.py, handlers/kp.py

**Текущее состояние:**
- ✅ Dev v2.0.1 — протестирован, работает
- ✅ Prod v2.0.0 — работает (GPT Router + Секретарь)
- ⚠️ Prod НЕ имеет изменений рассрочки (18 мес, новые проценты)
- ✅ Git dev синхронизирован

**Что нужно сделать:**
1. Деплой v2.0.1 в prod (изменения рассрочки)
2. APScheduler для напоминаний секретаря
3. Утренний дайджест

**Файлы для деплоя v2.0.1:**
```bash
cp /opt/bot-dev/services/kp_pdf_generator.py /opt/bot/services/
cp /opt/bot-dev/services/calc_universal.py /opt/bot/services/
cp /opt/bot-dev/services/calculations.py /opt/bot/services/
cp /opt/bot-dev/handlers/kp.py /opt/bot/handlers/
cp /opt/bot-dev/handlers/domoplaner.py /opt/bot/handlers/
cp /opt/bot-dev/app.py /opt/bot/
systemctl restart rizalta-bot
```

---

## 📎 ССЫЛКИ НА ФАЙЛЫ

**Документация:**
- https://raw.githubusercontent.com/semiekhin/rizalta-bot-dev/main/PROJECT.md
- https://raw.githubusercontent.com/semiekhin/rizalta-bot-dev/main/CLAUDE.md
- https://raw.githubusercontent.com/semiekhin/rizalta-bot-dev/main/PROJECT_HISTORY.md

**Ключевые файлы v2.0:**
- https://raw.githubusercontent.com/semiekhin/rizalta-bot-dev/main/app.py
- https://raw.githubusercontent.com/semiekhin/rizalta-bot-dev/main/services/intent_router.py
- https://raw.githubusercontent.com/semiekhin/rizalta-bot-dev/main/handlers/secretary.py
- https://raw.githubusercontent.com/semiekhin/rizalta-bot-dev/main/services/secretary_ai.py
- https://raw.githubusercontent.com/semiekhin/rizalta-bot-dev/main/services/secretary_db.py

**КП и расчёты:**
- https://raw.githubusercontent.com/semiekhin/rizalta-bot-dev/main/handlers/kp.py
- https://raw.githubusercontent.com/semiekhin/rizalta-bot-dev/main/services/kp_pdf_generator.py
- https://raw.githubusercontent.com/semiekhin/rizalta-bot-dev/main/services/calc_universal.py
- https://raw.githubusercontent.com/semiekhin/rizalta-bot-dev/main/services/calculations.py

**Остальные:**
- https://raw.githubusercontent.com/semiekhin/rizalta-bot-dev/main/services/telegram.py
- https://raw.githubusercontent.com/semiekhin/rizalta-bot-dev/main/config/settings.py
