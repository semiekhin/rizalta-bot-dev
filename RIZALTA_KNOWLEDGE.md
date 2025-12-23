# RIZALTA_KNOWLEDGE.md

## 🧠 Важные нюансы проекта

### Архитектура GPT Intent Router (v2.0)

**Как работает:**
```
Сообщение (голос/текст) → GPT Intent Router → Handler
```

**Где живёт:**
- `services/intent_router.py` — метазнания + классификатор
- Функция `classify_intent(text)` → `{"intent": str, "params": dict, "confidence": float}`

**15+ intent'ов:**
- `get_kp`, `calculate_roi`, `show_installment`, `compare_deposit`
- `open_fixation`, `open_shahmatka`, `book_showing`
- `send_documents`, `send_presentation`, `show_media`
- `create_task`, `show_schedule` (секретарь)
- `show_news`, `chat`, `main_menu`

**Правила приоритета:**
- "открой шахматку" → `open_shahmatka` (НЕ `create_task`!)
- "завтра позвонить Иванову" → `create_task`
- "напомню" (ошибка Whisper) → "напомни" → `create_task`

### AI-Секретарь

**Файлы:**
- `handlers/secretary.py` — UI, навигация, callback'и
- `services/secretary_ai.py` — GPT парсинг задач
- `services/secretary_db.py` — SQLite операции

**База данных:**
```
Dev:  /opt/bot-dev/secretary.db
Prod: /opt/bot/secretary.db
```

**Таблица tasks:**
```sql
id, user_id, task_text, due_date, due_time, client_name,
priority, status, description, reminder_sent, created_at, completed_at
```

**⚠️ Напоминания НЕ работают** — нужен APScheduler

### Рассрочка (v2.0.1)

**Текущие проценты (dev):**
| ПВ | Удорожание | Срок |
|----|------------|------|
| 30% | +9% | 18 мес |
| 40% | +7% | 18 мес |
| 50% | +4% | 18 мес |

**Старые проценты (prod):**
| ПВ | Удорожание | Срок |
|----|------------|------|
| 30% | +12% | 24 мес |
| 40% | +9% | 24 мес |
| 50% | +6% | 24 мес |

**Файлы расчётов:**
- `services/kp_pdf_generator.py` — PDF генерация КП
- `services/calc_universal.py` — расчёты для UI "Расчёты"→"Рассрочка"
- `services/calculations.py` — общие финансовые расчёты

### Два репозитория

| Репо | Путь | Бот | Режим |
|------|------|-----|-------|
| rizalta-bot-dev | /opt/bot-dev | @rizaltatestdevop_bot | polling |
| rizalta-bot | /opt/bot | @RealtMeAI_bot | webhook |

**Правило:** Всегда тестируем в dev, потом деплоим в prod.

---

## 🔧 Частые команды

### Сервер
```bash
ssh -p 2222 root@72.56.64.91
```

### Dev
```bash
cd /opt/bot-dev
source venv/bin/activate
systemctl restart rizalta-bot-dev
journalctl -u rizalta-bot-dev -f
journalctl -u rizalta-bot-dev -f | grep -E "\[INTENT\]|\[ROUTER\]"
```

### Prod
```bash
cd /opt/bot
source venv/bin/activate
systemctl restart rizalta-bot
journalctl -u rizalta-bot -f
```

### Git
```bash
cd /opt/bot-dev
git add -A && git commit -m "vX.X.X: описание" && git push

cd /opt/bot
git add -A && git commit -m "vX.X.X: описание" && git push
```

### Тест КП
```bash
cd /opt/bot-dev
source venv/bin/activate
python3 -c "from services.kp_pdf_generator import generate_kp_pdf; print(generate_kp_pdf(code='В101', include_18m=True, output_dir='/tmp'))"
```

### SQLite секретарь
```bash
sqlite3 /opt/bot/secretary.db "SELECT * FROM tasks ORDER BY id DESC LIMIT 5;"
```

---

## 🐛 Решённые проблемы

### 1. Голос создавал задачу вместо действия
**Проблема:** "открой шахматку" → создавалась задача
**Причина:** Режим секретаря перехватывал все сообщения
**Решение:** GPT Intent Router с правилами приоритета

### 2. ImportError при деплое в prod
**Проблема:** `cannot import name 'handle_secretary_menu'`
**Причина:** Не скопирован `handlers/__init__.py`
**Решение:** Копировать ВСЕ изменённые файлы

### 3. TypeError: unexpected keyword argument 'include_24m'
**Проблема:** Параметр переименован, но handlers не обновлены
**Причина:** Частичное обновление файлов
**Решение:** 
```bash
sed -i 's/include_24m/include_18m/g' handlers/kp.py handlers/domoplaner.py app.py
```

### 4. ModuleNotFoundError: No module named 'requests'
**Проблема:** Неправильный venv активирован
**Решение:** `source /opt/bot-dev/venv/bin/activate`

---

## 📋 Чеклист деплоя

1. [ ] Тест в dev (@rizaltatestdevop_bot)
2. [ ] `git add -A && git commit && git push` (dev)
3. [ ] Копировать файлы в /opt/bot
4. [ ] `systemctl restart rizalta-bot`
5. [ ] Проверить логи: `journalctl -u rizalta-bot -f`
6. [ ] Тест в prod (@RealtMeAI_bot)
7. [ ] `git add -A && git commit && git push` (prod)

---

## 🔮 Архитектурные решения

### Почему GPT вместо regex
- Regex не справлялся с естественным языком
- Голосовые команды содержат ошибки Whisper
- Режим секретаря создавал конфликты
- GPT понимает контекст и намерение

### Почему SQLite для секретаря
- Простота, достаточно для текущей нагрузки
- Отдельная база от properties.db
- Легко бэкапить

### Почему два репозитория
- Безопасность: prod никогда не ломается экспериментами
- Разные токены ботов
- Разные режимы (webhook vs polling)
