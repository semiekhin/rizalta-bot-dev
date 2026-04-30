# SESSION_LOG — Последние сессии

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
