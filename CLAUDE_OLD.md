# RIZALTA AI Bot — Правила для Claude Code

## ⚠️ КРИТИЧЕСКИ ВАЖНО
- **PROD (`/opt/bot`) — НЕ ТРОГАТЬ.** Никогда не редактировать, не копировать в, не рестартовать.
- **Работаем ТОЛЬКО в `/opt/bot-dev`**
- Перед началом любой задачи — `git status` + `git pull`
- После завершения — `git add -A && git commit && git push`

## Проект
- **Что это:** Telegram-бот AI-консультант для риэлторов. Инвестиционная недвижимость RIZALTA Resort Belokurikha (Алтай)
- **Версия:** 2.7.2
- **DEV бот:** @rizaltatestdevop_bot (polling через run_polling.py)
- **PROD бот:** @RealtMeAI_bot (webhook :8000) — НЕ ТРОГАТЬ

## Инфраструктура
- **Сервер:** Timeweb, 4 vCPU, 8 GB RAM
- **DEV:** `/opt/bot-dev` (этот проект)
- **PROD:** `/opt/bot` (READ-ONLY для нас)
- **WebApp DEV:** `/opt/webapp-dev` (отдельный проект, не трогать)
- **WebApp PROD:** `/opt/webapp` (отдельный проект, не трогать)

## Сервисы (systemd)
- `rizalta-bot-dev` — DEV бот (polling) — можно рестартовать
- `rizalta-dev-api` — DEV API (uvicorn :8002) — можно рестартовать
- `rizalta-bot` — PROD бот — **НЕ ТРОГАТЬ**
- `rizalta-watchdog` — мониторинг — не трогать

## Рестарт DEV
```bash
systemctl restart rizalta-bot-dev
# Если менялся API:
systemctl restart rizalta-dev-api
```

## База данных
- `data/properties.db` — SQLite WAL, лоты К1+К2+К3 (парсер cron обновляет)
- `data/corp3_access.db` — whitelist К3
- `data/corp3_units.json` — старая база К3 (в .gitignore)
- `data/hidden_buildings.json` — скрытые корпуса {"hidden": [2]}

## Корпуса
- **К1 «Family»:** ~256 лотов (building=1)
- **К2 «Business»:** ~104 лота (building=2), скрыт
- **К3 «Digital»:** ~116 available (building=3) — штатный режим

## Структура кода
```
app.py              — webhook + API + callback router (PROD)
run_polling.py      — DEV polling
config/settings.py  — настройки, токены, пути
handlers/           — обработчики команд и callback
services/           — бизнес-логика, PDF, расчёты, БД
data/               — базы данных, конфиги
```

## Ключевые файлы
- `handlers/kp.py` — КП: навигация по лотам, генерация PDF
- `services/kp_pdf_generator.py` — генерация КП PDF (HTML→wkhtmltopdf)
- `services/units_db.py` — работа с БД лотов (SQLite)
- `services/calc_universal.py` — расчёт ROI и рассрочки
- `handlers/booking_calendar.py` — календарь бронирования
- `services/tranche_mortgage_calculator.py` — траншевая ипотека

## Документация
- `docs/RIZALTA_CURRENT.md` — текущий статус, что сделано
- `docs/RIZALTA_ARCHITECTURE.md` — карта проекта для LLM
- `docs/RIZALTA_KNOWLEDGE.md` — бизнес-логика, формулы
- `docs/RIZALTA_TASKS.md` — задачи и бэклог
- `docs/RIZALTA_CALLBACKS.md` — индекс ~120 callback паттернов

## Деплой DEV→PROD
- **app.py НЕ копировать целиком** (hardcoded пути /opt/bot-dev/)
- app.py править точечно в PROD
- Деплой делает ЧЕЛОВЕК, не Claude Code
- После деплоя: `grep -rn "/opt/bot-dev" /opt/bot/ --include="*.py"` — должно быть пусто

## Парсер (cron)
- DEV 06:00, PROD 03:00
- `services/parser_rclick.py` — DELETE + INSERT для К1+К2+К3
- Если корпус убран с сайта — пропадёт из БД

## Ограничения Telegram
- Callback data: max 64 байта → кодирование area10 = int(area_m2 * 10)
- Inline buttons: max 100 кнопок → пагинация (PAGE_SIZE=50, MAX_BUTTONS=20)

## Git workflow
1. `git pull` перед работой
2. Атомарные коммиты с описанием на русском
3. `git push` после каждого логического блока
4. Docs обновлять при любых изменениях архитектуры
