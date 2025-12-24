"""
Мониторинг нагрузки бота.
"""

import asyncio
import aiohttp
import psutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque
import os

# Настройки
ADMIN_CHAT_ID = 512319063
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DB_PATH = Path("/opt/bot-dev/monitoring.db")

# Счётчик запросов (последние 60 секунд)
request_times = deque(maxlen=1000)

# Пороги
REQUESTS_PER_MIN_THRESHOLD = 30
RAM_THRESHOLD_PERCENT = 50


def init_db():
    """Создаёт таблицу статистики."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_id INTEGER,
            request_type TEXT,
            response_time_ms INTEGER
        )
    """)
    conn.commit()
    conn.close()


def log_request(user_id: int, request_type: str = "message", response_time_ms: int = 0):
    """Логирует запрос."""
    now = datetime.now()
    request_times.append(now)
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO stats (timestamp, user_id, request_type, response_time_ms) VALUES (?, ?, ?, ?)",
        (now.isoformat(), user_id, request_type, response_time_ms)
    )
    conn.commit()
    conn.close()


def get_requests_per_minute() -> int:
    """Возвращает количество запросов за последнюю минуту."""
    now = datetime.now()
    minute_ago = now - timedelta(minutes=1)
    return sum(1 for t in request_times if t > minute_ago)


def get_ram_usage() -> float:
    """Возвращает использование RAM в процентах."""
    return psutil.virtual_memory().percent


def get_daily_stats() -> dict:
    """Статистика за сегодня."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Всего запросов
    cursor.execute(
        "SELECT COUNT(*) FROM stats WHERE timestamp LIKE ?",
        (f"{today}%",)
    )
    total_requests = cursor.fetchone()[0]
    
    # Уникальных пользователей
    cursor.execute(
        "SELECT COUNT(DISTINCT user_id) FROM stats WHERE timestamp LIKE ?",
        (f"{today}%",)
    )
    unique_users = cursor.fetchone()[0]
    
    # Среднее время ответа
    cursor.execute(
        "SELECT AVG(response_time_ms) FROM stats WHERE timestamp LIKE ? AND response_time_ms > 0",
        (f"{today}%",)
    )
    avg_response = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "total_requests": total_requests,
        "unique_users": unique_users,
        "avg_response_ms": int(avg_response)
    }


async def send_alert(message: str):
    """Отправляет алерт админу."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                return await resp.json()
    except Exception as e:
        print(f"[MONITOR] Alert error: {e}")


# Флаги для предотвращения спама алертов
_last_requests_alert = None
_last_ram_alert = None


async def check_thresholds():
    """Проверяет пороги и отправляет алерты."""
    global _last_requests_alert, _last_ram_alert
    
    now = datetime.now()
    
    # Проверка запросов
    rpm = get_requests_per_minute()
    if rpm > REQUESTS_PER_MIN_THRESHOLD:
        if _last_requests_alert is None or (now - _last_requests_alert).seconds > 300:
            await send_alert(f"⚠️ <b>Высокая нагрузка!</b>\n\n📊 Запросов/мин: <b>{rpm}</b>\n⏰ {now.strftime('%H:%M:%S')}")
            _last_requests_alert = now
    
    # Проверка RAM
    ram = get_ram_usage()
    if ram > RAM_THRESHOLD_PERCENT:
        if _last_ram_alert is None or (now - _last_ram_alert).seconds > 300:
            await send_alert(f"⚠️ <b>Высокое использование RAM!</b>\n\n💾 RAM: <b>{ram:.1f}%</b>\n⏰ {now.strftime('%H:%M:%S')}")
            _last_ram_alert = now


async def send_daily_report():
    """Отправляет ежедневный отчёт."""
    stats = get_daily_stats()
    ram = get_ram_usage()
    
    message = f"""📊 <b>Ежедневный отчёт</b>
{datetime.now().strftime('%d.%m.%Y')}

📨 Запросов: <b>{stats['total_requests']}</b>
👥 Уникальных: <b>{stats['unique_users']}</b>
⚡ Среднее время: <b>{stats['avg_response_ms']} мс</b>
💾 RAM: <b>{ram:.1f}%</b>"""

    await send_alert(message)


async def monitoring_loop():
    """Фоновая задача мониторинга."""
    init_db()
    print("[MONITOR] Мониторинг запущен")
    
    last_daily_report = None
    
    while True:
        try:
            # Проверяем пороги каждые 10 секунд
            await check_thresholds()
            
            # Ежедневный отчёт в 20:00
            now = datetime.now()
            if now.hour == 20 and now.minute == 0:
                if last_daily_report != now.date():
                    await send_daily_report()
                    last_daily_report = now.date()
            
        except Exception as e:
            print(f"[MONITOR] Error: {e}")
        
        await asyncio.sleep(10)
