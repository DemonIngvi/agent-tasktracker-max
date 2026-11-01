# Интеграции: Platform module

← компонент · Deploy · методология

<div class="api-head">
<div><span class="about-label">Базовый адрес</span> `/api/platform` (в api форка ICPlan)</div>
<div><span class="about-label">Аутентификация</span> UI — сессия администратора; Runner — сервисный токен</div>
</div>

## Настройки агента

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-get">GET</span> | `/platform/agents/:agentId/settings` | <span class="st st-new">🆕 новое</span> | бюджеты, профили, автономия, данные guardrails | Администратор, Runner (I4) · сессия / сервисный токен | US-PM-01 | FR-95, FR-100 | I4 |
| <span class="m m-patch">PATCH</span> | `/platform/agents/:agentId/settings` | <span class="st st-new">🆕 новое</span> | изменить настройки (со следующего запуска) | Администратор · сессия | US-PM-01, US-PM-02, US-PM-05 | FR-95, FR-97, FR-117 | I20 |
| <span class="m m-get">GET</span> | `/platform/agents/:agentId/export` | <span class="st st-new">🆕 новое</span> | экспорт определения в YAML | Администратор · сессия | US-PM-03 | FR-99 | I20 |
| <span class="m m-post">POST</span> | `/platform/agents/import` | <span class="st st-new">🆕 новое</span> | импорт YAML (новая версия) | Администратор · сессия | US-PM-03 | FR-99 | I20 |
| <span class="m m-get">GET</span> | `/platform/agents/:agentId/settings/versions` | <span class="st st-new">🆕 новое</span> | история настроек: версия, кто, когда | Администратор · сессия (карточка агента → «Платформа», AD-24) | US-PM-02 | FR-98 | I20 |
| <span class="m m-post">POST</span> | `/platform/agents/:agentId/settings/rollback` | <span class="st st-new">🆕 новое</span> | откат к версии: новая версия с её содержимым, со следующего запуска | Администратор · сессия, право `ai_agents` | US-PM-02 | FR-98, FR-101 | I20 |

## Экземпляр: профили и kill switch

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-get">GET</span> | `/platform/sandbox-profiles` | <span class="st st-new">🆕 новое</span> | профили среды (`sandbox_profile`) | Администратор · сессия | US-PM-01 | FR-86 | I20 |
| <span class="m m-put">PUT</span> | `/platform/sandbox-profiles/:name` | <span class="st st-new">🆕 новое</span> | создать или изменить профиль среды | Владелец экземпляра · сессия (God mode → «Платформа», AD-24) | US-PM-01 | FR-86 | I20 |
| <span class="m m-del">DELETE</span> | `/platform/sandbox-profiles/:name` | <span class="st st-new">🆕 новое</span> | удалить профиль среды; запрещено, пока профиль используется | Владелец экземпляра · сессия (God mode → «Платформа», AD-24) | US-PM-01 | FR-86 | I20 |
| <span class="m m-get">GET</span> | `/platform/memory-profiles` | <span class="st st-new">🆕 новое</span> | профили памяти (`memory_profile`) | Администратор · сессия | US-MEM-04 | FR-48 | I20 |
| <span class="m m-put">PUT</span> | `/platform/memory-profiles/:name` | <span class="st st-new">🆕 новое</span> | создать или изменить профиль памяти | Владелец экземпляра · сессия (God mode → «Платформа», AD-24) | US-MEM-04 | FR-48 | I20 |
| <span class="m m-del">DELETE</span> | `/platform/memory-profiles/:name` | <span class="st st-new">🆕 новое</span> | удалить профиль памяти; запрещено, пока профиль используется | Владелец экземпляра · сессия (God mode → «Платформа», AD-24) | US-MEM-04 | FR-48 | I20 |
| <span class="m m-get">GET</span> | `/platform/kill-switch` | <span class="st st-new">🆕 новое</span> | состояние аварийной остановки: `platform`, `agent:<id>` | Администратор, эксплуатация · сессия / сервисный токен | US-GRD-04 | FR-124 | I20 |
| <span class="m m-put">PUT</span> | `/platform/kill-switch/:scope` | <span class="st st-new">🆕 новое</span> | включить или выключить kill switch агента или платформы, сразу | `agent:<id>` — администратор (право `ai_agents`), `platform` — владелец экземпляра; эксплуатация · сервисный токен (AD-24) | US-GRD-04 | FR-124, FR-97 | I20 |

## Проект

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-get">GET</span> | `/platform/projects/:projectKey` | <span class="st st-new">🆕 новое</span> | настройки проекта для экрана «Платформа: проект»: руководство, месячный бюджет, шаг подготовки (`project_platform`) | Администратор · сессия, право `ai_agents` | US-PM-08, US-PM-06 | FR-102 | I20 |
| <span class="m m-put">PUT</span> | `/platform/projects/:projectKey/guidance` | <span class="st st-new">🆕 новое</span> | руководство проекта для агентов | Администратор · сессия | US-PM-08 | FR-102 | I20 |
| <span class="m m-put">PUT</span> | `/platform/projects/:projectKey/budget` | <span class="st st-new">🆕 новое</span> | бюджет проекта | Администратор · сессия | US-PM-06 | FR-120 | I20 |
| <span class="m m-get">GET</span> | `/platform/projects/:projectKey/access` | <span class="st st-new">🆕 новое</span> | политика доступа агент × ресурс × право | Администратор, безопасность · сессия | US-SBX-06 | FR-76 | I20 |
| <span class="m m-put">PUT</span> | `/platform/projects/:projectKey/access` | <span class="st st-new">🆕 новое</span> | изменить политику доступа | Администратор · сессия | US-SBX-06 | FR-76 | I20 |
| <span class="m m-get">GET</span> | `/platform/projects/:projectKey/resources` | <span class="st st-new">🆕 новое</span> | ресурсы проекта: git, папки, документы, MCP (`project_resource`) | Администратор · сессия | US-SBX-06 | FR-76 | I20 |
| <span class="m m-put">PUT</span> | `/platform/projects/:projectKey/resources` | <span class="st st-new">🆕 новое</span> | изменить ресурсы проекта | Администратор · сессия, право `ai_agents` (Проект → ИИ-команда → «Платформа», AD-24) | US-SBX-06 | FR-76 | I20 |
| <span class="m m-put">PUT</span> | `/platform/projects/:projectKey/setup` | <span class="st st-new">🆕 новое</span> | шаг подготовки проекта: скрипт и lock-файлы (AD-19) | Администратор · сессия, право `ai_agents` | US-SBX-06 | FR-89 | I20 |

## Для Runner и журнал

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-get">GET</span> | `/platform/runs/:runId/manifest` | <span class="st st-new">🆕 новое</span> | манифест рабочего пространства запуска | Agent Runner · сервисный токен | US-SBX-05 | FR-76 | I4 |
| <span class="m m-get">GET</span> | `/platform/runs/:runId/agent` | <span class="st st-new">🆕 новое</span> | определение и настройки версии запуска одним ответом: `{version, definition, settings}`; версия закрепляется в `agent_run.agent_version` при первом вызове; 404 — запуск не `pending` или агент не `external`, 409 — версии нет (AD-23) | Agent Runner · сервисный токен | US-MEM-07 | FR-54, FR-55, FR-97 | I4 |
| <span class="m m-get">GET</span> | `/platform/audit` | <span class="st st-new">🆕 новое</span> | журнал изменений настроек и политик | Безопасность (право чтения), владелец экземпляра (God mode → «Платформа», AD-24) · сессия | US-PM-07 | FR-101 | I20 |
