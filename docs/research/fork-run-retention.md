# R&D: Срок хранения запусков, переписки и истории задачи в таблицах форка

← [Все R&D](README.md) · методология R&D v3.1 · компонент: **[ICPlan](../architecture/components/icplan/README.md), [Memory](../architecture/components/memory/README.md), [Observability](../architecture/components/observability/README.md)** · решение: [design AD-25](..\source\design\define-agent-platform\design.md) · вопрос: ОВ-icplan-integration-1, [Z-ICP-16](..\architecture\components\icplan\docs\findings.md)

<div class="rnd-hero" markdown>
<div class="rnd-q">Вопрос</div>
Платформа на каждый запуск пишет в таблицы форка `agent_run`, `agent_chat_message`, `issue_activity`. Форк чистит их только каскадом. Память читает те же строки: M1 — переписку, M2 — итоги запусков, со сроками `retention` (M1 30 д, M2 180 д). Сколько хранить эти строки и кто их удаляет?

<div class="rnd-a">Ответ: разделить срок памяти и срок хранения. [Memory](../architecture/components/memory/README.md) API применяет `retention` как фильтр чтения и не удаляет чужие строки. Запуски и треды чата удаляет владелец, [ICPlan](../architecture/components/icplan/README.md), задачей worker форка по своим срокам: не меньше верхних границ памяти (запуски ≥ 365 д, чат ≥ 90 д). История задачи по времени не чистится.</div>

<span class="rnd-badge adopt">Adopt</span> срок памяти — фильтр чтения, срок хранения — у [ICPlan](../architecture/components/icplan/README.md) · 0 $ · данные 12.10.2026
</div>

```deck
# Покрытие потребностей П1–П7
> раздельные сроки закрывают всё, кроме одной задачи в worker форка
stack C. Срок памяти — фильтр, хранение — ICPlan: 6 ok, 1 part, 0 no
stack B. ICPlan чистит по срокам памяти: 4 ok, 3 part, 0 no
stack 0. Как сейчас (без очистки): 5 ok, 0 part, 2 no
# Объём доработки
> две подзадачи, 7 ч: очистка worker'ом ICPlan и фильтр чтения памяти
bar Очистка worker'ом ICPlan: 4/7 4.7.7 — 4 ч ok
bar Фильтр чтения M1, M2: 3/7 2.5.9 — 3 ч ok
# Позиции ролей
side Раздельные сроки | Чистить по срокам памяти
pos Архитектор: -2 | удаляет владелец таблицы, Memory — только SELECT
pos Владелец продукта: -1 | статистика и история запусков не зависят от профиля агента
pos Разработчик Memory: -1 | нет прав на удаление в `public`
pos DevOps: 0 | рост таблиц ограничен; одна задача в worker
pos Безопасность (оппонент): 1 | переписка лежит дольше срока памяти
# Что меняется
> AD-25; FR-43 для M1 и M2; параметры очистки ICPlan; `POST /retention/run` — только своё
stack Документы: 10 ok, 0 part, 0 mute
```

<div class="rnd-grid" markdown>
<div class="take" markdown>
**Берём**

- `retention` памяти — фильтр чтения [Memory](../architecture/components/memory/README.md) API (`GET /context`): M1 и M2 старше срока профиля не отдаются ([FR-43](../architecture/components/memory/prd.md), «запись недоступна для чтения»);
- очистку [ICPlan](../architecture/components/icplan/README.md) по образцу очистки доставок вебхуков в worker форка;
- `issue_activity` — без очистки по времени: журнал задачи живёт с задачей.
</div>
<div class="adapt" markdown>
**Адаптируем**

- `runs.retention_days` (по `finished_at`, только завершённые) ≥ 365 — верхняя граница M2 и `retention_days` событий;
- `chat.retention_days` (тред целиком по `updated_at`) ≥ 90 — верхняя граница M1;
- `POST /retention/run` [Memory](../architecture/components/memory/README.md) API удаляет только своё: M3, позже M4.
</div>
<div class="drop" markdown>
**Не берём**

- удаление строк форка силами [Memory](../architecture/components/memory/README.md) API — запись в чужую схему ([AD-22](../architecture/decisions/AD-22.yaml));
- очистку `agent_run` по M2 профиля агента — история и статистика зависят от профиля памяти, от 30 д.
</div>
</div>

<div class="rnd-grid" markdown>
<div class="no" markdown>
**Отсеяны до сравнения**

- [Memory](../architecture/components/memory/README.md) API удаляет M1 и M2 в таблицах форка — нужен `DELETE` в `public` (против [AD-22](../architecture/decisions/AD-22.yaml)), а M1 удалил бы комментарии людей из задачи;
- удаление при закрытии задачи — против [FR-43](../architecture/components/memory/prd.md) («M2 остаётся»);
- секционирование `agent_run` по времени — меняет схему таблицы форка; это способ ускорить очистку, а не срок.
</div>
<div class="risk" markdown>
**Риски и пересмотр**

- переписка лежит дольше срока M1 профиля — если требования к персональным данным строже, снижают оба срока: M1 в профилях и `chat.retention_days`;
- пересмотр сроков — по объёму БД (нагрузочный тест 4.8) и статистике (3.9).
</div>
</div>

## Э1. Вопрос {#e1}

**Ситуация.** Таблицы форка, в которые пишет платформа (`datamodel.FORK_WRITTEN`):

- `agent_run` — запуски, это M2 ([AD-18](../architecture/decisions/AD-18.yaml) «Запись M2»);
- `agent_chat_message` — чат с агентом, это M1;
- `issue_activity` — комментарии (M1) и записи «агент взял / закончил» (`run-activity.ts` форка).

Форк удаляет их только каскадом: с агентом, проектом, задачей, тредом (`packages/db/src/schema/app.ts`). Worker форка по времени чистит только успешные доставки вебхуков: `cleanupOldDeliveries`, `WEBHOOK_CLEANUP_DAYS` = 30 (`apps/worker/src/config.ts`, `store.ts`). Сроки памяти — параметр `retention` профиля памяти (L1, S2): M1 30 д (7–90), M2 180 д (30–365) (`agent-memory/interfaces.md`).

**Осложнение.** [FR-43](../architecture/components/memory/prd.md): «записи M1–M4 MUST удаляться по истечении срока». `POST /retention/run` [Memory](../architecture/components/memory/README.md) API возвращает `{deleted: {m1, m2, m3}}`. Но у роли `memory` на `agent_run` и `agent_chat_message` только `SELECT` (`DB_GRANTS`, [AD-22](../architecture/decisions/AD-22.yaml)). Те же строки — это история запусков ([US-ICP-28](../architecture/components/icplan/stories/us-icp-28.yaml)), статистика ([FR-152](../architecture/components/observability/prd.md)) и журнал задачи.

**Вопрос.** Какой срок хранения у этих таблиц и кто удаляет строки?

**Решает:** архитектор (ОВ-icplan-integration-1). **Не решаем:** значения `retention` памяти, срок событий `run_event` (`retention_days`), бэкап ([FR-165](../architecture/components/infrastructure/prd.md)).

<span class="gate">G1</span> ✅ вопрос — выбор правила хранения; владелец и связь с ОВ-icplan-integration-1, [FR-43](../architecture/components/memory/prd.md) названы.

## Э2. Потребности {#e2}

| # | Потребность | Источник | Без неё |
|---|---|---|---|
| П1 | [Memory](../architecture/components/memory/README.md) не отдаёт M1 и M2 старше срока профиля | [FR-43](../architecture/components/memory/prd.md), `retention` | агент читает переписку дольше срока |
| П2 | история задачи (комментарии, «агент взял / закончил», переходы) живёт, пока жива задача | блок Автоподхват («пишет в историю»), `run-activity.ts`, `TABLE_POLICY` | из задачи пропадают комментарии людей |
| П3 | история запусков и статистика за период | [FR-152](../architecture/components/observability/prd.md) («с фильтром по … периоду»), [US-ICP-28](../architecture/components/icplan/stories/us-icp-28.yaml), `GET /issues/:issueId/agent-feed` | статистика агента за месяц неполна |
| П4 | строки удаляет владелец таблицы | [AD-22](../architecture/decisions/AD-22.yaml) («писать в чужую схему — ошибка границы»), `DB_GRANTS` | [Memory](../architecture/components/memory/README.md) получает `DELETE` в `public` |
| П5 | таблицы, в которые платформа пишет на каждый запуск, не растут без предела | ОВ-icplan-integration-1, `FORK_WRITTEN` | рост БД без ограничения |
| П6 | удаление не ломает ссылки на `agent_run` | `run_event`, `run_checkpoint`, `agent_run_delivery`, `scheduler_slot` (`PLATFORM_TABLES`) | очистка падает на внешнем ключе |
| П7 | мало правок кода форка | [AD-18](../architecture/decisions/AD-18.yaml) «слияние с upstream» | конфликты при обновлении |

<span class="gate">G2</span> ✅ у потребностей есть источник и цена отсутствия.

## Э3. Опорное решение: как сейчас {#e3}

| Функция | Что делает | Потребность | Факт |
|---|---|---|---|
| каскадное удаление | `agent_run` — с агентом, проектом, задачей, расписанием; `agent_chat_message` — с тредом и агентом; `issue_activity` — с задачей | П2, П6 | `app.ts` (Б, код) |
| очистки по времени нет | — | П5 не закрыта | `apps/worker/src/config.ts` — только вебхуки (Б, код) |
| [Memory](../architecture/components/memory/README.md) читает `agent_run`, `agent_chat_message` | `SELECT`; фильтра по сроку в описании нет | П1 не закрыта | `DB_GRANTS`, `GET /context` (`ENDPOINT_IO`) |
| `POST /retention/run` удаляет m1, m2 | прав на удаление нет | П4 нарушена | `ENDPOINT_IO`, `DB_GRANTS` |
| удаление треда форка | удаляет тред, сообщения и события каскадом, `agent_chat_usage` — кодом | П6 | `chat/service.ts` `deleteThread`, `chat-usage.ts` (Б, код) |

**Вывод этапа.** Сейчас ничего не теряется, но таблицы растут, а [FR-43](../architecture/components/memory/prd.md) для M1 и M2 описан через удаление, на которое ==у [Memory](../architecture/components/memory/README.md) нет прав==.

<span class="gate">G3</span> ✅ функции связаны с потребностями, наличие подтверждено кодом.

## Э4. Альтернативы и их ключевые функции {#e4}

Поиск — по коду форка (`packages/db`, `apps/worker`, `apps/api/src/modules/agents`), спекам agent-memory, observability, icplan-integration и `datamodel.py`, 12.10.2026.

| Вариант | Ключевая функция |
|---|---|
| 0. Как сейчас | только каскад |
| A. [Memory](../architecture/components/memory/README.md) API чистит по `retention` | `POST /retention/run` удаляет M1 (чат и комментарии) и M2 (`agent_run`) |
| B. [ICPlan](../architecture/components/icplan/README.md) чистит по `retention` памяти | worker удаляет чат по M1 и запуски по M2 профиля агента; история задачи не чистится |
| C. Раздельные сроки | `retention` — фильтр чтения [Memory](../architecture/components/memory/README.md); worker [ICPlan](../architecture/components/icplan/README.md) удаляет запуски и треды по своим срокам не меньше границ памяти; история задачи не чистится |
| D. Удаление при закрытии задачи | как M3: запуски и чат задачи — при закрытии |
| E. Секционирование по времени | `agent_run` — секции по месяцам, удаление секцией (как этап 4 у `run_event`, `TABLE_POLICY`) |

<span class="gate">G4</span> ✅ 6 кандидатов; «как сейчас» и «сделать самим» в списке; источники — код форка, спеки, модель данных.

## Э5. Ценность функций {#e5}

| Функция | Потребность | Почему ценна | Доказательство | Класс |
|---|---|---|---|---|
| удаление владельцем таблицы | П4 | права по схеме не расширяются | [AD-22](../architecture/decisions/AD-22.yaml) | базовая |
| журнал задачи живёт с задачей | П2 | комментарии людей — содержимое задачи | `issue_activity` — комментарии и активность (`app.ts`) | базовая |
| срок памяти как фильтр чтения | П1 | агент не видит старое, строки не трогаются | [FR-43](../architecture/components/memory/prd.md) «запись недоступна для чтения» | линейная |
| срок хранения ≥ верхних границ памяти и событий | П3, П6 | ни один профиль не требует строк дольше хранения; ссылки событий уходят раньше | границы `retention` (M1 90, M2 365), `retention_days` (365) | линейная |
| очистка по образцу вебхуков | П5, П7 | готовый образец в worker форка | `cleanupOldDeliveries` (Б, код) | линейная |
| срок запусков по профилю агента | — | история агента зависит от профиля памяти | M2 от 30 д | обратная |

<span class="gate">G5</span> ✅ ценность берущихся функций подтверждена кодом, решениями и спеками (Б).

## Э6. Перенос и критерии {#e6}

| Функция | Решение | Причина |
|---|---|---|
| удаление владельцем | брать | MUST (П4) |
| журнал задачи без очистки | брать | MUST (П2) |
| фильтр чтения [Memory](../architecture/components/memory/README.md) | брать | П1 без прав на удаление |
| нижние границы сроков [ICPlan](../architecture/components/icplan/README.md) | адаптировать | из границ `retention` и `retention_days`; по умолчанию — сами границы |
| очистка по образцу вебхуков | брать | П7 |
| срок запусков по профилю | не брать | обратная функция |

**MUST:** П2, П4. **Критерии:** П1, П3, П5, П6, П7.

<span class="gate">G6</span> ✅ у функций решение и причина; критерии из линейных функций.

## Э7. Отсев и встраивание {#e7}

| Кандидат | П2 журнал задачи | П4 удаляет владелец | Итог |
|---|---|---|---|
| A. [Memory](../architecture/components/memory/README.md) API чистит | нет: M1 — комментарии задачи | нет: `DELETE` в `public` | отсеян |
| D. При закрытии задачи | да | да | отсеян: против [FR-43](../architecture/components/memory/prd.md) («M2 остаётся») |
| E. Секционирование | да | да | отсеян: меняет схему таблицы форка ([AD-18](../architecture/decisions/AD-18.yaml)); способ очистки, а не срок |

| Кандидат | I-коды и стыки | Кто удаляет | Данные | Изменения у соседей | Готовность |
|---|---|---|---|---|---|
| B. [ICPlan](../architecture/components/icplan/README.md) по срокам памяти | [I22](../architecture/integrations/I22.yaml) (БД); worker читает `memory_profile.retention` из `platform` | [ICPlan](../architecture/components/icplan/README.md) (worker форка) | `agent_run`, `agent_chat_thread` | [Memory](../architecture/components/memory/README.md): `POST /retention/run` — только M3 | И2: образец есть в форке, задачи нет |
| C. Раздельные сроки | [I22](../architecture/integrations/I22.yaml); [I11](../architecture/components/harness/integrations/I11.yaml) и `GET /context` — фильтр по сроку | [ICPlan](../architecture/components/icplan/README.md) (worker форка) по L0-параметрам | `agent_run` (завершённые, по `finished_at`), `agent_chat_thread` → сообщения и события каскадом | [Memory](../architecture/components/memory/README.md): фильтр чтения, `POST /retention/run` — M3; [Observability](../architecture/components/observability/README.md): события уходят раньше запусков | И2 |

**Вывод этапа.** B и C удаляют силами владельца. B связывает очистку [ICPlan](../architecture/components/icplan/README.md) с профилями [Memory](../architecture/components/memory/README.md) (worker читает схему `platform`), а срок `agent_run` получается от 30 д — меньше 90 д событий, которые ссылаются на запуск. ==C не связывает модули==: память фильтрует, [ICPlan](../architecture/components/icplan/README.md) хранит не меньше, чем может попросить любой профиль.

<span class="gate">G7</span> ✅ у прошедших есть строка встраивания; изменения у соседей названы.

## Э8. Спор ролей {#e8}

Роли 🤖. Оппонент — Безопасность, она защищает B («удалять переписку ровно по M1»). «Адвокат дьявола» атакует C.

| Роль | За | Довод | Опасение | Согласится, если |
|---|---|---|---|---|
| Архитектор 🤖 | C | удаляет владелец, модули не связаны ([AD-22](../architecture/decisions/AD-22.yaml)) | — | — |
| Владелец продукта 🤖 | C | статистика за месяц и история запусков не зависят от профиля памяти ([FR-152](../architecture/components/observability/prd.md)) | — | — |
| Разработчик [Memory](../architecture/components/memory/README.md) 🤖 | C | только `SELECT`, фильтр по времени в запросе | — | — |
| DevOps 🤖 | C | рост ограничен, параметры как у вебхуков | ещё одна задача worker | отдельный файл задачи в модуле доработок форка |
| Безопасность 🤖 (оппонент) | B | переписка не хранится дольше M1 | персональные данные в чате 90 д | можно снизить `chat.retention_days` вместе с M1 профилей |

| Спор | Разрешение |
|---|---|
| Безопасность: «переписка лежит дольше M1» | **условие:** нижняя граница `chat.retention_days` — 90 д, верхняя граница M1. Если требования к персональным данным строже, снижают M1 в профилях и `chat.retention_days` вместе; в `agent-memory/interfaces.md` это основание выбора уже названо |
| Адвокат дьявола: «[FR-43](../architecture/components/memory/prd.md) требует удалять, а C только фильтрует» | **требование:** уточнить [FR-43](../architecture/components/memory/prd.md) — для M1 и M2 в таблицах форка срок означает «[Memory](../architecture/components/memory/README.md) не отдаёт», строки удаляет [ICPlan](../architecture/components/icplan/README.md) по своему сроку |
| Адвокат дьявола: «очистка запусков упадёт на ссылках `run_event`» | **условие:** `runs.retention_days` ≥ `retention_days` событий; при равных сроках worker пропускает запуски, у которых ещё есть `run_event` (та же роль `itsaplan`); `run_checkpoint` живёт 7 д |
| DevOps: «задача в worker форка — правка форка» | **условие:** по образцу `cleanupOldDeliveries`, параметры через env, как `WEBHOOK_CLEANUP_DAYS` |

<span class="gate">G8</span> ✅ у каждого спора есть разрешение.

## Э9. Выбор {#e9}

| Потребность | 0. Как сейчас | B. [ICPlan](../architecture/components/icplan/README.md) по срокам памяти | C. Раздельные сроки |
|---|---|---|---|
| П1 [Memory](../architecture/components/memory/README.md) не отдаёт старое | не закрывает | закрывает: строк нет | закрывает: фильтр чтения |
| П2 журнал задачи | закрывает | закрывает | закрывает |
| П3 история и статистика | закрывает | частично: срок по профилю агента, от 30 д | закрывает: ≥ 365 д |
| П4 удаляет владелец | закрывает | закрывает | закрывает |
| П5 рост ограничен | не закрывает | закрывает | закрывает |
| П6 ссылки | закрывает | частично: M2 от 30 д < 90 д событий | закрывает: граница ≥ `retention_days` |
| П7 правки форка | закрывает | частично: задача worker и чтение `platform` | частично: задача worker |

- **Утверждение.** Раздельные сроки ([AD-25](../architecture/decisions/AD-25.yaml)).
- **Основания.** Удалять в `public` может только владелец ([AD-22](../architecture/decisions/AD-22.yaml)). [Memory](../architecture/components/memory/README.md) удовлетворяет [FR-43](../architecture/components/memory/prd.md) фильтром («запись недоступна для чтения»). У worker форка уже есть образец очистки по времени.
- **Связка.** Хранение не короче любого срока памяти и событий, поэтому память, статистика и ссылки не теряют строк. Журнал задачи остаётся содержимым задачи.
- **Оговорка.** Пока сроки памяти не превышают границ параметра `retention` (M1 90, M2 365).
- **Когда неверно.** Если требования к персональным данным запретят хранить переписку дольше M1 — тогда `chat.retention_days` = M1 профиля, и очистку чата связывают с профилями (B для чата). Если поднимут верхние границы `retention` или `retention_days`, поднимают и нижние границы [ICPlan](../architecture/components/icplan/README.md).

<span class="gate">G9</span> ✅ вывод следует из покрытия и спора; есть условие пересмотра.

## Э10. Последствия {#e10}

Изменения вносит основной агент по процессу изменений.

| Изменение | Документ | Статус |
|---|---|---|
| Решение [AD-25](../architecture/decisions/AD-25.yaml): срок памяти — фильтр чтения; запуски и треды удаляет [ICPlan](../architecture/components/icplan/README.md) по `runs.retention_days` ≥ 365 и `chat.retention_days` ≥ 90; `issue_activity` — без очистки по времени | [design](..\source\design\define-agent-platform\design.md) | ✅ внесено |
| ОВ-icplan-integration-1 закрыт ссылкой на [AD-25](../architecture/decisions/AD-25.yaml) | `icplan-integration/open-questions.md` | ✅ внесено |
| Параметры `runs.retention_days`, `chat.retention_days` (L0, границы, 0 — не чистить) и требование очистки | `icplan-integration/interfaces.md`, spec icplan-integration | ✅ внесено |
| [FR-43](../architecture/components/memory/prd.md): для M1 и M2 — «[Memory](../architecture/components/memory/README.md) не отдаёт записи старше срока; строки удаляет [ICPlan](../architecture/components/icplan/README.md)» | spec agent-memory | ✅ внесено |
| `POST /retention/run` → `{deleted: {m3}}` (M4 — после MVP) | `datamodel.ENDPOINT_IO`, API [Memory](../architecture/components/memory/README.md) | ✅ внесено |
| `TABLE_POLICY` `agent_run`, `agent_chat_message`, `issue_activity`: срок и очистка по [AD-25](../architecture/decisions/AD-25.yaml) вместо «срок открыт» | `html-view/datamodel.py` | ✅ внесено |
| Расхождение: `ICPLAN_TABLES` [Memory](../architecture/components/memory/README.md) читает `issue_activity` (M1, M2), а `DB_GRANTS` не даёт `SELECT` | `datamodel.DB_GRANTS` | ✅ внесено |
| Переменные очистки worker в Deploy [ICPlan](../architecture/components/icplan/README.md) | [техспека ICPlan](..\architecture\components\icplan\docs\techspec.md) | ✅ внесено |
| Задачи: фильтр чтения M1 и M2 — 2.5; очистка worker — 4.7 | [2.5](..\source\tasks\2.5-memory-m2-m3.md), [4.7](..\source\tasks\4.7-postgres-storage-backup.md) | ✅ внесено |
| Z-ICP-16 → решено [AD-25](../architecture/decisions/AD-25.yaml) | [замечания ICPlan](..\architecture\components\icplan\docs\findings.md) | ✅ внесено |

<span class="gate">G10</span> ✅ у каждого изменения есть документ и статус.

## Источники

Чтение — 12.10.2026; в скобках уровень доказательства.

- Код форка `локальный путь` (А, прочитан): `packages/db/src/schema/app.ts` (`agent_run`, `agent_chat_thread`, `agent_chat_message`, `agent_chat_event`, `agent_chat_usage`, `issue_activity`); `apps/worker/src/config.ts`, `store.ts` (`cleanupOldDeliveries`); `apps/api/src/modules/agents/core/run-activity.ts`, `chat/service.ts`, `chat-usage.ts`
- [design](..\source\design\define-agent-platform\design.md): [AD-18](../architecture/decisions/AD-18.yaml) («Запись M2»), [AD-22](../architecture/decisions/AD-22.yaml)
- Спеки: agent-memory [FR-43](../architecture/components/memory/prd.md), `interfaces.md` (`retention`); observability [FR-152](../architecture/components/observability/prd.md), `interfaces.md` (`retention_days`); icplan-integration `open-questions.md`
- `html-view/datamodel.py`: `FORK_WRITTEN`, `TABLE_POLICY`, `DB_GRANTS`, `ICPLAN_TABLES`, `PLATFORM_TABLES`, `ENDPOINT_IO`
