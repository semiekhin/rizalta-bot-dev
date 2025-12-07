#!/bin/bash
# Ждём пока туннель запустится и обновляем webhook

sleep 10

# Получаем новый URL туннеля
TUNNEL_URL=$(journalctl -u cloudflare-rizalta --no-pager -n 50 | grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' | tail -1)

if [ -z "$TUNNEL_URL" ]; then
    echo "❌ Не удалось получить URL туннеля"
    exit 1
fi

echo "🔗 Новый URL: $TUNNEL_URL"

# Загружаем токен
source /opt/bot/.env

# Обновляем webhook
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook?url=${TUNNEL_URL}/telegram/webhook"

echo ""
echo "✅ Webhook обновлён!"
