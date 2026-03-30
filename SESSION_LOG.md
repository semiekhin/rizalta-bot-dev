# SESSION_LOG — Последние сессии

## 24.03.2026 — Cleanup v2.7.2: А101, base64, 380px, units_db, Claude Code

**Сделано:**
- Закоммичены незакоммиченные изменения kp_pdf_generator.py (download_layout base64, убран А101)
- Вернута ширина планировки 380px (была 220px для сводного КП)
- Откат units_db.py: status=available вернён в get_lot_by_code()
- Claude Code подключён к проекту (CLAUDE.md создан)

**Коммиты:** cleanup + фиксация состояния

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

## 05.03.2026 — Деплой траншевой ипотеки в PROD

**Сделано:**
- **PDF планировка исправлена:** float→table layout + base64 inline image (вместо file://)
- **Типографика PDF улучшена:** шрифты 16-19px, отступы 14px, мес→мес.
- **Траншевая ипотека задеплоена в PROD:** app.py + kp.py + все файлы сервиса
- **Кнопка переименована:** «Ипотека» → «Ипотека СОВКОМБАНК 4.4%» (DEV + PROD)

**Файлы:** app.py, handlers/kp.py, services/tranche_mortgage_calculator.py, services/tranche_mortgage_pdf_generator.py, handlers/tranche_mortgage.py

**Версия:** 2.7.2

---

## Предыдущие сессии → docs/RIZALTA_CURRENT.md
