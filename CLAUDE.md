# RIZALTA Bot - Quick Start для Claude

## Подключение к серверу
```bash
ssh -p 2222 root@72.56.64.91
```

## Структура
- **PROD:** /opt/bot (@RealtMeAI_bot) - webhook через uvicorn
- **DEV:** /opt/bot-dev (@rizaltatestdevop_bot) - polling

## Версия: 2.1.1

## Ключевые файлы
- `app.py` - главный файл, GPT Intent Router
- `run_polling.py` - DEV режим polling
- `handlers/kp.py` - КП, навигация, пагинация
- `handlers/secretary.py` - AI-секретарь с timezone
- `services/monitoring.py` - мониторинг нагрузки
- `services/secretary_db.py` - БД секретаря + timezone

## Базы данных (SQLite)
- `properties.db` - 348 лотов
- `secretary.db` - задачи + users (timezone)
- `monitoring.db` - статистика запросов

## Команды
```bash
# DEV
systemctl restart rizalta-bot-dev
journalctl -u rizalta-bot-dev -f

# PROD  
systemctl restart rizalta-bot
journalctl -u rizalta-bot -f
```

## Деплой
1. Изменения в DEV
2. Тест в DEV боте
3. Копирование в PROD
4. `sed -i 's|bot-dev|bot|g'` для путей
5. Рестарт + коммит оба репо

## Мониторинг
- Алерт >30 req/min
- Алерт RAM >50%
- Ежедневный отчёт 20:00

## TODO
- [ ] Кеширование GPT ответов для масштабирования
- [ ] Redis при >500 активных users
- [ ] PostgreSQL при >2000 users
