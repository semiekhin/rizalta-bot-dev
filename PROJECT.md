# RIZALTA Bot DEV — Документация

## Версия: 2.1.2

## Быстрый старт
```bash
ssh -p 2222 root@72.56.64.91
cd /opt/bot-dev
source venv/bin/activate
```

## Структура
- `/opt/bot` — PROD (@RealtMeAI_bot, webhook)
- `/opt/bot-dev` — DEV (@rizaltatestdevop_bot, polling)

## Что нового в v2.1.2 (29.12.2025)
- **Групповые заявки на показ** — кнопка "🙋 Взять заявку" в группе
- **Интеграция с секретарём** — автоматическое создание задачи при взятии заявки
- **Редактирование сообщений** — edit_message_inline() для обновления статуса
- **Стратегия Mini App** — RealtMy будет Telegram Mini App вместо native

## Глобальная задача
**Постепенный переход на Mini App архитектуру:**
1. Шахматка (визуальный выбор лотов) — прототип готов
2. RealtMy (управление контентом) — планируется

## Изменения v2.1.2
### Файлы:
- `app.py` — callback `book_take_`
- `services/telegram.py` — send_message_inline_return_id, edit_message_inline
- `handlers/booking_calendar.py` — handle_take_booking

### БД (properties.db):
```sql
ALTER TABLE bookings ADD COLUMN taken_by_id INTEGER;
ALTER TABLE bookings ADD COLUMN taken_by_name TEXT;
ALTER TABLE bookings ADD COLUMN group_message_id INTEGER;
```

## Предыдущие версии

### v2.1.1 (24.12.2025)
- Мониторинг нагрузки (services/monitoring.py)
- 11 часовых поясов для секретаря
- Напоминания через asyncio task

### v2.1.0 (24.12.2025)
- 348 лотов вместо 69
- Универсальная навигация Корпус → Этаж → Лоты
- Пагинация "Показать ещё N лотов"
- Обработка 70 дублей кодов
- Поиск по бюджету ±10%

### v1.9.6 (19.12.2025)
- Новый дизайн КП при 100% оплате
- 6 презентаций проекта
- 9 видео про Алтай

## Команды
```bash
# Запуск DEV бота
python run_polling.py

# Проверка синтаксиса
python3 -c "import app; print('OK')"

# Логи
journalctl -u rizalta-bot-dev -f

# Перезапуск
systemctl restart rizalta-bot-dev
```

## Деплой в PROD
```bash
# 1. Тест в DEV
# 2. Копирование
cp /opt/bot-dev/file.py /opt/bot/
sed -i 's|/opt/bot-dev|/opt/bot|g' /opt/bot/file.py

# 3. Рестарт PROD
cd /opt/bot
python3 -c "import app; print('OK')"
systemctl restart rizalta-bot

# 4. Коммит обоих репо
cd /opt/bot-dev && git add -A && git commit -m "v2.1.2" && git push
cd /opt/bot && git add -A && git commit -m "v2.1.2" && git push
```

## TODO
- [ ] Mini App шахматка (API + React + Vercel)
- [ ] Mini App RealtMy (контент-менеджмент)
- [ ] Детальное логирование callback'ов
- [ ] Кеширование GPT (Redis)
- [ ] PostgreSQL при >2000 users

## Ссылки
- **Prod repo:** https://github.com/semiekhin/rizalta-bot
- **Dev repo:** https://github.com/semiekhin/rizalta-bot-dev
- **Сервер:** ssh -p 2222 root@72.56.64.91
