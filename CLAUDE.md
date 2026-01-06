# RIZALTA — Quick Start для Claude

## Версия: 2.2.0 (06.01.2026)

## SSH
```bash
ssh -p 2222 root@72.56.64.91
```

## Структура
```
/opt/bot/        — PROD (НЕ ТРОГАТЬ без согласования!)
/opt/bot-dev/    — DEV (тут работаем)
/opt/miniapp/    — Mini App (React)
```

## Репозитории
- PROD: github.com/semiekhin/rizalta-bot
- DEV: github.com/semiekhin/rizalta-bot-dev  
- Mini App: github.com/semiekhin/rizalta-miniapp

## Сервисы (systemd)
```bash
# PROD — НЕ ТРОГАТЬ!
rizalta-bot.service          # uvicorn :8000 (webhook)
cloudflare-rizalta.service   # туннель PROD

# DEV — можно перезапускать
rizalta-bot-dev.service      # polling (Telegram)
rizalta-dev-api.service      # uvicorn :8002 (API Mini App)
rizalta-dev-tunnel.service   # туннель DEV + auto vercel.json
```

## Порты
- :8000 — PROD (webhook)
- :8002 — DEV API (Mini App)

## Mini App
- URL: https://rizalta-miniapp.vercel.app
- API: /api/lots, /api/miniapp-action
- Деплой: `cd /opt/miniapp && vercel --prod`

## Частые команды
```bash
# Статус
systemctl status rizalta-bot         # PROD
systemctl status rizalta-dev-api     # DEV API

# Логи
journalctl -u rizalta-dev-api -f

# Git
cd /opt/bot-dev && git add -A && git commit -m "msg" && git push
cd /opt/miniapp && git add -A && git commit -m "msg" && git push
```

## ⚠️ ВАЖНО
1. PROD работает коммерчески — изменения только после теста в DEV
2. При смене туннеля DEV — vercel.json обновляется автоматически
3. Документация: PROJECT.md, RIZALTA_PROJECT.md
