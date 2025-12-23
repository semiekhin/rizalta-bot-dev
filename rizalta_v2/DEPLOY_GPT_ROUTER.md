# RIZALTA Bot v2.0 — GPT Intent Router

## Что изменилось

### Было (v1.9.x):
```
Сообщение → Regex паттерны → Режим секретаря → AI fallback
                  ↓
         Перехват не тех команд
```

### Стало (v2.0):
```
Сообщение → GPT Intent Router → Handler
                  ↓
         Единая точка классификации
```

## Преимущества

1. **Голос работает везде** — не важно в каком меню, GPT поймёт
2. **Нет режима секретаря** — не нужно входить/выходить
3. **Умная классификация** — "открой шахматку" ≠ задача
4. **Исправление ошибок Whisper** — "напомню" = "напомни"

---

## Файлы для деплоя

```
/opt/bot-dev/
├── services/
│   ├── intent_router.py      ← НОВЫЙ (метазнания + классификатор)
│   ├── secretary_db.py       ← ОБНОВИТЬ (убрать режим)
│   └── secretary_ai.py       ← БЕЗ ИЗМЕНЕНИЙ
├── handlers/
│   └── secretary.py          ← ОБНОВИТЬ (убрать режим)
└── app.py                    ← ЗАМЕНИТЬ (новый роутер)
```

---

## Команды деплоя

### 1. Подключиться к серверу
```bash
ssh -p 2222 root@72.56.64.91
cd /opt/bot-dev
```

### 2. Бэкап текущей версии
```bash
cp app.py app.py.backup
cp services/secretary_db.py services/secretary_db.py.backup
cp handlers/secretary.py handlers/secretary.py.backup
```

### 3. Загрузить новые файлы
```bash
# Вариант 1: через SCP с локальной машины
scp -P 2222 intent_router.py root@72.56.64.91:/opt/bot-dev/services/
scp -P 2222 app_v2.py root@72.56.64.91:/opt/bot-dev/app.py
scp -P 2222 secretary_v2.py root@72.56.64.91:/opt/bot-dev/handlers/secretary.py
scp -P 2222 secretary_db_v2.py root@72.56.64.91:/opt/bot-dev/services/secretary_db.py

# Вариант 2: через cat << 'EOF' на сервере
# (скопировать содержимое файлов)
```

### 4. Перезапуск и проверка
```bash
systemctl restart rizalta-bot-dev
journalctl -u rizalta-bot-dev -f
```

### 5. Тестирование
В Telegram (@rizaltatestdevop_bot):
```
✅ "открой шахматку" → шахматка (не задача!)
✅ "скинь презентацию" → презентация
✅ "завтра позвонить Иванову в 10" → создаёт задачу
✅ "что на сегодня" → расписание
✅ Голосом из любого меню: "напомни отправить КП" → задача
```

### 6. Деплой в prod (после тестов)
```bash
# Копируем из dev в prod
cp /opt/bot-dev/app.py /opt/bot/
cp /opt/bot-dev/services/intent_router.py /opt/bot/services/
cp /opt/bot-dev/services/secretary_db.py /opt/bot/services/
cp /opt/bot-dev/handlers/secretary.py /opt/bot/handlers/

# Перезапуск prod
systemctl restart rizalta-bot
journalctl -u rizalta-bot -f
```

---

## Откат при проблемах

```bash
cd /opt/bot-dev
cp app.py.backup app.py
cp services/secretary_db.py.backup services/secretary_db.py
cp handlers/secretary.py.backup handlers/secretary.py
systemctl restart rizalta-bot-dev
```

---

## Метазнания в intent_router.py

GPT знает о боте:
- Все 15+ intent'ов (КП, расчёты, фиксация, секретарь, новости...)
- Триггеры для каждой функции
- Правила приоритета (action > task)
- Исправление ошибок Whisper
- Извлечение параметров (площадь, бюджет, дата, время)

---

## Расход токенов

| Тип запроса | Токены |
|------------|--------|
| Кнопка меню | 0 (quick match) |
| Голос/текст | ~300-500 |
| Создание задачи | ~400 |

При 100 сообщениях/день ≈ 40-50k токенов ≈ $0.01

---

## Логи для отладки

```bash
# Смотреть intent classification
journalctl -u rizalta-bot-dev -f | grep "\[INTENT\]"

# Смотреть роутинг
journalctl -u rizalta-bot-dev -f | grep "\[ROUTER\]"
```

---

## Что НЕ менялось

- callbacks (process_callback) — без изменений
- Все handlers/* кроме secretary.py — без изменений
- Все services/* кроме secretary_db.py — без изменений
- База данных — без изменений
- .env — без изменений
