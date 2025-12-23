# RIZALTA_CURRENT_TASK.md

## 📅 Сессия 23.12.2025

### ✅ Что сделано

**GPT Intent Router v2.0.0** (задеплоено в prod)
- Создан `services/intent_router.py` с метазнаниями о боте
- Единая GPT классификация всех сообщений (голос + текст)
- 15+ intent'ов: КП, расчёты, фиксация, шахматка, секретарь, новости
- Правила приоритета: "открой шахматку" → action (не задача!)
- Исправление ошибок Whisper: "напомню" → "напомни"
- Убраны regex паттерны из app.py
- Убран режим секретаря (не нужен с GPT-роутингом)

**AI-Секретарь** (задеплоен в prod)
- `handlers/secretary.py` — UI секретаря
- `services/secretary_ai.py` — GPT парсинг задач
- `services/secretary_db.py` — SQLite хранение (secretary.db)
- Кнопка "🗓 Секретарь" добавлена в главное меню
- Голосовой ввод задач работает из любого места

**Рассрочка v2.0.1** (⚠️ ТОЛЬКО DEV)
- 24 месяца → 18 месяцев
- Новые проценты: ПВ30%→+9%, ПВ40%→+7%, ПВ50%→+4%
- Было: ПВ30%→+12%, ПВ40%→+9%, ПВ50%→+6%
- Файлы КП: `_12m_24m.pdf` → `_12m_18m.pdf`
- Параметр: `include_24m` → `include_18m`

### 🟢 Текущий статус

| Среда | Версия | Статус |
|-------|--------|--------|
| Dev | 2.0.1 | ✅ Работает, протестировано |
| Prod | 2.0.0 | ✅ Работает (GPT Router + Секретарь) |

**⚠️ ВАЖНО:** Изменения рассрочки (18 мес, новые проценты) НЕ задеплоены в prod!

### 🔜 Следующие задачи

1. **Деплой v2.0.1 в prod** — изменения рассрочки
   ```bash
   cp /opt/bot-dev/services/kp_pdf_generator.py /opt/bot/services/
   cp /opt/bot-dev/services/calc_universal.py /opt/bot/services/
   cp /opt/bot-dev/services/calculations.py /opt/bot/services/
   cp /opt/bot-dev/handlers/kp.py /opt/bot/handlers/
   cp /opt/bot-dev/handlers/domoplaner.py /opt/bot/handlers/
   cp /opt/bot-dev/app.py /opt/bot/
   systemctl restart rizalta-bot
   ```

2. **APScheduler для напоминаний** — секретарь не отправляет напоминания
3. **Утренний дайджест** — функция есть, нужен cron/scheduler
4. **Специалисты для календаря** — все указывают на один telegram_id

### 📁 Изменённые файлы

**Новые файлы (v2.0.0):**
- `services/intent_router.py` — GPT классификатор + метазнания

**Изменённые файлы (v2.0.0):**
- `app.py` — GPT роутер вместо regex
- `handlers/secretary.py` — убран режим секретаря
- `services/secretary_db.py` — убран режим секретаря
- `handlers/__init__.py` — экспорты секретаря
- `config/settings.py` — кнопка секретаря в меню

**Изменённые файлы (v2.0.1):**
- `services/kp_pdf_generator.py` — calc_24→calc_18, проценты
- `services/calc_universal.py` — расчёты рассрочки 18 мес
- `services/calculations.py` — тексты и расчёты
- `handlers/kp.py` — include_24m→include_18m, тексты кнопок
- `handlers/domoplaner.py` — include_24m→include_18m

---

## 📅 Сессия 19.12.2025

### ✅ Что сделано
- Презентации проекта: 6 PDF документов с меню выбора
- Видео про Алтай: 9 видео (сжаты ffmpeg до <50 МБ)
- КП 100%: новый двухколоночный дизайн с блоком выгоды
- Функция send_video в telegram.py

### 🟢 Текущий статус
- Версия: 1.9.6
- Dev: работает ✅
- Prod: задеплоено ✅

---

## 📅 Сессия 18.12.2025

### ✅ Что сделано
- КП: 3 варианта (100%, 12 мес, 12+24 мес)
- Фиксация клиентов через ri.rclick.ru
- Сравнение депозит vs RIZALTA

### 🟢 Текущий статус
- Версия: 1.9.5
