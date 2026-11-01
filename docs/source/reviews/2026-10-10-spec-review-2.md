# Ревью спецификаций 10.10.2026 (ревью 2)

← [Ревью 1](2026-10-10-spec-review.md) · журнал отклонений · [решения AD-17, AD-18](..\design\define-agent-platform\design.md)

Повторное ревью после закрытия открытых вопросов. Роли: аналитик, техлид, архитектор, DevOps-инженер, разработчик, инженер сборки и поставки, тестировщик.

## Статус замечаний ревью 1 {#review1-status}

| ID | Спеки | Было | Решение | Статус |
|---|---|---|---|---|
| X1 | все | трассировка на уровне спеки | ID требований, «Реализует задача», «Закрывает требования», проверка в сборке | ✅ |
| X2 | все | обоснование на уровне спеки | обоснование у требования в RTM: сквозные — R&D и D-номер, новые — [AD-17, AD-18](..\design\define-agent-platform\design.md) | ✅ |
| X3 | все | нет сценариев отказа | FMEA и требование «Отказы»; отказ своего хранилища в каждой FMEA (О-10) | ✅ |
| X4 | все | где хранится параметр | таблица параметров с обоснованием и границами (spec-kinds) | ✅ |
| X5 | platform-infrastructure | бэкап не реализован | [FR-165](../../architecture/components/infrastructure/prd.md), задача 4.7; WAL-архив и копии вне площадки ([AD-18](../../architecture/decisions/AD-18.yaml)) | ✅ |
| X6 | icplan-integration | [I1](../../architecture/components/agent-runner/integrations/I1.yaml)–[I3](../../architecture/components/agent-runner/integrations/I3.yaml) — гипотеза | сверено с кодом `@itsaplan/runner`: claim, heartbeat, result; события — доработка форка | ✅ |
| X7 | guardrails | пороги не обоснованы | обоснования и границы в таблице параметров; калибровка — 3.9, 4.8 ([AD-18](../../architecture/decisions/AD-18.yaml)) | ✅ |
| X8 | guardrails | mTLS | этапы 1–3 без mTLS, этап 4 — mTLS ([AD-18](../../architecture/decisions/AD-18.yaml)) | ✅ |
| X9 | — (правила) | формула не доказывает достаточность | уникальность, двусторонняя трассировка, истории, потолки ревью и подтверждений | ✅ |
| X10 | все, platform-infrastructure | НФТ и развёртывание | требования «Нагрузка» и «Развёртывание» своим содержанием каждой спеки, техспеки | ✅ |
| X11 | platform-infrastructure, tool-integration | архивированные проекты | заменены; версии закреплены ([AD-18](../../architecture/decisions/AD-18.yaml)) | ✅ |
| Р1-01 | agent-runner | падение Runner | FMEA, аренда [ICPlan](../../architecture/components/icplan/README.md) | ✅ |
| Р1-02 | agent-runner | протокол Runner ↔ [Harness](../../architecture/components/harness/README.md) | HTTP + NDJSON ([AD-18](../../architecture/decisions/AD-18.yaml)) | ✅ |
| Р1-03 | agent-runner | sequential и approve | [FR-69](../../architecture/components/agent-runner/prd.md) | ✅ |
| Р1-04 | agent-sandbox | Docker-сокет | rootless Docker, этап 4 — K8s API ([AD-18](../../architecture/decisions/AD-18.yaml)) | ✅ |
| Р1-05 | agent-sandbox | задание в контейнер пула | [I7](../../architecture/components/agent-runner/integrations/I7.yaml) | ✅ |
| Р1-06 | agent-harness | [Harness](../../architecture/components/harness/README.md) в Postgres | checkpoint через Runner ([I12](../../architecture/components/harness/integrations/I12.yaml), [AD-18](../../architecture/decisions/AD-18.yaml)) | ✅ |
| Р1-07 | agent-harness | падение checkpointer | FMEA | ✅ |
| Р1-08 | agent-harness | формат критериев приёмки | чек-лист [ICPlan](../../architecture/components/icplan/README.md) «Критерии приёмки» ([AD-18](../../architecture/decisions/AD-18.yaml)) | ✅ |
| Р1-09 | agent-memory | M4 без задачи | бэклог | ✅ |
| Р1-10 | agent-memory | две точки записи | M2 = `agent_run` [ICPlan](../../architecture/components/icplan/README.md), [Memory](../../architecture/components/memory/README.md) API читает ([AD-18](../../architecture/decisions/AD-18.yaml)) | ✅ |
| Р1-11 | agent-registry | граница Registry и [Platform module](../../architecture/components/platform-module/README.md) | уточнено в требовании «Каталог ресурсов» ([AD-18](../../architecture/decisions/AD-18.yaml)) | ✅ |
| Р1-12 | control-plane | источник правды | S2 | ✅ |
| Р1-13 | guardrails | латентность OPA | рядом, p95 ≤ 20 мс, кэш `opa.cache_ttl_s` ([AD-18](../../architecture/decisions/AD-18.yaml)) | ✅ |
| Р1-14 | guardrails | параметр автономии | `autonomy_level` в таблицах | ✅ |
| Р1-15 | llm-gateway | единая точка отказа | 2 реплики LiteLLM; Postgres с WAL-архивом ([AD-18](../../architecture/decisions/AD-18.yaml)) | ✅ |
| Р1-16 | llm-gateway | версия LiteLLM | v1.104.2 ([AD-18](../../architecture/decisions/AD-18.yaml)) | ✅ |
| Р1-17 | observability | шаблоны маскирования | список в interfaces.md ([AD-18](../../architecture/decisions/AD-18.yaml)) | ✅ |
| Р1-18 | tool-integration | админ-тулы без задачи | бэклог | ✅ |
| Р1-19 | icplan-integration | аренда в протоколе | есть: `next_attempt_at`, `AGENT_RUN_LEASE_SECONDS` | ✅ |
| Р1-20 | icplan-integration | AGPL | доработки форка открыты ([AD-18](../../architecture/decisions/AD-18.yaml)) | ✅ |
| Р1-21 | icplan-agent-autopickup | лимит запусков | `step.max_runs` 3 ([FR-197](../../architecture/components/icplan/prd.md)) | ✅ |
| Р1-22 | icplan-integration | уведомление о решении | [FR-6](../../architecture/components/icplan/prd.md) | ✅ |

## Новые замечания

| ID | Спеки | Роль | Замечание | Решение | Статус |
|---|---|---|---|---|---|
| Р2-01 | все | Аналитик | сквозные требования — шаблонный текст | своё содержание каждой спеки (О-5) | ✅ |
| Р2-02 | все | DevOps-инженер | «Конфигурация» невалидна для модулей [ICPlan](../../architecture/components/icplan/README.md) и инфраструктуры | генерация по видам спек, подтверждения ролей (О-5) | ✅ |
| Р2-03 | icplan-integration, icplan-agent-autopickup | Аналитик | истории [ICPlan](../../architecture/components/icplan/README.md) без администратора и точек входа | 29 историй, методика историй (О-6) | ✅ |
| Р2-04 | icplan-agent-autopickup, icplan-integration, agent-harness, observability | Аналитик | пути историй без требований (вердикт, остановка, указания, выключение, тест, сводка) | [FR-199](../../architecture/components/icplan/prd.md)…22, [FR-10](../../architecture/components/icplan/prd.md)…18, [FR-28](../../architecture/components/harness/prd.md), [FR-152](../../architecture/components/observability/prd.md) ([AD-17](../../architecture/decisions/AD-17.yaml)) | ✅ |
| Р2-05 | icplan-agent-autopickup, tool-integration | Архитектор | «есть в [ICPlan](../../architecture/components/icplan/README.md)» без требования | [FR-204](../../architecture/components/icplan/prd.md), [FR-182](../../architecture/components/mcp-tools/prd.md) (О-4) | ✅ |
| Р2-06 | agent-memory | Архитектор | запись памяти описана только для M3 | потоки M0–M6, правила записи, [FR-44](../../architecture/components/memory/prd.md) (О-8) | ✅ |
| Р2-07 | agent-runner, agent-sandbox, agent-harness | Архитектор | не описано подключение папки и репозитория | [FR-76](../../architecture/components/agent-runner/prd.md), [FR-89](../../architecture/components/sandbox/prd.md), [FR-29](../../architecture/components/harness/prd.md) (О-15) | ✅ |
| Р2-08 | agent-harness, control-plane, llm-gateway | Разработчик | не описаны параметры вызова модели и слои промпта | [FR-30](../../architecture/components/harness/prd.md), [FR-102](../../architecture/components/platform-module/prd.md), параметры `model.*` (О-16) | ✅ |
| Р2-09 | все | Инженер сборки и поставки | не описана сборка и поставка образов | техспеки компонентов (О-17) | ✅ |
| Р2-10 | все | DevOps-инженер | FMEA без отказа своих хранилищ | строки FMEA (О-10) | ✅ |
| Р2-11 | agent-memory | Тестировщик | значение в двух местах разное (10 и 16 КБ) | одно место — параметр (О-9) | ✅ |
| Р2-12 | icplan-integration | Архитектор | [I1](../../architecture/components/agent-runner/integrations/I1.yaml)–[I3](../../architecture/components/agent-runner/integrations/I3.yaml) не сверены с кодом | сверено (О-13) | ✅ |

## Итог

- Открытых замечаний нет; причины найденных отклонений закрыты правилами (журнал).
- Решения [AD-18](../../architecture/decisions/AD-18.yaml) по бывшим вопросам 📌 приняты агентом; их подтверждает владелец продукта (роль в `approvals.md`).
