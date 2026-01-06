#!/bin/bash
# Автообновление vercel.json при смене URL туннеля DEV

sleep 15

# Получаем новый URL туннеля
TUNNEL_URL=$(journalctl -u rizalta-dev-tunnel --no-pager -n 50 2>/dev/null | grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' | tail -1)

if [ -z "$TUNNEL_URL" ]; then
    echo "❌ Не удалось получить URL туннеля"
    exit 1
fi

echo "🔗 Новый DEV туннель: $TUNNEL_URL"

# Обновляем vercel.json
cat > /opt/miniapp/vercel.json << VERCEL
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "${TUNNEL_URL}/api/:path*"
    }
  ]
}
VERCEL

echo "✅ vercel.json обновлён"

# Редеплой Vercel (если установлен)
if command -v vercel &> /dev/null; then
    cd /opt/miniapp && vercel --prod --yes 2>/dev/null && echo "✅ Vercel redeploy done"
fi
