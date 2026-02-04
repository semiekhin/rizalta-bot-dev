#!/usr/bin/env python3
"""
DEV режим — polling вместо webhook.
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Импортируем обработчики из app.py
from app import process_callback, process_message, process_voice_message, handle_contact_shared
from services.monitoring import log_request, monitoring_loop

async def get_updates(session, offset=None, timeout=30):
    """Получает обновления через long polling."""
    url = f"{TG_API}/getUpdates"
    params = {"timeout": timeout}
    if offset:
        params["offset"] = offset
    
    async with session.get(url, params=params) as resp:
        data = await resp.json()
        return data.get("result", [])

async def delete_webhook(session):
    """Удаляет webhook перед запуском polling."""
    url = f"{TG_API}/deleteWebhook"
    async with session.post(url) as resp:
        result = await resp.json()
        print(f"[DEV] Webhook deleted: {result.get('ok')}")

async def handle_update(upd):
    """Обработка одного update — копия логики из webhook."""
    
    # Callback Query (inline-кнопки)
    callback_query = upd.get("callback_query")
    if callback_query:
        await process_callback(callback_query)
        return
    
    # Message
    msg = upd.get("message") or upd.get("edited_message")
    if not msg:
        return
    
    chat_id = msg["chat"]["id"]
    
    # Игнорируем сообщения из групповых чатов (бот отвечает только в личных)
    chat_type = msg["chat"].get("type", "private")
    if chat_type != "private":
        return
    
    text = (msg.get("text") or "").strip()
    
    # Контакт
    contact_data = msg.get("contact")
    if contact_data:
        await handle_contact_shared(chat_id, contact_data)
        return
    
    # Голосовое сообщение
    voice = msg.get("voice")
    if voice:
        await process_voice_message(chat_id, voice, msg.get("from", {}))
        return
    
    if not text:
        return
    
    user_info = msg.get("from", {})
    import time as _t
    _start = _t.time()
    await process_message(chat_id, text, user_info)
    duration = int((_t.time() - _start) * 1000)
    print(f"[TIMING] Response time: {duration} ms")
    log_request(chat_id, "message", duration)

async def reminder_loop():
    """Проверяет и отправляет напоминания каждую минуту."""
    import sqlite3
    from datetime import datetime, timedelta
    from pathlib import Path
    
    DB_PATH = Path("/opt/bot-dev/secretary.db")
    
    await asyncio.sleep(5)  # Даём боту запуститься
    print("[DEV] Фоновая задача напоминаний запущена")
    
    def get_user_tz(cursor, user_id):
        cursor.execute("SELECT timezone FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return row[0] if row else 3  # По умолчанию Москва
    
    while True:
        try:
            if DB_PATH.exists():
                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()
                
                # Получаем все pending задачи с временем
                cursor.execute("""
                    SELECT id, user_id, task_text, due_date, due_time, client_name
                    FROM tasks 
                    WHERE status = 'pending' 
                    AND reminder_sent = 0
                    AND due_time IS NOT NULL
                """)
                
                all_tasks = cursor.fetchall()
                tasks = []
                
                now_utc = datetime.utcnow()
                
                for task in all_tasks:
                    task_id, user_id, task_text, due_date, due_time, client_name = task
                    
                    # Получаем timezone пользователя
                    user_tz = get_user_tz(cursor, user_id)
                    
                    # Текущее время по timezone пользователя
                    now_user = now_utc + timedelta(hours=user_tz)
                    today_user = now_user.strftime("%Y-%m-%d")
                    current_time_user = now_user.strftime("%H:%M")
                    remind_time_user = (now_user + timedelta(minutes=15)).strftime("%H:%M")
                    
                    # Проверяем нужно ли напоминание
                    if due_date == today_user and due_time <= remind_time_user and due_time > current_time_user:
                        tasks.append(task)
                
                for task in tasks:
                    task_id, user_id, task_text, due_date, due_time, client_name = task
                    
                    client_info = f"\n👤 Клиент: {client_name}" if client_name else ""
                    message = f"""⏰ <b>Напоминание!</b>

📋 {task_text}{client_info}
🕐 Через 15 минут ({due_time})"""
                    
                    url = f"{TG_API}/sendMessage"
                    payload = {
                        "chat_id": user_id,
                        "text": message,
                        "parse_mode": "HTML",
                        "disable_notification": False
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, json=payload) as resp:
                            result = await resp.json()
                            if result.get("ok"):
                                cursor.execute("UPDATE tasks SET reminder_sent = 1 WHERE id = ?", (task_id,))
                                conn.commit()
                                print(f"[REMINDER] ✅ {user_id}: {task_text}")
                            else:
                                print(f"[REMINDER] ❌ {user_id}: {result}")
                
                conn.close()
        except Exception as e:
            print(f"[REMINDER] Error: {e}")
        
        await asyncio.sleep(60)


async def main():
    print("[DEV] RIZALTA Bot — режим polling")
    print("[DEV] Ctrl+C для остановки")
    print("=" * 40)
    
    # Запускаем фоновую задачу напоминаний
    asyncio.create_task(reminder_loop())
    
    # Запускаем мониторинг
    asyncio.create_task(monitoring_loop())
    
    async with aiohttp.ClientSession() as session:
        await delete_webhook(session)
        
        offset = None
        while True:
            try:
                updates = await get_updates(session, offset)
                for update in updates:
                    offset = update["update_id"] + 1
                    print(f"[DEV] update: {update}")
                    try:
                        await handle_update(update)
                    except Exception as e:
                        print(f"[DEV] Ошибка обработки: {e}")
                        import traceback
                        traceback.print_exc()
            except asyncio.CancelledError:
                print("\n[DEV] Остановка...")
                break
            except Exception as e:
                print(f"[DEV] Ошибка polling: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
