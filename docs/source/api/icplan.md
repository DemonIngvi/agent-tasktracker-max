# Интеграции: ICPlan (форк)

← компонент · Deploy · методология

<div class="api-head">
<div><span class="about-label">Базовый адрес</span> `https://<домен>/api` (api ICPlan, порт 3000)</div>
<div><span class="about-label">Аутентификация</span> UI — сессия пользователя; агент и Runner — `Authorization: Bearer <ключ агента>`</div>
</div>

## Агенты

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-get">GET</span> | `/teams/:teamId/ai-agents` | <span class="st st-ok">✅ есть</span> | список агентов команды | Администратор (UI) · сессия | US-ICP-20 | FR-8 | I20 |
| <span class="m m-post">POST</span> | `/teams/:teamId/ai-agents` | <span class="st st-ok">✅ есть</span> | создать агента (kind `external` для платформы); ключ показывается один раз | Администратор · сессия | US-ICP-20 | FR-54, FR-1 | I20 |
| <span class="m m-patch">PATCH</span> | `/teams/:teamId/ai-agents/:agentId` | <span class="st st-fork">🛠 доработка форка</span> | изменить модель, инструкцию, триггеры; доработка — выключить / включить агента и судьба активных запусков (`enabled`, `onDisable`: `finish` / `cancel`) | Администратор · сессия | US-ICP-21, US-ICP-22 | FR-55, FR-11 | I20 |
| <span class="m m-del">DELETE</span> | `/teams/:teamId/ai-agents/:agentId` | <span class="st st-ok">✅ есть</span> | удалить агента; шаги процессов становятся ручными | Администратор · сессия | US-ICP-23 | FR-195 | I20 |
| <span class="m m-put">PUT</span> | `/teams/:teamId/ai-agents/:agentId/projects` | <span class="st st-ok">✅ есть</span> | проекты агента | Администратор · сессия | US-ICP-20 | FR-54 | I20 |
| <span class="m m-put">PUT</span> | `/teams/:teamId/ai-agents/:agentId/skills` | <span class="st st-ok">✅ есть</span> | навыки агента (M5) | Администратор · сессия | US-MCP-04 | FR-181 | I20 |
| <span class="m m-put">PUT</span> | `/teams/:teamId/ai-agents/:agentId/tool-configs` | <span class="st st-ok">✅ есть</span> | тулы агента | Администратор · сессия | US-MCP-01 | FR-177 | I20 |
| <span class="m m-post">POST</span> | `/teams/:teamId/ai-agents/:agentId/regenerate-key` | <span class="st st-ok">✅ есть</span> | перевыпустить ключ агента (Runner) | Администратор / безопасность · сессия | US-INF-07 | FR-166 | I20 |
| <span class="m m-get">GET</span> | `/teams/:teamId/ai-agents/:agentId/runs` | <span class="st st-ok">✅ есть</span> | запуски агента | Администратор · сессия | US-ICP-28 | FR-152 | I20 |

## Протокол раннера

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-post">POST</span> | `/agent-runs/claim` | <span class="st st-ok">✅ есть</span> | выдать следующий запуск агенту с арендой (`AGENT_RUN_LEASE_SECONDS`) | Agent Runner · ключ агента | US-ICP-07, US-RUN-01 | FR-2, FR-3, FR-198 | I1 |
| <span class="m m-post">POST</span> | `/agent-runs/:runId/heartbeat` | <span class="st st-fork">🛠 доработка форка</span> | продлить аренду; сейчас ответ 204 без тела, 404 — запуск не найден или уже завершён (отменён); доработка — ответ `Heartbeat`: решения по approve и указания пользователя; отмена — по-прежнему 404 (единственный сигнал) | Agent Runner · ключ агента | US-ICP-04, US-ICP-14, US-ICP-10, US-HAR-06 | FR-7, FR-10 | I3 |
| <span class="m m-post">POST</span> | `/agent-runs/:runId/events` | <span class="st st-new">🆕 новое</span> | события запуска для чата в задаче: `{events: RunEvent[]}` — события AG-UI, как у `POST /agent-chats/:messageId/events` (AD-21) | Agent Runner · ключ агента | US-ICP-02, US-OBS-01 | FR-4, FR-146 | I2 |
| <span class="m m-post">POST</span> | `/agent-runs/:runId/result` | <span class="st st-fork">🛠 доработка форка</span> | итог запуска: статус, вывод, токены (M2); доработка — причина, артефакты, проверка по критериям, критерии следующему шагу, стоимость | Agent Runner · ключ агента | US-ICP-01, US-MEM-02 | FR-4, FR-73, FR-197 | I2 |

## Чат с агентом

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-post">POST</span> | `/projects/:projectKey/ai-agents/:agentId/chat` | <span class="st st-ok">✅ есть</span> | сообщение агенту в чате (тред пользователь × агент) | Пользователь / администратор · сессия | US-ICP-10, US-ICP-24 | FR-12 | I20 |
| <span class="m m-get">GET</span> | `/projects/:projectKey/ai-agents/:agentId/chat/:messageId/stream` | <span class="st st-ok">✅ есть</span> | поток ответа агента | UI · сессия | US-ICP-10 | FR-12 | I20 |
| <span class="m m-post">POST</span> | `/projects/:projectKey/ai-agents/:agentId/chat/:messageId/cancel` | <span class="st st-ok">✅ есть</span> | остановить ответ в чате | Пользователь · сессия | US-ICP-04 | FR-7 | I20 |
| <span class="m m-get">GET</span> | `/projects/:projectKey/ai-agents/:agentId/threads` | <span class="st st-ok">✅ есть</span> | треды чата (M1) | Пользователь · сессия | US-MEM-06 | FR-38 | I20 |
| <span class="m m-post">POST</span> | `/agent-chats/claim` | <span class="st st-ok">✅ есть</span> | Runner забирает сообщение чата | Agent Runner · ключ агента | US-ICP-24 | FR-12 | I1 |
| <span class="m m-post">POST</span> | `/agent-chats/:messageId/events` | <span class="st st-ok">✅ есть</span> | шаги ответа в чате | Agent Runner · ключ агента | US-ICP-24 | FR-12 | I2 |
| <span class="m m-post">POST</span> | `/agent-chats/:messageId/result` | <span class="st st-ok">✅ есть</span> | итог ответа в чате | Agent Runner · ключ агента | US-ICP-24 | FR-12 | I2 |

## Задачи и поручение агенту

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-post">POST</span> | `/projects/:projectKey/issues` | <span class="st st-ok">✅ есть</span> | создать задачу (тип = процесс → первый шаг) | Пользователь, Telegram-бот, API · сессия / ключ | US-ICP-01 | FR-189, FR-204 | I20 |
| <span class="m m-patch">PATCH</span> | `/issues/:issueId` | <span class="st st-fork">🛠 доработка форка</span> | изменить задачу: колонка, делегат, исполнитель, приоритет; доработка — флаг `reviewWithMe` (проверять со мной все шаги) | Пользователь; агент (без смены колонки в процессе) · сессия / ключ | US-ICP-08, US-ICP-17, US-ICP-15 | FR-191, FR-204, FR-182, FR-199 | I20 |
| <span class="m m-post">POST</span> | `/issues/:issueId/comments` | <span class="st st-ok">✅ есть</span> | комментарий; `@агент` создаёт запуск | Пользователь, агент · сессия / ключ | US-ICP-09, US-ICP-11 | FR-204 | I20 |
| <span class="m m-get">GET</span> | `/issues/:issueId/checklists` | <span class="st st-ok">✅ есть</span> | чек-лист «Критерии приёмки» для quality gate | Harness (через MCP) · ключ агента | US-HAR-03 | FR-26 | I9 |
| <span class="m m-get">GET</span> | `/issues/:issueId/timeline` | <span class="st st-ok">✅ есть</span> | история задачи: подхваты, переходы, итоги | Пользователь · сессия | US-ICP-02 | FR-194 | I20 |
| <span class="m m-post">POST</span> | `/projects/:projectKey/ai-agents/:agentId/run` | <span class="st st-ok">✅ есть</span> | ручной запуск агента | Пользователь / администратор · сессия | US-ICP-24 | FR-12 | I20 |

## Ход задачи

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-get">GET</span> | `/agent-runs/:runId/stream` | <span class="st st-new">🆕 новое</span> | живой поток событий запуска (SSE, одно событие AG-UI в строке `data:`), как `…/chat/:messageId/stream` (AD-21) | Пользователь · сессия | US-ICP-02 | FR-147 | I20 |
| <span class="m m-get">GET</span> | `/issues/:issueId/agent-feed` | <span class="st st-new">🆕 новое</span> | история чата запусков задачи по шагам процесса: запуски, сохранённые события, итоги (AD-21) | Пользователь · сессия | US-ICP-02, US-OBS-01 | FR-147 | I20 |
| <span class="m m-post">POST</span> | `/issues/:issueId/agent-verdict` | <span class="st st-new">🆕 новое</span> | вердикт «принято / не выполнено» с заметкой | Исполнитель, владелец процесса · сессия | US-ICP-13 | FR-200 | I20 |
| <span class="m m-post">POST</span> | `/issues/:issueId/process/pause · /resume` | <span class="st st-new">🆕 новое</span> | остановить / возобновить процесс по задаче | Пользователь · сессия | US-ICP-14 | FR-201 | I20 |
| <span class="m m-post">POST</span> | `/issues/:issueId/process/retry` | <span class="st st-new">🆕 новое</span> | повторить шаг или начать с шага N (`fromStep`) | Пользователь, владелец процесса · сессия | US-ICP-16 | FR-202 | I20 |
| <span class="m m-get">GET</span> | `/issues/:issueId/agent-status` | <span class="st st-new">🆕 новое</span> | место в очереди и причина ожидания | Пользователь · сессия | US-ICP-18 | FR-198, FR-194 | I20 |
| <span class="m m-post">POST</span> | `/agent-runs/:runId/decisions` | <span class="st st-new">🆕 новое</span> | решение пользователя: approve, reject или ответ на вопрос (`ApprovalDecision`) | Task UI · сессия | US-ICP-11 | FR-5 | I20 |
| <span class="m m-post">POST</span> | `/agent-runs/:runId/messages` | <span class="st st-new">🆕 новое</span> | указание пользователя активному запуску (`UserMessage`) | Task UI · сессия | US-ICP-10 | FR-10 | I20 |
| <span class="m m-post">POST</span> | `/agent-runs/:runId/cancel` | <span class="st st-new">🆕 новое</span> | отменить запуск по задаче | Task UI · сессия | US-ICP-04 | FR-7 | I20 |
| <span class="m m-get">GET</span> | `/issues/:issueId/costs` | <span class="st st-new">🆕 новое</span> | затраты задачи по агентам (`CostAggregate`) | Task UI · сессия | US-ICP-12 | FR-150 | I20 |

Передать шаг другому агенту или человеку (US-ICP-17) — смена делегата или исполнителя `PATCH /issues/:issueId` (FR-191).

## Процессы и автоматизация

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-get">GET</span> | `/projects/:projectKey/processes` | <span class="st st-new">🆕 новое</span> | процессы проекта по типам задач | Администратор · сессия | US-ICP-05 | FR-196 | I20 |
| <span class="m m-put">PUT</span> | `/projects/:projectKey/processes/:issueTypeId` | <span class="st st-new">🆕 новое</span> | создать / изменить процесс (новая версия; перенос задач при удалении шага) | Администратор · сессия | US-ICP-05, US-ICP-25, US-ICP-26 | FR-196, FR-203, FR-188 | I20 |
| <span class="m m-post">POST</span> | `/projects/:projectKey/columns` | <span class="st st-ok">✅ есть</span> | колонка (шаг процесса) | Администратор · сессия | US-ICP-05 | FR-196 | I20 |
| <span class="m m-post">POST</span> | `/projects/:projectKey/issue-types` | <span class="st st-ok">✅ есть</span> | тип задачи (тип процесса) | Администратор · сессия | US-ICP-05 | FR-189 | I20 |
| <span class="m m-post">POST</span> | `/projects/:projectKey/actions` | <span class="st st-fork">🛠 доработка форка</span> | Действие: условие и эффект (частичная правка задачи); доработка — эффект «делегировать агенту» = ключ `delegateUserId` в `effect` | Администратор · сессия | US-ICP-27 | FR-190 | I20 |
| <span class="m m-post">POST</span> | `/projects/:projectKey/agent-schedules` | <span class="st st-ok">✅ есть</span> | расписание агента | Пользователь / администратор · сессия | US-ICP-19 | FR-204 | I20 |

## Сводка и статистика

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-get">GET</span> | `/projects/:projectKey/analytics/agent-run-stats` | <span class="st st-ok">✅ есть</span> | статистика запусков агентов | Администратор, владелец продукта · сессия | US-ICP-28, US-OBS-05 | FR-152 | I20 |
| <span class="m m-get">GET</span> | `/projects/:projectKey/analytics/agent-runs` | <span class="st st-ok">✅ есть</span> | запуски за период | Администратор · сессия | US-OBS-02 | FR-152 | I20 |
| <span class="m m-get">GET</span> | `/projects/:projectKey/analytics/agent-workload` | <span class="st st-ok">✅ есть</span> | загрузка агентов | Администратор · сессия | US-ICP-28 | FR-152 | I20 |
| <span class="m m-get">GET</span> | `/me/agent-summary` | <span class="st st-new">🆕 новое</span> | мои задачи с агентами: в работе, в очереди, ждут меня, время, токены и $ | Пользователь · сессия | US-ICP-12 | FR-152 | I20 |

## Уведомления, документы, MCP

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-get">GET</span> | `/notifications` | <span class="st st-ok">✅ есть</span> | уведомления: вопрос агента, итог, ошибка шага | Пользователь · сессия | US-ICP-03 | FR-6 | I20 |
| <span class="m m-get">GET</span> | `/projects/:projectKey/documents/:documentId` | <span class="st st-ok">✅ есть</span> | документ проекта (M6) | Агент через MCP · ключ агента | US-MEM-08 | FR-36 | I9 |
| <span class="m m-post">POST</span> | `/mcp` | <span class="st st-ok">✅ есть</span> | MCP `itsaplan-core`: REST ICPlan как тулы (путь вне OpenAPI, по коду форка) | MCP-прокси Agent Runner от имени Harness (AD-19) · ключ агента | US-ICP-29, US-HAR-01 | FR-182 | I24 |
