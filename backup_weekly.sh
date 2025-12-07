#!/bin/bash
# Еженедельный бэкап медиа RIZALTA Bot

DATE=$(date +%Y%m%d)
BOT_DIR="/opt/bot"
BACKUP_FILE="/tmp/rizalta_media_${DATE}.tar.gz"

EMAIL_TO="89181011091s@mail.ru"

echo "📦 Создаю бэкап медиа..."

cd $BOT_DIR
tar -czf $BACKUP_FILE \
    kp_all/ \
    media/ \
    2>/dev/null

BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
echo "✅ Архив создан: $BACKUP_FILE ($BACKUP_SIZE)"

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
msg['Subject'] = f"🗄 RIZALTA Media Backup {datetime.now().strftime('%Y-%m-%d')}"

body = """
Еженедельный бэкап медиа RIZALTA Bot

Содержимое архива:
- kp_all/ (69 КП картинок)
- media/ (презентация, документы)
"""
msg.attach(MIMEText(body, 'plain', 'utf-8'))

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
    print(f"❌ Ошибка: {e}")
PYTHON

rm -f $BACKUP_FILE
echo "✅ Готово!"
