# SESSION_LOG — Последние сессии

## 12.04.2026 — Срок сдачи К3: 2 кв. 2028 + деплой в PROD

**Сделано:**
- **Срок сдачи К3 = 2 кв. 2028:** условие по building в `kp_pdf_generator.py`, обновлён `corp3.py`, `rizalta_finance.json` (поле `completion_by_building`), `ai_chat.py` с группировкой корпусов
- **Деплой в PROD:** коммит `bc6666f`, бонусом уехал давно ждавший фикс `data:image` в `kp_pdf_generator.py`
- **Подключение:** Claude Code теперь работает на сервере через `root` (не `claude-dev`)
- **Контекст:** создана система CLAUDE.md + SESSION_LOG.md + BACKLOG.md по стандарту Sofia

**Файлы:** services/kp_pdf_generator.py, handlers/corp3.py, data/rizalta_finance.json, services/ai_chat.py, CLAUDE.md, SESSION_LOG.md, BACKLOG.md

**Найденный баг (не пофикшен):** `services/calc_universal.py:137` — `CUSTOM_INSTALLMENT_UNITS` без проверки `building==1`, перенесён в BACKLOG P1

**Версия:** 2.7.2

---

## 30.03.2026 — Система управления контекстом + исследование Custom Installment

**Сделано:**
- **CLAUDE.md** создан по формату Sofia-GPT (218 строк): архитектура, 19 handlers, 22 services, БД, правила, уроки
- **SESSION_LOG.md** + **BACKLOG.md** созданы, старый CLAUDE.md → CLAUDE_OLD.md
- **Исследование CUSTOM_INSTALLMENT_UNITS:** 11 кодов К1, 5 мест проверки, найден баг в calc_universal.py:137 (нет проверки building==1)
- **Исследование ограничения по площади:** правила нет, ограничение только по списку кодов
- **Добавлена секция "Промпты для Claude Code"** в CLAUDE.md (критерии готовности задачи)

**Файлы:** CLAUDE.md, CLAUDE_OLD.md, SESSION_LOG.md, BACKLOG.md

**Найденный баг:** `services/calc_universal.py:137` — `CUSTOM_INSTALLMENT_UNITS` проверяется без `building==1` (пропущен при фиксе 01.03)

**Версия:** 2.7.2

---

## 24.03.2026 — Cleanup v2.7.2: А101, base64, 380px, units_db, Claude Code

**Сделано:**
- Закоммичены незакоммиченные изменения kp_pdf_generator.py (download_layout base64, убран А101)
- Вернута ширина планировки 380px (была 220px для сводного КП)
- Откат units_db.py: status=available вернён в get_lot_by_code()
- Claude Code подключён к проекту (CLAUDE.md создан)

**Файлы:** services/kp_pdf_generator.py, services/units_db.py

**Версия:** 2.7.2

---

## Предыдущие сессии → docs/RIZALTA_CURRENT.md
