# SESSION_LOG — Последние сессии

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

## 19.03.2026 — Сводное КП для 3 лотов К3

**Сделано:**
- Сводное КП: 3 лота (В713, В715, В721) из building=3
- Индивидуальные КП + сводная таблица landscape
- PyPDF2 склейка, Pillow сжатие планировок, wkhtmltopdf
- Временные лоты удалены после генерации

**Файлы:** services/kp_pdf_generator.py

**Версия:** 2.7.2

---

## Предыдущие сессии → docs/RIZALTA_CURRENT.md
