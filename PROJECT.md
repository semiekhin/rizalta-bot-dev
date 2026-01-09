# ⚠️⚠️⚠️ КРИТИЧЕСКИ ВАЖНО ⚠️⚠️⚠️
# PROD НЕ ТРОГАТЬ! РАБОТАТЬ ТОЛЬКО В DEV!
# PROD (/opt/bot) — ТОЛЬКО ДЛЯ ДЕПЛОЯ ПОСЛЕ ТЕСТИРОВАНИЯ И СОГЛАСОВАНИЯ!
# ВСЕ ИЗМЕНЕНИЯ СНАЧАЛА В /opt/bot-dev → ТЕСТИРОВАНИЕ → ПОТОМ В PROD

---

# RIZALTA Bot DEV — Документация

## Версия: 2.3.0

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

## Что нового в v2.3.0 (06.01.2026)
- **Mini App полностью работает!** — шахматка лотов на Vercel
- **Разделение PROD/DEV** — через параметр `?env=dev` и Vercel proxy
- **Обход блокировок РФ** — запросы идут через Vercel, не напрямую на trycloudflare

## Архитектура Mini App
```
┌─────────────────────────────────────────────────────────────┐
│                     MINI APP (Vercel)                        │
│              https://rizalta-miniapp.vercel.app              │
│                                                              │
│  ?env=dev  → /api-dev/* → DEV туннель → :8002               │
│  (default) → /api/*     → PROD туннель → :8000              │
└─────────────────────────────────────────────────────────────┘

vercel.json:
- /api/*     → enrolled-chapter-clouds-fold.trycloudflare.com (PROD)
- /api-dev/* → provide-resident-retain-employees.trycloudflare.com (DEV)
```

## Сервисы
```
PROD:
├── rizalta-bot.service (uvicorn :8000, webhook)
└── cloudflare-rizalta.service (туннель PROD)

DEV:
├── rizalta-bot-dev.service (polling)
├── rizalta-dev-api.service (uvicorn :8002)
└── rizalta-dev-tunnel.service (туннель DEV)
```

## Команды
```bash
# Статус
systemctl status rizalta-bot          # PROD
systemctl status rizalta-bot-dev      # DEV polling
systemctl status rizalta-dev-api      # DEV API

# Логи
journalctl -u rizalta-bot -f          # PROD
journalctl -u rizalta-dev-api -f      # DEV API

# Деплой Mini App
cd /opt/miniapp && npm run build && vercel --prod
```

## Важно: туннели
При смене URL туннеля нужно обновить vercel.json:
```bash
cat /opt/miniapp/vercel.json
# Изменить URL и редеплоить:
cd /opt/miniapp && vercel --prod
```

## История версий
- **v2.3.0** (06.01.2026) — Mini App работает, разделение PROD/DEV
- **v2.2.0** (06.01.2026) — Mini App интеграция, systemd сервисы DEV
- **v2.1.2** (29.12.2025) — Групповые заявки на показ
