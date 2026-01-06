# RIZALTA Bot DEV — Документация

## Версия: 2.2.0

## Быстрый старт
```bash
ssh -p 2222 root@72.56.64.91
cd /opt/bot-dev
source venv/bin/activate
```

## Структура
- `/opt/bot` — PROD (@RealtMeAI_bot, webhook :8000)
- `/opt/bot-dev` — DEV (@rizaltatestdevop_bot, polling)
- `/opt/miniapp` — Mini App (React, Vercel)

## Репозитории
- **PROD:** https://github.com/semiekhin/rizalta-bot
- **DEV:** https://github.com/semiekhin/rizalta-bot-dev
- **Mini App:** https://github.com/semiekhin/rizalta-miniapp

## Что нового в v2.2.0 (06.01.2026)
- **Mini App интеграция** — шахматка лотов на Vercel
- **API для Mini App** — /api/lots, /api/miniapp-action
- **CORS middleware** — кросс-доменные запросы
- **Кнопка "🏢 Лоты"** — открывает Mini App
- **Systemd сервисы DEV:**
  - `rizalta-dev-api.service` — uvicorn :8002
  - `rizalta-dev-tunnel.service` — cloudflared + автообновление vercel.json
- **Скрипт update_vercel_tunnel.sh** — автообновление при смене URL туннеля

## Архитектура
```
PROD :8000
├── rizalta-bot.service (uvicorn, webhook)
└── cloudflare-rizalta.service (туннель)

DEV :8002
├── rizalta-bot-dev.service (polling)
├── rizalta-dev-api.service (uvicorn, API для Mini App)
└── rizalta-dev-tunnel.service (туннель + auto vercel.json)

Mini App
├── https://rizalta-miniapp.vercel.app (статика)
└── API проксируется через Vercel → DEV туннель
```

## Mini App
- **URL:** https://rizalta-miniapp.vercel.app
- **Стек:** React + Vite + Tailwind CSS
- **Функции:** визуальный выбор 348 лотов, фильтры
- **Деплой:** `cd /opt/miniapp && vercel --prod`

## Команды
```bash
# Статус сервисов
systemctl status rizalta-bot          # PROD
systemctl status rizalta-bot-dev      # DEV polling
systemctl status rizalta-dev-api      # DEV API
systemctl status rizalta-dev-tunnel   # DEV туннель

# Логи
journalctl -u rizalta-bot -f          # PROD
journalctl -u rizalta-dev-api -f      # DEV API
journalctl -u rizalta-dev-tunnel -f   # DEV туннель

# Перезапуск
systemctl restart rizalta-bot         # PROD
systemctl restart rizalta-dev-api rizalta-dev-tunnel  # DEV
```

## Предыдущие версии

### v2.1.2 (29.12.2025)
- Групповые заявки на показ с кнопкой "Взять"
- Интеграция заявок с AI-секретарём

### v2.1.1 (24.12.2025)
- Мониторинг нагрузки
- 11 часовых поясов для секретаря

### v2.1.0 (24.12.2025)
- 348 лотов, универсальная навигация
- Пагинация, GPT Intent Router

## TODO
- [ ] Named Tunnel или свой домен для PROD (надёжность)
- [ ] Деплой Mini App в PROD
- [ ] Self-healing мониторинг
- [ ] RealtMy Mini App (контент-менеджмент)
