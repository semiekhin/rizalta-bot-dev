#!/bin/bash
# Умный бэкап RIZALTA Bot

DATE=$(date +%Y%m%d_%H%M)
BOT_DIR="/opt/bot"
BACKUP_FILE="/tmp/rizalta_backup_${DATE}.tar.gz"

EMAIL_TO="89181011091s@mail.ru"

echo "📦 Создаю бэкап..."

# Создаём архив с критичными файлами
cd $BOT_DIR
tar -czf $BACKUP_FILE \
    .env \
    properties.db \
    data/ \
    2>/dev/null

BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
echo "✅ Архив создан: $BACKUP_FILE ($BACKUP_SIZE)"

# Отправляем на email
echo "📧 Отправляю на email..."

python3 << PYTHON
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
from datetime import datetime

msg = MIMEMultipart()
msg['From'] = "rizalta-bot@mail.ru"
msg['To'] = "$EMAIL_TO"
msg['Subject'] = f"🗄 RIZALTA Backup {datetime.now().strftime('%Y-%m-%d %H:%M')}"

body = """
Автоматический бэкап RIZALTA Bot

Содержимое архива:
- .env (секреты, токены)
- properties.db (база данных)
- data/ (JSON файлы, knowledge base)

Для восстановления:
1. git clone репозитория
2. Распаковать этот архив в /opt/bot/
3. Запустить бота
"""
msg.attach(MIMEText(body, 'plain', 'utf-8'))

# Прикрепляем файл
filepath = "$BACKUP_FILE"
with open(filepath, 'rb') as f:
    part = MIMEBase('application', 'gzip')
    part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(filepath)}"')
    msg.attach(part)

try:
    server = smtplib.SMTP("smtp.mail.ru", 587)
    server.starttls()
    server.login("rizalta-bot@mail.ru", "3QZURbnlnb7ga25PGBc7")
    server.send_message(msg)
    server.quit()
    print("✅ Email отправлен!")
except Exception as e:
    print(f"❌ Ошибка отправки: {e}")
PYTHON

# Удаляем временный файл
rm -f $BACKUP_FILE

echo "✅ Готово!"
