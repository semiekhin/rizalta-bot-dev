"""
RIZALTA Telegram Bot
Главный файл приложения.

Модульная архитектура:
- config/     - настройки
- models/     - состояния
- services/   - бизнес-логика
- handlers/   - обработчики событий
"""

import re
from fastapi import FastAPI, Request
from typing import Dict, Any, List

# Конфигурация
from config.settings import (
    TELEGRAM_BOT_TOKEN,
    MAIN_MENU_BUTTONS,
    MAIN_MENU_TRIGGER_TEXTS,
    LINK_FIXATION,
    LINK_SHAHMATKA,
)

# Состояния
from models.state import (
    get_dialog_state,
    set_dialog_state,
    clear_dialog_state,
    clear_user_state,
    get_budget,
    save_budget,
    is_in_booking_flow,
    DialogStates,
)

# Сервисы
from services.telegram import send_message, send_message_inline, answer_callback_query, send_document
from services.calculations import normalize_unit_code

# Обработчики
from handlers import (
    handle_secretary_menu,
    handle_secretary_day,
    handle_secretary_week,
    handle_secretary_task_detail,
    handle_secretary_done,
    handle_secretary_undone,
    handle_secretary_delete,
    handle_secretary_move_menu,
    handle_secretary_move_to,
    handle_secretary_add_prompt,
    process_secretary_input,
    # Динамические расчёты
    handle_calculations_menu_new,
    handle_calc_roi_menu,
    handle_calc_roi_by_area_menu,
    handle_calc_roi_by_budget_menu,
    handle_calc_roi_area_range,
    handle_calc_roi_budget_range,
    handle_calc_roi_lot,
    handle_calc_finance_menu,
    handle_calc_finance_by_area_menu,
    handle_calc_finance_by_budget_menu,
    handle_calc_finance_area_range,
    handle_calc_finance_budget_range,
    handle_calc_finance_lot,
    # Меню
    handle_start,
    handle_help,
    handle_back,
    handle_about_project,
    handle_calculations_menu,
    handle_why_rizalta,
    handle_why_altai,
    handle_architect,
    handle_choose_unit_for_roi,
    handle_choose_unit_for_finance,
    handle_choose_unit_for_layout,
    handle_main_menu,
    handle_myid,
    
    # Юниты
    handle_base_roi,
    handle_unit_roi,
    handle_finance_overview,
    handle_layouts,
    handle_select_lot,
    handle_budget_input,
    handle_format_input,
    handle_download_pdf,
    
    # Запись на показ
    handle_online_show_start,
    handle_call_manager,
    handle_contact_shared,
    handle_quick_contact,
    handle_booking_step,
    
    # AI
    handle_free_text,
    
    # КП
    handle_kp_menu,
    handle_kp_request,
    
    # Медиа
    handle_media_menu,
    handle_send_presentation,
    handle_send_presentation_file,
    handle_video_menu,
    handle_send_video,
)


app = FastAPI(title="RIZALTA Bot")


# ====== Текстовые триггеры для контекстного поиска ======

# Паттерны для презентации
PRESENTATION_PATTERNS = [
    r"презентаци",
    r"скачать презент",
    r"отправь презент",
    r"пришли презент",
    r"дай презент",
    r"покажи презент",
]

# Паттерны для фиксации клиента
FIXATION_PATTERNS = [
    r"фиксаци",
    r"зафиксир",
    r"закрепи",
    r"закрепить клиент",
]

# Паттерны для шахматки
SHAHMATKA_PATTERNS = [
    r"шахматк",
    r"шахмат",
    r"наличие",
    r"свободные лоты",
    r"какие лоты",
    r"что свободно",
    r"что есть в наличии",
]

# Паттерны для медиа
MEDIA_PATTERNS = [
    r"медиа",
    r"материал",
    r"видео",
    r"ролик",
]

# Паттерны для записи на показ
BOOKING_PATTERNS = [
    r"записать",
    r"запиши",
    r"показ",
    r"созвон",
    r"встреч",
    r"консультаци",
    r"связаться",
    r"позвони",
    r"перезвони",
]

# Паттерны для договоров
DOCS_PATTERNS = [
    r"договор",
    r"дду",
    r"аренд",
    r"документ",
]

# Паттерны для КП
KP_PATTERNS = [
    r"коммерческ",
    r"\bкп\b",
    r"предложени",
]


def match_patterns(text: str, patterns: list) -> bool:
    """Проверяет совпадение текста с паттернами."""
    text_lower = text.lower()
    for pattern in patterns:
        if re.search(pattern, text_lower):
            return True
    return False


# ====== Health check ======

@app.get("/")
async def health():
    """Health check."""
    return {"ok": True, "bot": "RIZALTA"}


# ====== Telegram Webhook ======

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """Главный webhook для обработки сообщений от Telegram."""
    
    try:
        upd = await request.json()
    except Exception as e:
        print(f"[WEBHOOK] JSON parse error: {e}")
        return {"ok": False}
    
    print(f"[WEBHOOK] update: {upd}")
    
    # ===== Callback Query (inline-кнопки) =====
    callback_query = upd.get("callback_query")
    if callback_query:
        await process_callback(callback_query)
        return {"ok": True}
    
    # ===== Message =====
    msg = upd.get("message") or upd.get("edited_message")
    if not msg:
        return {"ok": True}
    
    chat_id = msg["chat"]["id"]
    text = (msg.get("text") or "").strip()
    
    # Обработка контакта
    contact_data = msg.get("contact")
    if contact_data:
        await handle_contact_shared(chat_id, contact_data)
        return {"ok": True}
    
    # Обработка голосового сообщения
    voice = msg.get("voice")
    if voice:
        await process_voice_message(chat_id, voice, msg.get("from", {}))
        return {"ok": True}
    
    if not text:
        return {"ok": True}
    
    user_info = msg.get("from", {})
    
    await process_message(chat_id, text, user_info)
    return {"ok": True}


async def process_callback(callback: Dict[str, Any]):
    """Обработка нажатия inline-кнопки."""
    
    callback_id = callback.get("id")
    data = callback.get("data", "")
    message = callback.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    from_user = callback.get("from", {})
    username = from_user.get("username", "")
    
    if not chat_id:
        return
    
    # Убираем часики
    if callback_id:
        await answer_callback_query(callback_id)
    
    # ===== Роутинг callback_data =====
    
    if data == "download_pdf":
        await handle_download_pdf(chat_id, username)
    
    elif data == "select_lot":
        await handle_select_lot(chat_id)
    
    elif data == "call_manager" or data == "online_show":
        from handlers.booking_calendar import handle_booking_start
        await handle_booking_start(chat_id)
    
    elif data == "calculate_roi":
        await handle_choose_unit_for_roi(chat_id)
    
    elif data == "get_layouts":
        from handlers.docs import handle_documents_menu
        await handle_documents_menu(chat_id)
    
    elif data.startswith("roi_xlsx_"):
        area_x10 = int(data.replace("roi_xlsx_", ""))
        area = area_x10 / 10
        await send_message(chat_id, f"⏳ Создаю Excel для {area} м²...")
        from services.calc_xlsx_generator import generate_roi_xlsx
        xlsx_path = generate_roi_xlsx(area=area)
        if xlsx_path:
            await send_document(chat_id, xlsx_path, f"ROI_{area}m2.xlsx")
        else:
            await send_message(chat_id, f"❌ Ошибка создания Excel")

    elif data.startswith("roi_"):
        unit_code = data[4:]
        await handle_base_roi(chat_id, unit_code=unit_code)
    
    elif data.startswith("finance_"):
        unit_code = data[8:]
        await handle_finance_overview(chat_id, unit_code=unit_code)
    
    elif data.startswith("layout_"):
        unit_code = data[7:]
        await handle_layouts(chat_id, unit_code=unit_code)
    
    # ===== Медиа =====
    
    elif data == "media_menu":
        await handle_media_menu(chat_id)
    
    elif data == "media_presentation":
        await handle_send_presentation(chat_id)
    elif data.startswith("pres_"):
        await handle_send_presentation_file(chat_id, data)
    elif data == "media_video":
        await handle_video_menu(chat_id)
    
    # === AI-Секретарь ===
    elif data == "secretary_menu":
        await handle_secretary_menu(chat_id)
    elif data.startswith("sec_day_"):
        date_str = data.replace("sec_day_", "")
        await handle_secretary_day(chat_id, date_str)
    elif data.startswith("sec_week_"):
        date_str = data.replace("sec_week_", "")
        await handle_secretary_week(chat_id, date_str)
    elif data.startswith("sec_task_"):
        task_id = int(data.replace("sec_task_", ""))
        await handle_secretary_task_detail(chat_id, task_id)
    elif data.startswith("sec_done_"):
        task_id = int(data.replace("sec_done_", ""))
        await handle_secretary_done(chat_id, task_id)
    elif data.startswith("sec_undone_"):
        task_id = int(data.replace("sec_undone_", ""))
        await handle_secretary_undone(chat_id, task_id)
    elif data.startswith("sec_del_"):
        task_id = int(data.replace("sec_del_", ""))
        await handle_secretary_delete(chat_id, task_id)
    elif data.startswith("sec_move_") and not data.startswith("sec_moveto_"):
        task_id = int(data.replace("sec_move_", ""))
        await handle_secretary_move_menu(chat_id, task_id)
    elif data.startswith("sec_moveto_"):
        parts = data.replace("sec_moveto_", "").split("_")
        task_id = int(parts[0])
        new_date = parts[1]
        await handle_secretary_move_to(chat_id, task_id, new_date)
    elif data == "sec_add":
        await handle_secretary_add_prompt(chat_id)
    elif data.startswith("sec_add_"):
        preset_date = data.replace("sec_add_", "")
        await handle_secretary_add_prompt(chat_id, preset_date)
    elif data.startswith("video_"):
        await handle_send_video(chat_id, data)
    
    elif data == "back_to_menu":
        await handle_main_menu(chat_id)
    
    # ===== КП =====
    
    elif data == "kp_menu":
        await handle_kp_menu(chat_id)
    
    elif data == "kp_refine":
        await handle_kp_menu(chat_id)
    
    elif data == "kp_by_area":
        from handlers.kp import handle_kp_by_area_menu
        await handle_kp_by_area_menu(chat_id)
    
    elif data == "kp_by_budget":
        from handlers.kp import handle_kp_by_budget_menu
        await handle_kp_by_budget_menu(chat_id)
    
    elif data.startswith("kp_area_"):
        # kp_area_22_25 -> min=22, max=25
        from handlers.kp import handle_kp_area_range
        parts = data.replace("kp_area_", "").split("_")
        min_area, max_area = float(parts[0]), float(parts[1])
        await handle_kp_area_range(chat_id, min_area, max_area)
    
    elif data.startswith("kp_budget_"):
        # kp_budget_15_18 -> min=15, max=18
        from handlers.kp import handle_kp_budget_range
        parts = data.replace("kp_budget_", "").split("_")
        min_budget, max_budget = int(parts[0]), int(parts[1])
        await handle_kp_budget_range(chat_id, min_budget, max_budget)
    
    elif data.startswith("kp_send_"):
        # kp_send_273 -> отправить КП (273 = area * 10)
        from handlers.kp import handle_kp_send_one
        area_str = data.replace("kp_send_", "")
        area = int(area_str) / 10.0 if area_str.isdigit() else 0
        await handle_kp_send_one(chat_id, area=area)
    
    elif data.startswith("kp_show_area_"):
        # kp_show_area_22_30 -> показать все лоты по площади
        from handlers.kp import handle_kp_show_all_area
        parts = data.replace("kp_show_area_", "").split("_")
        min_area, max_area = float(parts[0]), float(parts[1])
        await handle_kp_show_all_area(chat_id, min_area, max_area)
    
    elif data.startswith("kp_show_budget_"):
        # kp_show_budget_15_18 -> показать все лоты по бюджету
        from handlers.kp import handle_kp_show_all_budget
        parts = data.replace("kp_show_budget_", "").split("_")
        min_budget, max_budget = int(parts[0]), int(parts[1])
        await handle_kp_show_all_budget(chat_id, min_budget, max_budget)

    elif data.startswith("kp_select_"):
        from handlers.kp import handle_kp_select_lot
        area_x10 = int(data.replace("kp_select_", ""))
        await handle_kp_select_lot(chat_id, area_x10)

    elif data.startswith("kp_gen_"):
        from handlers.kp import handle_kp_generate_pdf
        parts = data.replace("kp_gen_", "").rsplit("_", 1)
        if len(parts) == 2:
            area_x10 = int(parts[0])
            mode = parts[1]  # "100", "12", или "24"
            await handle_kp_generate_pdf(chat_id, area_x10, mode)

    # ===== Документы =====

    elif data == "doc_menu":
        from handlers.docs import handle_documents_menu
        await handle_documents_menu(chat_id)

    elif data == "doc_ddu":
        from handlers.docs import handle_send_ddu
        await handle_send_ddu(chat_id)

    elif data == "doc_arenda":
        from handlers.docs import handle_send_arenda
        await handle_send_arenda(chat_id)

    elif data == "doc_all":
        from handlers.docs import handle_send_all_docs
        await handle_send_all_docs(chat_id)

    # ===== Динамические расчёты =====

    elif data == "calc_main_menu":
        await handle_calculations_menu_new(chat_id)

    elif data == "calc_roi_menu":
        await handle_calc_roi_menu(chat_id)

    elif data == "calc_finance_menu":
        await handle_calc_finance_menu(chat_id)

    elif data == "calc_roi_by_area":
        await handle_calc_roi_by_area_menu(chat_id)

    elif data == "calc_roi_by_budget":
        await handle_calc_roi_by_budget_menu(chat_id)

    elif data == "calc_finance_by_area":
        await handle_calc_finance_by_area_menu(chat_id)

    elif data == "calc_finance_by_budget":
        await handle_calc_finance_by_budget_menu(chat_id)

    elif data.startswith("calc_roi_area_"):
        parts = data.replace("calc_roi_area_", "").split("_")
        min_area, max_area = float(parts[0]), float(parts[1])
        await handle_calc_roi_area_range(chat_id, min_area, max_area)

    elif data.startswith("calc_roi_budget_"):
        parts = data.replace("calc_roi_budget_", "").split("_")
        min_budget, max_budget = int(parts[0]), int(parts[1])
        await handle_calc_roi_budget_range(chat_id, min_budget, max_budget)

    elif data.startswith("calc_roi_show_area_"):
        from handlers.calc_dynamic import handle_calc_roi_show_all_area
        parts = data.replace("calc_roi_show_area_", "").split("_")
        min_area, max_area = float(parts[0]), float(parts[1])
        await handle_calc_roi_show_all_area(chat_id, min_area, max_area)

    elif data.startswith("calc_roi_show_budget_"):
        from handlers.calc_dynamic import handle_calc_roi_show_all_budget
        parts = data.replace("calc_roi_show_budget_", "").split("_")
        min_budget, max_budget = int(parts[0]), int(parts[1])
        await handle_calc_roi_show_all_budget(chat_id, min_budget, max_budget)

    elif data.startswith("calc_fin_show_area_"):
        from handlers.calc_dynamic import handle_calc_finance_show_all_area
        parts = data.replace("calc_fin_show_area_", "").split("_")
        min_area, max_area = float(parts[0]), float(parts[1])
        await handle_calc_finance_show_all_area(chat_id, min_area, max_area)

    elif data.startswith("calc_fin_show_budget_"):
        from handlers.calc_dynamic import handle_calc_finance_show_all_budget
        parts = data.replace("calc_fin_show_budget_", "").split("_")
        min_budget, max_budget = int(parts[0]), int(parts[1])
        await handle_calc_finance_show_all_budget(chat_id, min_budget, max_budget)
    elif data.startswith("calc_fin_area_"):
        parts = data.replace("calc_fin_area_", "").split("_")
        min_area, max_area = float(parts[0]), float(parts[1])
        await handle_calc_finance_area_range(chat_id, min_area, max_area)

    elif data.startswith("calc_fin_budget_"):
        parts = data.replace("calc_fin_budget_", "").split("_")
        min_budget, max_budget = int(parts[0]), int(parts[1])
        await handle_calc_finance_budget_range(chat_id, min_budget, max_budget)

    elif data.startswith("calc_roi_lot_"):
        area_str = data.replace("calc_roi_lot_", "")
        area = int(area_str) / 10.0 if area_str.isdigit() else 0
        await handle_calc_roi_lot(chat_id, area)

    elif data.startswith("calc_finance_lot_"):
        area_str = data.replace("calc_finance_lot_", "")
        area = int(area_str) / 10.0 if area_str.isdigit() else 0
        await handle_calc_finance_lot(chat_id, area)

    # ===== Календарь бронирования =====

    elif data == "booking_calendar":
        from handlers.booking_calendar import handle_booking_start
        await handle_booking_start(chat_id)

    elif data.startswith("book_spec_"):
        from handlers.booking_calendar import handle_select_specialist
        spec_id = int(data.replace("book_spec_", ""))
        await handle_select_specialist(chat_id, spec_id)

    elif data == "book_back_specialist":
        from handlers.booking_calendar import handle_booking_start
        await handle_booking_start(chat_id)

    elif data.startswith("book_date_"):
        from handlers.booking_calendar import handle_select_date
        date_str = data.replace("book_date_", "")
        await handle_select_date(chat_id, date_str)

    elif data.startswith("book_time_"):
        from handlers.booking_calendar import handle_select_time
        time_str = data.replace("book_time_", "")
        await handle_select_time(chat_id, time_str, username)

    elif data.startswith("book_confirm_"):
        from handlers.booking_calendar import handle_confirm_booking
        booking_id = int(data.replace("book_confirm_", ""))
        await handle_confirm_booking(chat_id, booking_id)

    elif data.startswith("book_decline_"):
        from handlers.booking_calendar import handle_decline_booking
        booking_id = int(data.replace("book_decline_", ""))
        await handle_decline_booking(chat_id, booking_id)

    # ===== Domoplaner =====
    elif data == "domo_all":
        flats = domoplaner_cache.get(chat_id, [])
        if not flats:
            await send_message(chat_id, "❌ Подборка не найдена. Отправьте ссылку заново.")
        else:
            await send_message(chat_id, f"⏳ Генерирую {len(flats)} КП...")
            from services.kp_pdf_generator import generate_kp_pdf
            success = 0
            for flat in flats:
                pdf_path = generate_kp_pdf(code=flat["code"], include_24m=True)
                if pdf_path:
                    await send_document(chat_id, pdf_path, f"КП_{flat['code']}.pdf")
                    success += 1
            await send_message(chat_id, f"✅ Создано {success} из {len(flats)} КП")


    elif data.startswith("domo_"):
        lot_code = data.replace("domo_", "")
        await send_message(chat_id, f"⏳ Генерирую КП для {lot_code}...")
        from services.kp_pdf_generator import generate_kp_pdf
        pdf_path = generate_kp_pdf(code=lot_code, include_24m=True)
        if pdf_path:
            await send_document(chat_id, pdf_path, f"КП_{lot_code}.pdf")
        else:
            await send_message(chat_id, f"❌ Лот {lot_code} не найден в базе.")

    # ===== Новости =====

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

    elif data == "news_flights":
        from handlers.news import handle_flights
        await handle_flights(chat_id)

    # ===== Сравнение депозит vs RIZALTA =====

    elif data == "compare_menu":
        from handlers.compare import handle_compare_menu
        await handle_compare_menu(chat_id)

    elif data == "compare_by_area":
        from handlers.compare import handle_compare_by_area_menu
        await handle_compare_by_area_menu(chat_id)

    elif data == "compare_by_budget":
        from handlers.compare import handle_compare_by_budget_menu
        await handle_compare_by_budget_menu(chat_id)

    elif data == "compare_quick":
        from handlers.compare import handle_compare_quick
        await handle_compare_quick(chat_id)

    elif data.startswith("compare_area_"):
        from handlers.compare import handle_compare_area_range
        parts = data.split("_")
        min_area = float(parts[2])
        max_area = float(parts[3])
        await handle_compare_area_range(chat_id, min_area, max_area)

    elif data.startswith("compare_budget_"):
        from handlers.compare import handle_compare_budget_range
        parts = data.split("_")
        min_budget = int(parts[2]) * 1_000_000
        max_budget = int(parts[3]) * 1_000_000
        await handle_compare_budget_range(chat_id, min_budget, max_budget)

    elif data.startswith("compare_lot_back_"):
        from handlers.compare import handle_compare_lot
        amount = int(data.split("_")[3])
        await handle_compare_lot(chat_id, "выбранный", amount)

    elif data.startswith("compare_lot_"):
        from handlers.compare import handle_compare_lot
        parts = data.split("_")
        lot_code = parts[2]
        price = int(parts[3]) * 1000
        await handle_compare_lot(chat_id, lot_code, price)

    elif data.startswith("compare_table_"):
        from handlers.compare import handle_compare_table
        amount = int(data.split("_")[2])
        await handle_compare_table(chat_id, amount)

    elif data == "compare_table":
        from handlers.compare import handle_compare_table
        await handle_compare_table(chat_id)

    elif data.startswith("compare_period_"):
        from handlers.compare import handle_compare_period
        parts = data.split("_")
        years = int(parts[2])
        amount = int(parts[3]) if len(parts) > 3 else 15_000_000
        await handle_compare_period(chat_id, years, amount)

    elif data.startswith("compare_full_"):
        from handlers.compare import handle_compare_full
        parts = data.split("_")
        years = int(parts[2])
        amount = int(parts[3]) if len(parts) > 3 else 15_000_000
        await handle_compare_full(chat_id, years, amount)

    elif data.startswith("compare_amount_"):
        from handlers.compare import handle_compare_amount_menu
        context = data.split("_")[2]
        await handle_compare_amount_menu(chat_id, context)

    elif data.startswith("compare_sum_"):
        from handlers.compare import handle_compare_with_amount
        parts = data.split("_")
        amount_mln = int(parts[2])
        context = parts[3]
        await handle_compare_with_amount(chat_id, amount_mln, context)

    elif data.startswith("compare_pdf_"):
        from handlers.compare import handle_compare_pdf
        parts = data.split("_")
        years = int(parts[2])
        amount = int(parts[3])
        await handle_compare_pdf(chat_id, years, amount, username)


    elif data == "booking_menu":
        from handlers.booking_fixation import handle_booking_menu
        await handle_booking_menu(chat_id, user_info.get("id", chat_id))

    elif data == "booking_auth":
        from handlers.booking_fixation import handle_booking_auth_start
        await handle_booking_auth_start(chat_id, from_user.get("id", chat_id))

    elif data == "booking_reauth":
        from handlers.booking_fixation import handle_booking_reauth
        await handle_booking_reauth(chat_id, from_user.get("id", chat_id))

    elif data == "booking_new":
        from handlers.booking_fixation import handle_booking_new
        await handle_booking_new(chat_id, from_user.get("id", chat_id))

    elif data == "booking_cancel":
        from handlers.booking_fixation import handle_booking_cancel
        await handle_booking_cancel(chat_id, from_user.get("id", chat_id))

    elif data == "booking_skip_comment":
        from handlers.booking_fixation import handle_booking_skip_comment
        await handle_booking_skip_comment(chat_id, from_user.get("id", chat_id))

# Кеш подборок domoplaner
domoplaner_cache = {}

async def handle_domoplaner_link(chat_id: int, url: str):
    """Обрабатывает ссылку на подборку domoplaner."""
    from services.domoplaner_parser import parse_domoplaner_set
    
    await send_message(chat_id, "⏳ Загружаю подборку...")
    
    flats = parse_domoplaner_set(url)
    
    if not flats:
        await send_message(chat_id, "❌ Не удалось загрузить подборку. Проверьте ссылку.")
        return
    
    domoplaner_cache[chat_id] = flats
    
    buttons = []
    for flat in flats:
        price_mln = flat["price"] / 1_000_000
        btn_text = f"{flat['code']} — {flat['area']} м² — {price_mln:.1f} млн"
        callback = f"domo_{flat['code']}"
        buttons.append([{"text": btn_text, "callback_data": callback}])
    
    buttons.append([{"text": f"📦 Создать {len(flats)} КП", "callback_data": "domo_all"}])
    buttons.append([{"text": "🔙 Отмена", "callback_data": "main_menu"}])
    
    text = f"📋 Подборка от менеджера\n\nНайдено {len(flats)} квартир.\nВыберите для генерации КП:"
    
    await send_message_inline(chat_id, text, buttons)

async def process_message(chat_id: int, text: str, user_info: Dict[str, Any]):
    """Главный роутер текстовых сообщений."""
    
    # ===== Проверка кнопок главного меню =====
    # При нажатии сбрасываем состояния
    is_main_menu_button = any(btn in text for btn in MAIN_MENU_TRIGGER_TEXTS)
    
    if is_main_menu_button:
        clear_dialog_state(chat_id)
    

    # ===== Обработка ввода фиксации =====
    from handlers.booking_fixation import handle_booking_input, has_active_booking_state
    if has_active_booking_state(user_info.get("id", chat_id)):
        user_id = user_info.get("id", chat_id)
        handled = await handle_booking_input(chat_id, user_id, text)
        if handled:
            return
    
    # ===== AI-Секретарь (проверка режима) =====
    from services.secretary_db import is_secretary_mode, set_secretary_mode
    if is_secretary_mode(chat_id):
        # Если нажата кнопка главного меню — выходим из режима
        if is_main_menu_button:
            set_secretary_mode(chat_id, False)
        else:
            handled = await process_secretary_input(chat_id, text)
            if handled:
                return
    
    # ===== Команды =====
    if text == "/help":
        await handle_help(chat_id)
        return
    
    if text == "/myid":
        await handle_myid(chat_id, user_info)
        return
    
    
    if text.startswith("/start"):
        await handle_start(chat_id, text, user_info)
        return
    
    # ===== Ссылки domoplaner =====
    from services.domoplaner_parser import is_domoplaner_link, parse_domoplaner_set
    domo_url = is_domoplaner_link(text)
    if domo_url:
        await handle_domoplaner_link(chat_id, domo_url)
        return
    
    # ===== Кнопка Назад =====
    
    if text in ("🔙 Назад", "⬅️ Назад", "Назад"):
        await handle_back(chat_id)
        return
    
    # ===== Диалоговые состояния =====
    
    state = get_dialog_state(chat_id)
    
    # Подбор лота: ввод бюджета
    if state == DialogStates.CHOOSE_UNIT_ASK_BUDGET and not is_main_menu_button:
        await handle_budget_input(chat_id, text)
        return
    
    # Подбор лота: выбор формата
    if state == DialogStates.CHOOSE_UNIT_ASK_FORMAT and not is_main_menu_button:
        await handle_format_input(chat_id, text)
        return
    
    # Запись на показ: ввод контакта
    if state == DialogStates.ASK_CONTACT_FOR_CALLBACK and not is_main_menu_button:
        if text == "✍️ Ввести вручную":
            await send_message(chat_id, "Напишите ваш телефон или @username:")
            return
        await handle_quick_contact(chat_id, text)
        return
    
    # Многошаговая запись
    if is_in_booking_flow(chat_id) and not text.startswith("/") and not is_main_menu_button:
        await handle_booking_step(chat_id, text)
        return
    
    # Выбор юнита для ROI
    if state == DialogStates.CHOOSE_ROI_UNIT:
        normalized = normalize_unit_code(text)
        if normalized in ["A209", "B210", "A305"]:
            await handle_base_roi(chat_id, unit_code=text)
            return
    
    # Выбор юнита для рассрочки
    if state == DialogStates.CHOOSE_FINANCE_UNIT:
        normalized = normalize_unit_code(text)
        if normalized in ["A209", "B210", "A305"]:
            await handle_finance_overview(chat_id, unit_code=text)
            return
    
    # Выбор юнита для планировки
    if state == DialogStates.CHOOSE_PLAN_UNIT:
        normalized = normalize_unit_code(text)
        if normalized in ["A209", "B210", "A305"]:
            await handle_layouts(chat_id, unit_code=text)
            return
    
    # Запрос КП
    if state == DialogStates.AWAIT_KP_REQUEST and not is_main_menu_button:
        await handle_kp_request(chat_id, text)
        return
    
    # ===== Кнопки главного меню =====
    
    if "📖 О проекте" in text or text == "О проекте":
        await handle_about_project(chat_id)
        return
    
    if "💰 Расчёты" in text or text == "Расчёты":
        await handle_calculations_menu_new(chat_id)
        return

    if "📊 Сравнение" in text or "депозит" in text.lower():
        from handlers.compare import handle_compare_menu
        await handle_compare_menu(chat_id)
        return
    
    if "📋 КП (JPG)" in text:
        await handle_kp_menu(chat_id)
        return
    
    if "🎯 Подобрать лот" in text or "Выбрать лот" in text or "🧩 Выбрать лот" in text:
        await handle_select_lot(chat_id)
        return
    
    if "🔥 Записаться на онлайн-показ" in text or "📅 Записаться на онлайн показ" in text:
        from handlers.booking_calendar import handle_booking_start
        await handle_booking_start(chat_id)
        return
    
    if "📄 Договоры" in text:
        from handlers.docs import handle_documents_menu
        await handle_documents_menu(chat_id)
        return
    
    # ===== Кнопки с внешними ссылками =====
    
    if "📌 Фиксация" in text:
        from handlers.booking_fixation import handle_booking_menu, has_active_booking_state
        await handle_booking_menu(chat_id, user_info.get("id", chat_id))
        return
    
    if "🏠 Шахматка" in text:
        inline_buttons = [
            [{"text": "🔗 Открыть шахматку", "url": LINK_SHAHMATKA}]
        ]
        await send_message_inline(
            chat_id,
            "🏠 <b>Шахматка</b>\n\nНажмите кнопку ниже, чтобы открыть шахматку с актуальными лотами:",
            inline_buttons
        )
        return
    
    if "🗓 Секретарь" in text:
        await handle_secretary_menu(chat_id)
        return
    
    if "📰 Новости" in text:
        from handlers.news import handle_news_menu
        await handle_news_menu(chat_id)
        return

    if "🎬 Медиа" in text:
        await handle_media_menu(chat_id)
        return
    
    # ===== Подменю "О проекте" =====
    
    if "Почему RIZALTA" in text or "✨ Почему RIZALTA" in text:
        await handle_why_rizalta(chat_id)
        return
    
    if "Почему Алтай" in text or "🏔 Почему Алтай" in text or "ℹ️ Почему Алтай" in text:
        await handle_why_altai(chat_id)
        return
    
    if "Об архитекторе" in text or "👨‍🎨 Об архитекторе" in text:
        await handle_architect(chat_id)
        return
    
    # ===== Подменю "Расчёты" =====
    
    if "📊 Рентабельность/доходность" in text or "📊 Расчёт доходности" in text:
        await handle_choose_unit_for_roi(chat_id)
        return
    
    if "💳 Рассрочка и ипотека" in text:
        await handle_choose_unit_for_finance(chat_id)
        return
    
    # ===== Подменю "Медиа" =====
    
    if "📊 Презентация" in text:
        await handle_send_presentation(chat_id)
        return
    
    # ===== Выбор юнита по кнопкам =====
    
    if text in ["A209", "B210", "A305"]:
        state = get_dialog_state(chat_id)
        
        if state == DialogStates.CHOOSE_ROI_UNIT:
            await handle_base_roi(chat_id, unit_code=text)
            return
        
        if state == DialogStates.CHOOSE_FINANCE_UNIT:
            await handle_finance_overview(chat_id, unit_code=text)
            return
        
        if state == DialogStates.CHOOSE_PLAN_UNIT:
            await handle_layouts(chat_id, unit_code=text)
            return
        
        # Без состояния — игнорируем
        return
    
    # ===== Контекстный поиск по тексту =====
    
    # Презентация
    if match_patterns(text, PRESENTATION_PATTERNS):
        inline_buttons = [
            [{"text": "📥 Скачать презентацию", "callback_data": "media_presentation"}],
            [{"text": "🔙 В меню", "callback_data": "back_to_menu"}]
        ]
        await send_message_inline(
            chat_id,
            "📊 <b>Презентация проекта RIZALTA</b>\n\nГотов отправить презентацию в PDF формате.",
            inline_buttons
        )
        return
    
    # Фиксация клиента
    if match_patterns(text, FIXATION_PATTERNS):
        from handlers.booking_fixation import handle_booking_menu
        await handle_booking_menu(chat_id, user_info.get("id", chat_id))
        return
    
    # Шахматка
    if match_patterns(text, SHAHMATKA_PATTERNS):
        inline_buttons = [
            [{"text": "🏠 Открыть шахматку", "url": LINK_SHAHMATKA}],
            [{"text": "🔙 В меню", "callback_data": "back_to_menu"}]
        ]
        await send_message_inline(
            chat_id,
            "🏠 <b>Шахматка</b>\n\nАктуальная шахматка с доступными лотами:",
            inline_buttons
        )
        return
    
    # Медиа
    if match_patterns(text, MEDIA_PATTERNS):
        await handle_media_menu(chat_id)
        return
    
    # Запись на показ
    if match_patterns(text, BOOKING_PATTERNS):
        inline_buttons = [
            [{"text": "🔥 Записаться на показ", "callback_data": "online_show"}],
            [{"text": "🔙 В меню", "callback_data": "back_to_menu"}]
        ]
        await send_message_inline(
            chat_id,
            "📅 <b>Запись на онлайн-показ</b>\n\nХотите записаться на онлайн-показ с менеджером проекта?",
            inline_buttons
        )
        return
    
    # Договоры
    if match_patterns(text, DOCS_PATTERNS):
        from handlers.docs import handle_documents_menu
        await handle_documents_menu(chat_id)
        return
    
    # КП
    if match_patterns(text, KP_PATTERNS):
        inline_buttons = [
            [{"text": "📋 Открыть меню КП", "callback_data": "kp_menu"}],
            [{"text": "🔙 В меню", "callback_data": "back_to_menu"}]
        ]
        await send_message_inline(
            chat_id,
            "📋 <b>Коммерческие предложения</b>\n\nМогу отправить КП по площади или бюджету:",
            inline_buttons
        )
        return
    
    # ===== Свободный текст → AI =====
    
    await handle_free_text(chat_id, text)


async def process_voice_message(chat_id: int, voice: Dict[str, Any], user_info: Dict[str, Any]):
    """Обработка голосового сообщения через Whisper API."""
    from services.telegram import download_file
    from services.speech import transcribe_voice
    
    file_id = voice.get("file_id")
    if not file_id:
        return
    
    # Уведомляем пользователя
    await send_message(chat_id, "🎤 Распознаю голосовое сообщение...")
    
    # Скачиваем файл
    save_path = f"/tmp/voice_{chat_id}_{file_id}.ogg"
    downloaded = await download_file(file_id, save_path)
    
    if not downloaded:
        await send_message(chat_id, "❌ Не удалось обработать голосовое сообщение. Попробуйте ещё раз.")
        return
    
    # Распознаём речь
    text = transcribe_voice(save_path)
    
    if not text:
        await send_message(chat_id, "❌ Не удалось распознать речь. Попробуйте ещё раз или напишите текстом.")
        return
    
    # Показываем распознанный текст
    await send_message(chat_id, f"📝 Распознано: <i>{text}</i>")
    
    # Обрабатываем как обычное сообщение
    await process_message(chat_id, text, user_info)


# ====== Запуск ======

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
