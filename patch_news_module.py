#!/usr/bin/env python3
"""
Автоматический установщик модуля новостей для RIZALTA Bot.
Запуск: python3 patch_news_module.py
"""

import os
import sys
import re

BOT_DIR = "/opt/bot"
HANDLERS_DIR = os.path.join(BOT_DIR, "handlers")

def patch_init_py():
    """Добавляет импорт в handlers/__init__.py"""
    init_path = os.path.join(HANDLERS_DIR, "__init__.py")
    
    with open(init_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "handle_news_menu" in content:
        print("✅ handlers/__init__.py: импорт уже есть")
        return
    
    import_block = '''
# Модуль новостей
from handlers.news import (
    handle_news_menu,
    handle_currency_rates,
    handle_weather,
    handle_news_digest,
)
'''
    
    content += import_block
    
    with open(init_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ handlers/__init__.py: импорт добавлен")


def patch_menu_py():
    """Добавляет кнопку новостей в главное меню."""
    menu_path = os.path.join(HANDLERS_DIR, "menu.py")
    
    with open(menu_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "news_menu" in content:
        print("✅ handlers/menu.py: кнопка уже есть")
        return
    
    # Ищем функцию handle_main_menu и добавляем кнопку
    # Типичный паттерн: inline_buttons = [ ... ]
    
    # Паттерн для поиска последней кнопки перед закрывающей скобкой в handle_main_menu
    # Добавляем кнопку новостей перед кнопкой "О проекте" или в конец списка
    
    # Ищем паттерн с inline_buttons в handle_main_menu
    pattern = r'(async def handle_main_menu.*?inline_buttons\s*=\s*\[)(.*?)(\])'
    
    def add_news_button(match):
        prefix = match.group(1)
        buttons = match.group(2)
        suffix = match.group(3)
        
        # Добавляем кнопку новостей
        news_button = '\n        [{"text": "📰 Новости", "callback_data": "news_menu"}],'
        
        # Вставляем перед последней кнопкой
        buttons_lines = buttons.rstrip().rstrip(',')
        new_buttons = buttons_lines + ',' + news_button
        
        return prefix + new_buttons + suffix
    
    # Попробуем более простой подход - найти конкретное место
    # Ищем строку с "О проекте" или "Контакты" и добавляем перед ней
    
    if '{"text": "ℹ️ О проекте"' in content:
        content = content.replace(
            '{"text": "ℹ️ О проекте"',
            '{"text": "📰 Новости", "callback_data": "news_menu"}],\n        [{"text": "ℹ️ О проекте"'
        )
        print("✅ handlers/menu.py: кнопка добавлена перед 'О проекте'")
    elif '[{"text": "📞 Контакты"' in content:
        content = content.replace(
            '[{"text": "📞 Контакты"',
            '[{"text": "📰 Новости", "callback_data": "news_menu"}],\n        [{"text": "📞 Контакты"'
        )
        print("✅ handlers/menu.py: кнопка добавлена перед 'Контакты'")
    else:
        # Если не нашли типичные кнопки, добавим вручную
        print("⚠️ handlers/menu.py: не удалось найти место для кнопки")
        print("   Добавьте вручную в inline_buttons функции handle_main_menu:")
        print('   [{"text": "📰 Новости", "callback_data": "news_menu"}],')
        return
    
    with open(menu_path, "w", encoding="utf-8") as f:
        f.write(content)


def patch_app_py():
    """Добавляет обработчики callback в app.py"""
    app_path = os.path.join(BOT_DIR, "app.py")
    
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "news_menu" in content:
        print("✅ app.py: обработчики уже есть")
        return
    
    # Код обработчиков
    handlers_code = '''
        # === НОВОСТИ ===
        elif data == "news_menu":
            from handlers.news import handle_news_menu
            await handle_news_menu(chat_id)
        elif data == "news_currency":
            from handlers.news import handle_currency_rates
            await handle_currency_rates(chat_id)
        elif data == "news_weather":
            from handlers.news import handle_weather
            await handle_weather(chat_id)
        elif data == "news_digest":
            from handlers.news import handle_news_digest
            await handle_news_digest(chat_id)
'''
    
    # Ищем место для вставки - перед else или в конце обработчика callback_query
    # Типичный паттерн: elif data == "something": ... else:
    
    # Ищем паттерн "else:" в обработчике callback и вставляем перед ним
    # Или ищем последний elif data == и вставляем после него
    
    # Паттерн для поиска последнего elif data == "..." перед else или концом
    pattern = r'(elif data == "[^"]+":.*?(?:await|pass)[^\n]*\n)'
    
    matches = list(re.finditer(pattern, content, re.DOTALL))
    
    if matches:
        # Вставляем после последнего elif data ==
        last_match = matches[-1]
        insert_pos = last_match.end()
        
        # Проверяем что после этого идёт else или конец функции
        after_match = content[insert_pos:insert_pos+100]
        
        if "else:" in after_match or "# ===" in after_match:
            content = content[:insert_pos] + handlers_code + content[insert_pos:]
            print("✅ app.py: обработчики добавлены")
        else:
            # Ищем "else:" и вставляем перед ним
            else_pattern = r'(\n\s*else:)'
            match = re.search(else_pattern, content[insert_pos:])
            if match:
                real_pos = insert_pos + match.start()
                content = content[:real_pos] + handlers_code + content[real_pos:]
                print("✅ app.py: обработчики добавлены перед else")
            else:
                print("⚠️ app.py: не удалось найти место для обработчиков")
                print("   Добавьте вручную в секцию callback_query:")
                print(handlers_code)
                return
    else:
        print("⚠️ app.py: не найдены обработчики callback")
        print("   Добавьте вручную:")
        print(handlers_code)
        return
    
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(content)


def check_news_py():
    """Проверяет наличие news.py"""
    news_path = os.path.join(HANDLERS_DIR, "news.py")
    
    if os.path.exists(news_path):
        print("✅ handlers/news.py: файл найден")
        return True
    else:
        print("❌ handlers/news.py: файл не найден!")
        print("   Сначала скопируйте news.py в /opt/bot/handlers/")
        return False


def check_aiohttp():
    """Проверяет установку aiohttp"""
    try:
        import aiohttp
        print("✅ aiohttp: установлен")
    except ImportError:
        print("📦 Устанавливаю aiohttp...")
        os.system("pip install aiohttp --break-system-packages")


def main():
    print("=" * 50)
    print("📰 Установка модуля новостей RIZALTA Bot")
    print("=" * 50)
    print()
    
    # Проверяем директорию
    if not os.path.exists(BOT_DIR):
        print(f"❌ Директория {BOT_DIR} не найдена!")
        sys.exit(1)
    
    os.chdir(BOT_DIR)
    
    # Проверяем файлы
    if not check_news_py():
        sys.exit(1)
    
    check_aiohttp()
    
    print()
    print("📝 Применяю патчи...")
    print()
    
    patch_init_py()
    patch_menu_py()
    patch_app_py()
    
    print()
    print("=" * 50)
    print("✅ Установка завершена!")
    print()
    print("Перезапустите бота:")
    print("  systemctl restart rizalta-bot")
    print()
    print("Проверьте логи:")
    print("  journalctl -u rizalta-bot -f")
    print("=" * 50)


if __name__ == "__main__":
    main()
