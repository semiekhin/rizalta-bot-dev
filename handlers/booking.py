"""
Обработчики записи на показ и связи с менеджером.
"""

from typing import Dict, Any, Optional

from config.settings import MAIN_MENU_BUTTONS
from models.state import (
    set_dialog_state,
    clear_dialog_state,
    get_dialog_state,
    get_budget,
    get_format,
    get_booking_state,
    start_booking,
    update_booking_state,
    clear_booking_state,
    DialogStates,
)
from services.telegram import send_message, send_message_inline
from services.notifications import send_booking_notification
from services.calculations import fmt_rub


async def handle_online_show_start(chat_id: int):
    """
    ✅ Записаться на онлайн-показ — начало диалога.
    """
    set_dialog_state(chat_id, DialogStates.ASK_CONTACT_FOR_CALLBACK)
    budget = get_budget(chat_id)
    
    lines = []
    lines.append("Отлично, давайте запишу вас на онлайн-показ RIZALTA. 🎥")
    if budget:
        lines.append(f"Я зафиксировал ваш бюджет: {fmt_rub(budget)}.")
    lines.append("\nПоделитесь контактом для связи или введите вручную:")
    
    await send_message(
        chat_id,
        "\n".join(lines),
        with_keyboard=True,
        buttons=[
            [{"text": "📱 Поделиться контактом", "request_contact": True}],
            ["🔙 Назад"],
        ]
    )


async def handle_call_manager(chat_id: int):
    """
    📞 Вызвать менеджера — то же что и запись на показ.
    """
    await handle_online_show_start(chat_id)


async def handle_contact_shared(chat_id: int, contact_data: Dict[str, Any]):
    """
    Обработка кнопки "Поделиться контактом".
    """
    # Проверяем состояние бронирования онлайн-показа
    from handlers.booking_calendar import get_booking_state, set_booking_state, show_booking_confirmation
    from services.user_profiles import save_profile
    
    booking_state = get_booking_state(chat_id)
    if booking_state.get("step") == "awaiting_phone":
        phone = contact_data.get("phone_number", "")
        first_name = contact_data.get("first_name", "")
        last_name = contact_data.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip()
        
        # Сохраняем в профиль
        save_profile(chat_id, name=full_name, phone=phone)
        set_booking_state(chat_id, realtor_name=full_name, realtor_phone=phone, step="confirm_booking")
        
        # Показываем подтверждение
        await show_booking_confirmation(chat_id, {"first_name": first_name, "last_name": last_name})
        return
    
    state = get_dialog_state(chat_id)
    
    if state != DialogStates.ASK_CONTACT_FOR_CALLBACK:
        return
    
    phone = contact_data.get("phone_number", "")
    first_name = contact_data.get("first_name", "")
    last_name = contact_data.get("last_name", "")
    
    # Формируем контакт
    full_name = f"{first_name} {last_name}".strip()
    if phone:
        if full_name:
            contact = f"+{phone} ({full_name})"
        else:
            contact = f"+{phone}"
    else:
        contact = full_name or "Контакт не указан"
    
    budget = get_budget(chat_id)
    pay_format = get_format(chat_id)
    
    clear_dialog_state(chat_id)
    
    # Подтверждение пользователю
    lines = []
    lines.append("✅ Заявка на онлайн-показ зафиксирована.")
    if budget:
        lines.append(f"• Бюджет: {fmt_rub(budget)}")
    if pay_format:
        lines.append(f"• Формат: {pay_format}")
    if contact:
        lines.append(f"• Контакт: {contact}")
    lines.append(
        "\nМенеджер проекта свяжется с вами, чтобы уточнить детали и подобрать финальный лот."
    )
    
    await send_message(chat_id, "\n".join(lines), with_keyboard=True, buttons=MAIN_MENU_BUTTONS)
    
    # Уведомление менеджерам
    await send_booking_notification(
        chat_id=chat_id,
        name=full_name,
        contact=contact,
        budget=budget,
        pay_format=pay_format,
    )


async def handle_quick_contact(chat_id: int, text: str):
    """
    Обработка ввода контакта вручную (текстом).
    """
    contact = text.strip()
    budget = get_budget(chat_id)
    pay_format = get_format(chat_id)
    
    clear_dialog_state(chat_id)
    
    # Подтверждение
    lines = []
    lines.append("✅ Заявка на онлайн-показ зафиксирована.")
    if budget:
        lines.append(f"• Бюджет: {fmt_rub(budget)}")
    if pay_format:
        lines.append(f"• Формат: {pay_format}")
    if contact:
        lines.append(f"• Контакт: {contact}")
    lines.append(
        "\nМенеджер проекта свяжется с вами, чтобы уточнить детали и подобрать финальный лот."
    )
    
    await send_message(chat_id, "\n".join(lines), with_keyboard=True, buttons=MAIN_MENU_BUTTONS)
    
    # Уведомление менеджерам
    await send_booking_notification(
        chat_id=chat_id,
        contact=contact,
        budget=budget,
        pay_format=pay_format,
    )


# ====== Многошаговая запись (если нужна) ======

async def handle_booking_step(chat_id: int, text: str):
    """
    Многошаговая форма записи на показ.
    Собираем: имя → контакт → удобное время.
    """
    state_data = get_booking_state(chat_id)
    
    if not state_data:
        start_booking(chat_id)
        await send_message(
            chat_id,
            "📝 Отлично! Давайте запишу вас на онлайн-показ RIZALTA.\n\n"
            "Как к вам обращаться?"
        )
        return
    
    stage = state_data.get("stage")
    
    # Шаг 1: имя
    if stage == DialogStates.BOOKING_ASK_NAME:
        update_booking_state(chat_id, name=text.strip(), stage=DialogStates.BOOKING_ASK_CONTACT)
        await send_message(
            chat_id,
            "📱 Как с вами удобнее связаться — укажите, пожалуйста, телефон или @telegram."
        )
        return
    
    # Шаг 2: контакт
    if stage == DialogStates.BOOKING_ASK_CONTACT:
        update_booking_state(chat_id, contact=text.strip(), stage=DialogStates.BOOKING_ASK_TIME)
        await send_message(
            chat_id,
            "⏰ В какое время вам удобнее выйти на связь? "
            "(Например: сегодня после 18:00 по Москве, завтра утром и т.п.)"
        )
        return
    
    # Шаг 3: время — финал
    if stage == DialogStates.BOOKING_ASK_TIME:
        update_booking_state(chat_id, time=text.strip())
        
        state_data = get_booking_state(chat_id)
        name = state_data.get("name", "—")
        contact = state_data.get("contact", "—")
        time_pref = state_data.get("time", "—")
        budget = get_budget(chat_id)
        
        clear_booking_state(chat_id)
        
        # Подтверждение
        await send_message(
            chat_id,
            "✅ Спасибо! Я зафиксировал вашу заявку на онлайн-показ RIZALTA.\n\n"
            "Менеджер свяжется с вами в указанное время, чтобы показать лоты и "
            "подобрать оптимальный сценарий под ваш бюджет. 🙌",
            with_keyboard=True,
            buttons=MAIN_MENU_BUTTONS,
        )
        
        # Уведомление
        await send_booking_notification(
            chat_id=chat_id,
            name=name,
            contact=contact,
            budget=budget,
            time_pref=time_pref,
        )
        return
    
    # Неизвестный шаг — начинаем заново
    start_booking(chat_id)
    await send_message(
        chat_id,
        "📝 Давайте начнём запись на онлайн-показ заново.\n\nКак к вам обращаться?"
    )
