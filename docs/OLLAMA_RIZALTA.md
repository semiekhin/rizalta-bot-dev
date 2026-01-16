# OLLAMA_RIZALTA.md
# Контекст проекта RIZALTA для локальных AI-моделей
# Версия: 1.0.0 | Дата: 16.01.2026

---

## 🎯 КАК ИСПОЛЬЗОВАТЬ ЭТОТ ФАЙЛ

**Перед началом работы** скопируй содержимое этого файла в чат с моделью.

**Приоритет моделей:**
1. `gpt-oss:120b` — сложные задачи, архитектура, рефакторинг
2. `deepseek-r1:32b` — reasoning, планирование, анализ
3. `gpt-oss:20b` — ежедневные задачи
4. `qwen2.5-coder:32b` — быстрые фиксы, простой код

**Формат работы:** Браузер (Open WebUI или аналог)

---

## ⚠️ КРИТИЧЕСКОЕ ПРАВИЛО

```
╔══════════════════════════════════════════════════════════════╗
║           PROD НЕ ТРОГАТЬ! РАБОТАТЬ ТОЛЬКО В DEV!            ║
╠══════════════════════════════════════════════════════════════╣
║  DEV:  /opt/bot-dev  →  @rizaltatestdevop_bot (polling)      ║
║  PROD: /opt/bot      →  @RealtMeAI_bot (webhook)             ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 📋 О ПРОЕКТЕ

**RIZALTA AI System v2.4.2** — Telegram-бот AI-консультант для риэлторов.
Продаёт инвестиционную недвижимость RIZALTA Resort Belokurikha (Алтай).

### Инфраструктура
- **Сервер:** `ssh -p 2222 root@72.56.64.91`
- **DEV:** `/opt/bot-dev` (polling, тестирование)
- **PROD:** `/opt/bot` (webhook :8000, боевой)
- **Mini App:** `/opt/miniapp` → https://rizalta-miniapp.vercel.app

### Стек
Python 3.12 · FastAPI · GPT-4o-mini · Whisper · SQLite · Cloudflare Tunnel

### Репозитории
- DEV: github.com/semiekhin/rizalta-bot-dev
- PROD: github.com/semiekhin/rizalta-bot
- Mini App: github.com/semiekhin/rizalta-miniapp

---

## 📁 СТРУКТУРА ПРОЕКТА

```
/opt/bot-dev/
├── app.py                      # Главный файл (роутинг, webhook, API)
├── run_polling.py              # DEV режим
├── properties.db               # БД лотов (350 записей)
├── secretary.db                # БД секретаря
│
├── config/
│   └── settings.py             # Константы, кнопки меню
│
├── data/
│   ├── installment_config.json # ⭐ ЕДИНЫЙ ИСТОЧНИК рассрочки
│   ├── units.json              # Данные лотов (legacy, для AI)
│   └── rizalta_finance.json    # Финансовые параметры
│
├── handlers/                   # Обработчики callback'ов
│   ├── kp.py                   # КП + навигация + пагинация
│   ├── calc_dynamic.py         # Расчёты ROI
│   ├── booking.py              # Онлайн-показы
│   ├── secretary.py            # AI-секретарь
│   └── ...
│
├── services/                   # Бизнес-логика
│   ├── installment_calculator.py  # ⭐ Расчёты рассрочки (SSOT)
│   ├── kp_pdf_generator.py     # PDF генератор КП
│   ├── units_db.py             # Работа с БД лотов
│   ├── parser_rclick.py        # Парсер сайта застройщика
│   ├── investment_calc.py      # Расчёты ROI
│   ├── intent_router.py        # GPT Intent Router
│   └── ...
│
└── docs/                       # Документация
    ├── RIZALTA_CONTEXT.md
    ├── RIZALTA_CURRENT.md
    ├── RIZALTA_ARCHITECTURE.md
    ├── RIZALTA_KNOWLEDGE.md
    └── RIZALTA_TASKS.md
```

---

## 🗄️ БАЗА ДАННЫХ

### properties.db — лоты недвижимости (350 записей)

```sql
CREATE TABLE units (
    id INTEGER PRIMARY KEY,
    code TEXT,              -- "В708", "А101"
    project TEXT DEFAULT 'Rizalta',
    building INTEGER,       -- 1 = Family, 2 = Business
    floor INTEGER,
    rooms INTEGER,
    area_m2 REAL,
    price_rub INTEGER,
    price_per_m2_rub INTEGER,
    completion TEXT,        -- срок сдачи
    layout_url TEXT,
    page_url TEXT,
    status TEXT DEFAULT 'available',
    block_section INTEGER,
    updated_at TIMESTAMP
);
```

**Полезные запросы:**
```bash
# Все лоты
sqlite3 /opt/bot-dev/properties.db "SELECT COUNT(*) FROM units;"

# Лоты по корпусу
sqlite3 /opt/bot-dev/properties.db "SELECT code, area_m2, price_rub FROM units WHERE building=1 LIMIT 10;"

# Найти по коду
sqlite3 /opt/bot-dev/properties.db "SELECT * FROM units WHERE code='В708';"

# Статистика цен
sqlite3 /opt/bot-dev/properties.db "SELECT MIN(price_rub), MAX(price_rub), AVG(price_rub) FROM units;"
```

---

## 🔧 ЧАСТЫЕ КОМАНДЫ

### Управление сервисами
```bash
# DEV
systemctl restart rizalta-bot-dev
journalctl -u rizalta-bot-dev -f

# PROD (осторожно!)
systemctl restart rizalta-bot
journalctl -u rizalta-bot -f
```

### Парсинг данных
```bash
# DEV
cd /opt/bot-dev && python3 services/parser_rclick.py

# PROD
cd /opt/bot && /opt/bot/venv/bin/python3 services/parser_rclick.py
```

### Git
```bash
cd /opt/bot-dev
git add -A && git commit -m "v2.4.x: описание" && git push
```

### Тестирование
```bash
cd /opt/bot-dev
source venv/bin/activate

# Тест КП
python3 -c "from services.kp_pdf_generator import generate_kp_pdf; print(generate_kp_pdf(code='В101', include_18m=True, output_dir='/tmp'))"

# Тест расчётов
python3 -c "from services.installment_calculator import calculate_installment; print(calculate_installment(15000000, 50, 12))"
```

---

## 📝 ТИПОВЫЕ ЗАДАЧИ С РЕШЕНИЯМИ

---

### ЗАДАЧА 1: Изменить параметры рассрочки

**Файл:** `/opt/bot-dev/data/installment_config.json`

**Структура конфига:**
```json
{
  "programs": {
    "12_months": {
      "duration_months": 12,
      "markup_percent": 0,
      "variants": [
        {"down_payment_percent": 30, "description": "12 равных платежей"},
        {"down_payment_percent": 40, "description": "11×200К + остаток"},
        {"down_payment_percent": 50, "description": "11×100К + остаток"}
      ]
    },
    "18_months": {
      "duration_months": 18,
      "variants": [
        {"down_payment_percent": 30, "markup_percent": 9},
        {"down_payment_percent": 40, "markup_percent": 7},
        {"down_payment_percent": 50, "markup_percent": 4}
      ]
    }
  }
}
```

**Шаги:**
1. Редактировать `/opt/bot-dev/data/installment_config.json`
2. Перезапустить: `systemctl restart rizalta-bot-dev`
3. Протестировать в @rizaltatestdevop_bot
4. Скопировать в PROD: `cp /opt/bot-dev/data/installment_config.json /opt/bot/data/`
5. Перезапустить PROD: `systemctl restart rizalta-bot`

**Файлы которые используют конфиг:**
- `services/installment_calculator.py` — расчёты
- `services/kp_pdf_generator.py` — PDF КП
- `services/calc_universal.py` — UI расчёты

---

### ЗАДАЧА 2: Добавить лот в Custom Installment (спец-условия)

**Файл:** `/opt/bot-dev/services/kp_pdf_generator.py`

**Найти:**
```python
CUSTOM_INSTALLMENT_UNITS = ['В615', 'В527', 'В517', 'В617', 'В525', 'В625', 'А101']
```

**Добавить код лота в список.**

**Также проверить:** `/opt/bot-dev/handlers/kp.py` — там скрывается кнопка "КП с рассрочкой 12+18 мес"

**Быстрая команда:**
```bash
# Добавить В700
sed -i "s/CUSTOM_INSTALLMENT_UNITS = \[/CUSTOM_INSTALLMENT_UNITS = ['В700', /" /opt/bot-dev/services/kp_pdf_generator.py
```

---

### ЗАДАЧА 3: Обновить (спарсить) базу данных лотов

**Парсер:** `/opt/bot-dev/services/parser_rclick.py`
**Источник:** https://ri.rclick.ru/catalog/more/ (CATALOG_ID = 340)

**Команды:**
```bash
# DEV
cd /opt/bot-dev && python3 services/parser_rclick.py

# PROD
cd /opt/bot && /opt/bot/venv/bin/python3 services/parser_rclick.py
```

**Cron (автоматически):**
- DEV: 6:00 ежедневно
- PROD: 3:00 ежедневно

**Проверка после парсинга:**
```bash
sqlite3 /opt/bot-dev/properties.db "SELECT COUNT(*) FROM units;"
sqlite3 /opt/bot-dev/properties.db "SELECT code, price_rub FROM units ORDER BY id DESC LIMIT 5;"
```

---

### ЗАДАЧА 4: Закрыть/открыть лот из доступа

**Вариант A: Через статус в БД**
```bash
# Закрыть лот
sqlite3 /opt/bot-dev/properties.db "UPDATE units SET status='sold' WHERE code='В708';"

# Открыть лот
sqlite3 /opt/bot-dev/properties.db "UPDATE units SET status='available' WHERE code='В708';"

# Проверить
sqlite3 /opt/bot-dev/properties.db "SELECT code, status FROM units WHERE code='В708';"
```

**Вариант B: Удалить из БД**
```bash
# Удалить
sqlite3 /opt/bot-dev/properties.db "DELETE FROM units WHERE code='В708';"
```

⚠️ **Внимание:** При следующем парсинге удалённый лот вернётся!

**Вариант C: Добавить в исключения парсера**

Редактировать `/opt/bot-dev/services/parser_rclick.py`, добавить фильтр:
```python
EXCLUDED_CODES = ['В708', 'А101']

# В функции fetch_all_units() после парсинга:
units = [u for u in units if u.get('code') not in EXCLUDED_CODES]
```

---

### ЗАДАЧА 5: Изменить дизайн PDF КП

**Файл:** `/opt/bot-dev/services/kp_pdf_generator.py`

**Основные функции:**
- `generate_kp_pdf()` — главная функция
- `_create_header()` — шапка с логотипом
- `_create_lot_info()` — блок информации о лоте
- `_create_installment_table()` — таблица рассрочки
- `_create_footer()` — подвал

**Стили:**
```python
# Цвета
PRIMARY_COLOR = "#1a365d"
ACCENT_COLOR = "#c9a227"

# Шрифты
TITLE_FONT_SIZE = 24
BODY_FONT_SIZE = 11
```

**Тестирование:**
```bash
cd /opt/bot-dev && source venv/bin/activate
python3 -c "
from services.kp_pdf_generator import generate_kp_pdf
path = generate_kp_pdf(code='В101', include_18m=True, output_dir='/tmp')
print(f'PDF создан: {path}')
"
# Скачать и посмотреть: scp -P 2222 root@72.56.64.91:/tmp/KP_*.pdf .
```

---

### ЗАДАЧА 6: Изменить расчёты ROI

**Файлы:**
- `/opt/bot-dev/services/investment_calc.py` — основные расчёты
- `/opt/bot-dev/handlers/calc_dynamic.py` — UI обработчики

**Ключевые параметры в `investment_calc.py`:**
```python
# Доходность
ANNUAL_YIELD = 0.12  # 12% годовых
OCCUPANCY_RATE = 0.75  # 75% заполняемость

# Расходы
MANAGEMENT_FEE = 0.20  # 20% УК
TAX_RATE = 0.06  # 6% налог
```

**Формула ROI:**
```python
annual_income = price * ANNUAL_YIELD * OCCUPANCY_RATE
net_income = annual_income * (1 - MANAGEMENT_FEE) * (1 - TAX_RATE)
roi_years = price / net_income
```

---

### ЗАДАЧА 7: Добавить/убрать кнопку в меню

**Файл:** `/opt/bot-dev/config/settings.py`

**Главное меню:**
```python
MAIN_MENU_BUTTONS = [
    ["🏠 О проекте", "📊 Расчёты"],
    ["📋 Коммерческое предложение", "🎬 Медиа"],
    ["📅 Записаться на показ", "📞 Связаться"],
]
```

**Inline кнопки в хендлерах:**
```python
# handlers/kp.py
keyboard = [
    [{"text": "📄 КП без рассрочки", "callback_data": f"kp_no_inst_{code}"}],
    [{"text": "📄 КП с рассрочкой 12 мес", "callback_data": f"kp_12m_{code}"}],
    # Добавить/убрать строки здесь
]
```

---

## 🚀 ДЕПЛОЙ DEV → PROD

### Чеклист

```bash
# 1. Тест в DEV
systemctl restart rizalta-bot-dev
# Проверить в @rizaltatestdevop_bot

# 2. Коммит DEV
cd /opt/bot-dev
git add -A && git commit -m "v2.4.x: описание" && git push

# 3. Копировать файлы
cp /opt/bot-dev/ФАЙЛ /opt/bot/ФАЙЛ

# 4. Проверить синтаксис
cd /opt/bot && python3 -c "import app; print('OK')"

# 5. Перезапустить PROD
systemctl restart rizalta-bot

# 6. Проверить логи
journalctl -u rizalta-bot -f

# 7. Тест в PROD
# Проверить в @RealtMeAI_bot

# 8. Коммит PROD
cd /opt/bot
git add -A && git commit -m "v2.4.x: описание" && git push
```

### ⚠️ ВАЖНО: Mini App URL

После копирования `app.py` проверить URL:
```bash
# PROD должен быть БЕЗ ?env=dev
grep "rizalta-miniapp" /opt/bot/app.py
# Должно быть: https://rizalta-miniapp.vercel.app

# Если есть ?env=dev — исправить:
sed -i 's|https://rizalta-miniapp.vercel.app?env=dev|https://rizalta-miniapp.vercel.app|' /opt/bot/app.py
```

---

## 🐛 ЧАСТЫЕ ОШИБКИ И РЕШЕНИЯ

### ImportError: cannot import name 'handle_xxx'
**Причина:** Не скопирован `handlers/__init__.py`
**Решение:** `cp /opt/bot-dev/handlers/__init__.py /opt/bot/handlers/`

### ModuleNotFoundError: No module named 'xxx'
**Причина:** Неправильный venv
**Решение:** `source /opt/bot-dev/venv/bin/activate`

### TypeError: unexpected keyword argument
**Причина:** Параметр переименован, но не везде обновлён
**Решение:** Поиск и замена во всех файлах:
```bash
grep -r "старый_параметр" /opt/bot-dev --include="*.py"
sed -i 's/старый_параметр/новый_параметр/g' /opt/bot-dev/**/*.py
```

### PDF не генерируется
**Проверить:**
```bash
cd /opt/bot-dev && source venv/bin/activate
python3 -c "from services.kp_pdf_generator import generate_kp_pdf; generate_kp_pdf('В101')"
```

### Парсер не обновляет данные
**Проверить лог:**
```bash
tail -50 /var/log/rizalta_parser.log
```
**Запустить вручную:**
```bash
cd /opt/bot-dev && python3 services/parser_rclick.py
```

---

## 📊 МОНИТОРИНГ

### Логи
```bash
# DEV
journalctl -u rizalta-bot-dev -f
journalctl -u rizalta-bot-dev -f | grep -E "ERROR|WARN"

# PROD
journalctl -u rizalta-bot -f

# Парсер
tail -f /var/log/rizalta_parser.log
```

### Статус сервисов
```bash
systemctl status rizalta-bot-dev
systemctl status rizalta-bot
systemctl status cloudflare-rizalta
```

### БД статистика
```bash
sqlite3 /opt/bot-dev/properties.db "
SELECT 
    COUNT(*) as total,
    MIN(price_rub) as min_price,
    MAX(price_rub) as max_price
FROM units;
"
```

---

## 📚 ДОПОЛНИТЕЛЬНАЯ ДОКУМЕНТАЦИЯ

На сервере:
- `/opt/bot-dev/docs/RIZALTA_CONTEXT.md` — контекст проекта
- `/opt/bot-dev/docs/RIZALTA_CURRENT.md` — текущий статус
- `/opt/bot-dev/docs/RIZALTA_ARCHITECTURE.md` — архитектура
- `/opt/bot-dev/docs/RIZALTA_KNOWLEDGE.md` — база знаний
- `/opt/bot-dev/docs/RIZALTA_TASKS.md` — бэклог

---

## 🔄 ОБНОВЛЕНИЕ ЭТОГО ФАЙЛА

При решении новой задачи — добавь её в раздел "ТИПОВЫЕ ЗАДАЧИ":

```markdown
### ЗАДАЧА N: Краткое описание

**Файлы:** какие файлы затронуты

**Шаги:**
1. ...
2. ...

**Команды:**
```bash
# команды
```

**Проверка:**
```bash
# как проверить что всё работает
```
```

---

*Последнее обновление: 16.01.2026*
*Версия контекста: 1.0.0*
