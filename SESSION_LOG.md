# SESSION_LOG — Последние сессии

## 08.05.2026 — Расследование В225: WebApp обходит CUSTOM_INSTALLMENT, генерит КП с 18 мес (read-only audit)

**Жалоба риэлторов:** 04.05.2026 сгенерировано КП по В225 (К1, 22.1 м², 15.028M ₽) с рассрочкой 18 мес, лот сейчас в БД отсутствует. Подтвердить факт, найти источник 18 мес, найти когда лот ушёл.

**Режим:** read-only, ничего не правил/не рестартил/не коммитил по коду.

**Ключевые находки:**

**1) Telegram-бот (PROD `/opt/bot`) — 18 мес для В225 заблокированы корректно.**
- `services/kp_pdf_generator.py:20`: `CUSTOM_INSTALLMENT_UNITS = [..., 'В225', ...]` (12 кодов), `is_custom = code in list and building == 1`
- Карточка В225 в TG-боте показывает только 2 кнопки КП: `kp_gen_В225_1_100` и `kp_gen_В225_1_12`. Кнопки `_full` (12+18 мес) нет.
- За 15.04–08.05 в логах PROD-бота: 26× `KP_В225_12m.pdf`, 5× `KP_В225_100.pdf`, **0×** `KP_В225_18m.pdf` или `_full`.

**2) WebApp PROD (`/opt/webapp`, порт 8003, `webapp.rizaltaservice.ru`) — баг подтверждён.**
- `backend/services/kp_pdf_generator.py:21`: `CUSTOM_INSTALLMENT_UNITS = ['В327', 'В615', 'В527', 'В517', 'В617', 'В525', 'В625', 'А101']` — **В225 отсутствует**, и `is_custom = code in list` (без проверки `building==1`).
- WebApp `kp_pdf_generator.py` не правился с 25.01.2026 (`101f157`); правки в bot-PROD-листе (В217/В225/В317/В417 — `4ae4774`; В717 — `ec87671`) в webapp **не зеркалировались**.
- Логи `journalctl -u webapp` 04.05: 4 генерации КП по В225, **3 из них — `KP_В225_12m_18m.pdf`** (с включённой 18-мес секцией): 13:03, 18:02, 18:03.
- Дельта списков: webapp лишний `А101`, не хватает 5 кодов (В217, В225, В317, В417, В717). Условие is_custom без `building==1` (в TG-боте — с проверкой).

**3) RIZALTA MAX bot (`/opt/bot-max`) — отдельная безопасная реализация.**
- Не использует список кодов: `is_custom = lot["area"] <= CUSTOM_INSTALLMENT_MAX_AREA` (= 22.1, в `config/settings.py:30`).
- В225 (22.1 м²) попадает в custom, в логах max-bot за период — только `_12m` и `_100`, файлов `_12m_18m` для В225 нет.

**4) Когда В225 пропал из PROD-БД.**
- Парсер `/var/log/rizalta_parser.log` (cron `/opt/bot` 03:00 ежедневно): май-3 → 450, май-4 → 450, **май-5 → 449** (тут пропал), май-6 → 448, май-7 → 448, май-8 → 447.
- Точный момент в логах бота: `May 05 13:11:53` карточка В225 ещё рендерилась из закэшированного TG-сообщения от 04.05; `May 05 19:43:28` клик на `kp_lot_В225_1` дал «❌ Лот В225 не найден в корпусе 1» (DB-лукап). Парсер 05.05 03:00 удалил лот.
- Промежуточные клики на `mgp_calc_*`/`mortgage_*`/`tmort_*` 05.05 13:11–13:12 успешно обработались, потому что area закодирована в callback и DB-лукап там не нужен.

**5) Токен `MkKGpwCAsq6IF3RtRH7bvg`** — `secrets.token_urlsafe(16)` в `webapp.db.access_tokens` (level='white'); используется как `?token=…` в URL, подставляется в кнопку Mini App из `bot-dev/handlers/menu.py:89` и `bot-max/handlers/menu.py:89`.

**Состояние БД на момент аудита:**
- PROD `/opt/bot/properties.db` (mtime May 8 03:00): 234+102+111=447 lots, **В225 отсутствует**.
- DEV `/opt/bot-dev/properties.db` (mtime May 7 16:55): 248+103+118=469 lots, **В225 присутствует** — DEV-парсер закомментирован в cron, БД отстаёт.

**Что не сделано (вынесено в BACKLOG как P0/P1):**
- WebApp `CUSTOM_INSTALLMENT_UNITS` рассинхронизирован с bot-PROD на 4 кода + А101-аномалия + отсутствие проверки `building==1` (Грозит: лоты с кодами из bot-листа, которых нет в webapp-листе, продолжают получать 18-мес рассрочку через webapp). По плану: синхронизировать на единый источник истины (вынести в `data/installment_config.json` либо импортировать из bot).

**Файлы:** ничего не менял.

**Версия:** 2.7.2

---

## 05.05.2026 — Ставки траншевой ипотеки (DEV+PROD) + сводное КП на этаж К3-2 (one-shot)

**Сделано:**

**1) Обновление ставок траншевой ипотеки Сбербанк** (только 4 числа в `data/tranche_mortgage_config.json`, поля `pct`/`tranche_amounts`/`term_months`/`tranche_period_months` не тронуты):
- 20.1: 21.7 → **21.2**
- 30.1: 21.2 → **19.7**
- 40.1: 21.2 → **19.7**
- 50.1: 19.2 → **19.0**
- DEV-коммит `ae9a280`, рестарт `rizalta-bot-dev` ✓
- PROD: бэкап `data/tranche_mortgage_config.json.bak.20260505-072028`, коммит `5d9728c` в `git@github.com:semiekhin/rizalta-bot.git`, рестарт `rizalta-bot` ✓

**2) Сводное КП на этаж — one-shot для К3, 2 этаж (36 лотов):**
- Источник: PROD-БД через `sqlite3.connect("file:/opt/bot/properties.db?mode=ro", uri=True)` (read-only URI)
- Сравнение DEV vs PROD по К3-2 — наборы кодов идентичны (36 лотов, 1138.6 м², 751 009 500 ₽). DEV-парсер не запускается с 30.04, известное состояние.
- Готовый PDF: `/tmp/КП_К3_2этаж_сводное.pdf` (2.1 МБ, 7 страниц A4 portrait, копия в `/opt/bot-dev/scripts/`)
- Стиль матчит `services/kp_pdf_generator.py`: тёмно-зелёная шапка #313D20 + золотая плашка #DCB764 + белые карточки на светлом фоне #F6F0E3, шрифт Montserrat (base64 из `services/kp_resources/`)
- Layout: HTML-`<table>` + `float` (НЕ CSS Grid — wkhtmltopdf 0.12.6/Qt 5.15.13 рендерит каждый ряд Grid на отдельной странице, у первой версии получилось 13 страниц вместо 7)
- Скрипт `/opt/bot-dev/scripts/generate_floor_kp.py` — **untracked, временный**, не закоммичен. Виртуальные лоты в БД не вставлялись.

**3) Диагностика памяти PROD** (по запросу): RAM 7.8G total / used 2.3G / available 5.5G; swap 311M; load 0.12; OOM в dmesg/journal — пусто; диск 36% used. Норма.

**Файлы (committed):** `data/tranche_mortgage_config.json` (DEV+PROD).

**Untracked в DEV (артефакты сессии):**
- `scripts/generate_floor_kp.py` — one-shot скрипт сводного КП
- `scripts/КП_К3_2этаж_сводное.pdf` — финальный результат
- `scripts/КП_К3_2этаж_36лотов.pdf` — старая версия (CSS Grid, 13 страниц, негодная)
- `scripts/test_single_kp_А200.pdf` — эталон одиночного КП для сравнения стиля
- `scripts/kp_resources_copy/` — копия ресурсов для выгрузки на Mac
- `properties.db.bak.20260430-111725` — с прошлой сессии (P3 в backlog)

**Уроки:**
- Для wkhtmltopdf 0.12.6 + Qt 5.15.13: **CSS Grid не использовать**, только `<table>` + `float` + `overflow:hidden` для очистки. Эталон вёрстки — `services/kp_pdf_generator.py`.
- Перед генерацией одноразовых артефактов сверять `building`/`floor` в DEV vs PROD — DEV-парсер закомментирован, PROD-БД авторитетна.

**Версия:** 2.7.2

---

## 30.04.2026 — Лот В717 в custom installment + фиксация ручных PROD-правок в git

**Сделано:**
- **Разведка В317/В307:** парсер на PROD отработал штатно (mtime 03:00, 451 запись, лог без ошибок). В307 уже снят парсером — на ri.rclick.ru его нет. В317 остался `available` — рассинхрон между внутренней CRM застройщика и публичным каталогом ri.rclick.ru (гипотеза «b»).
- **DEV:** добавлен `'В717'` в `CUSTOM_INSTALLMENT_UNITS` (коммит `be1469d`). Точечный INSERT записи В717 в `properties.db` из PROD — DEV-парсер закомментирован в cron, БД отставала с 11.04. Бэкап `properties.db.bak.20260430-111725`. Рестарт `rizalta-bot-dev` ✓.
- **PROD:** В717 добавлен через sed (точечная замена `'В625']` → `'В625', 'В717']`), бэкап `kp_pdf_generator.py.bak.20260430-112929`. Рестарт `rizalta-bot` ✓, в логах сразу прошла генерация КП по В717 в новом сценарии.
- **Аудит /opt/bot:** найдено 5 modified + 1 untracked в working tree — хвосты ручных деплоев. Все диффы прочитаны и квалифицированы.
- **Коммиты в /opt/bot (4 шт):**
  - `353e898 fix(rclick)` — RCLICK-фикс 20.04 (rclick_service, booking_fixation, send_rclick_update_notification)
  - `0c6eed5 feat(watchdog)` — мониторинг rizalta-bot-max (health_check, watchdog/config)
  - `ec87671 feat: В717` — синхронизация PROD-кода с DEV-коммитом `be1469d`
  - `62a5a90 fix(units_db)` — снят `AND status='available'` в 3 SQL-запросах (осознанно, готовимся к статусу 'бронь')
- **Push:** `bc6666f..62a5a90 main -> main` в `git@github.com:semiekhin/rizalta-bot.git` ✓

**Файлы:** services/kp_pdf_generator.py (DEV+PROD), properties.db (DEV INSERT). На PROD дополнительно: services/rclick_service.py, handlers/booking_fixation.py, send_rclick_update_notification.py, health_check.sh, services/watchdog/config.py, services/units_db.py.

**Незакрытое (для следующей сессии):**
- `/opt/bot/services/kp_pdf_generator.py.bak.20260430-112929` и `/opt/bot-dev/properties.db.bak.20260430-111725` — cp-бэкапы остались untracked. После стабильного периода унести в `/var/backups/` или удалить.
- В317 на ri.rclick.ru — попросить застройщика/менеджеров обновить статус в их CRM, чтобы парсер увидел и снял лот штатно.
- DEV-парсер закомментирован → DEV БД отстаёт от PROD на 19+ дней. Не критично, известное состояние, при необходимости — раскомментировать cron `/opt/bot-dev` 06:00.

**Версия:** 2.7.2

---

## 20.04.2026 — Фикс фиксации через RCLICK + авто-релогин с зашифрованным паролем (деплой в PROD)

**Проблема:** с ~17:12 MSK все фиксации через ri.rclick.ru падали с криптичным "Ошибка подключения: Expecting value: line 1 column 1 (char 0)". RCLICK начал возвращать HTTP 500 с пустым телом на `POST /notice/newbooking/`.

**Диагностика (через поэтапное добавление логов в DEV):**
- RCLICK /notice/newbooking/ требует `multipart/form-data` (не url-encoded), браузерные заголовки (User-Agent/Origin/Referer), и ВАЛИДНУЮ PHP-сессию на их бэке привязанную к agent через PHPSESSID
- Login отдаёт ДВЕ куки: `rClick_token` + `PHPSESSID`, обе нужны. Старый код сохранял только `rClick_token`
- Успех curl'а с браузерными куками vs 500 с токеном-only из БД подтвердил гипотезу

**Решение (3 стейджа, stage 3 коммитов):**
- `fcd1b92` stage 1 — миграция БД (ALTER TABLE: `encrypted_password`, `phpsessid`, `session_refreshed_at`) + Fernet helpers
- `c69f487` stage 2 — `login_rclick()` через `requests.Session`, `_do_rclick_booking()`, `_is_dead_session()`, `_attempt_relogin()` с rate-limit 30 сек, `create_booking_for_user(telegram_id, ...)` с детектором + 1 повтором
- `95aa1fb` stage 3 — handler переведён на `create_booking_for_user` + `save_auth_after_login` (handler не знает про Fernet), новая кнопка «🔑 Авторизоваться заново» при `reauth_required=True`

**Деплой в PROD (23:04 MSK):**
- Бэкап в `/root/rizalta-prod-backup-20260420-230141/`
- `cryptography==41.0.7` в /opt/bot/venv
- Сгенерирован и добавлен в `/opt/bot/.env` отдельный `RCLICK_ENCRYPTION_KEY` (44 chars, бэкап в менеджере паролей у человека)
- Миграция БД: 40 записей целы, новые поля NULL — каждый риэлтор один раз получит «Сессия истекла, авторизуйтесь заново» → после этого работает прозрачно с авто-релогином

**Тесты в DEV (прошли):** новый юзер (#3), авто-релогин при мёртвом токене (#4), обратная совместимость с NULL encrypted_password (#5), повреждённый шифротекст (#6), rate-limit (unit-test в stage 2)

**Файлы:** services/rclick_service.py, handlers/booking_fixation.py, .env.example (+ .env с ключом)

**Версия:** 2.7.2

---

## 12.04.2026 — Срок сдачи К3: 2 кв. 2028 + деплой в PROD

**Сделано:**
- **Срок сдачи К3 = 2 кв. 2028:** условие по building в `kp_pdf_generator.py`, обновлён `corp3.py`, `rizalta_finance.json` (поле `completion_by_building`), `ai_chat.py` с группировкой корпусов
- **Деплой в PROD:** коммит `bc6666f`, бонусом уехал давно ждавший фикс `data:image` в `kp_pdf_generator.py`
- **Подключение:** Claude Code теперь работает на сервере через `root` (не `claude-dev`)
- **Контекст:** создана система CLAUDE.md + SESSION_LOG.md + BACKLOG.md по стандарту Sofia
- **mortgage_config.json:** закоммичен висевший с 31.03 hotfix — `markup_pct` обнулён для всех ПВ (30/40/50: 6/9/12 → 0/0/0), удорожания больше нет

**Файлы:** services/kp_pdf_generator.py, handlers/corp3.py, data/rizalta_finance.json, services/ai_chat.py, data/mortgage_config.json, CLAUDE.md, SESSION_LOG.md, BACKLOG.md

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

## Предыдущие сессии → docs/RIZALTA_CURRENT.md
