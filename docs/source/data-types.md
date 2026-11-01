# Типы данных

← Правила документации · термины и коды · [взаимодействие компонентов](architecture.md) · [сборка запроса к модели](..\architecture\components\harness\docs\how.md)

Все данные платформы разбиты на типы. Для каждого типа — откуда берётся, где хранится, кто пишет и читает, как защищается. Каждый интерфейс (I-код) отнесён к типам данных, которые по нему идут; сборка проверяет, что в матрице есть все I-коды из `interfaces.md` спек.

## Типы

| Код | Тип | Примеры | Откуда | Где хранится | Пишет | Читает | Защита | Срок |
|---|---|---|---|---|---|---|---|---|
| **Т1** | Промпт | системный промпт платформы, руководство проекта, инструкция и навыки агента, задание, указания пользователя | git платформы, [Platform module](../architecture/components/platform-module/README.md), Registry, задача [ICPlan](../architecture/components/icplan/README.md), чат | S8, S2, S1; копия в событиях запуска S3 (`events.level: всё`) | разработчик платформы, администратор, пользователь | [Harness](../architecture/components/harness/README.md) → модель | слой 1 не отменяется нижними; маскирование секретов в задании | версии; задача — по [ICPlan](../architecture/components/icplan/README.md) |
| **Т2** | Контекст памяти | M0 рабочий, M1 переписка, M2 итоги, M3 состояние, M4 факты | [Harness](../architecture/components/harness/README.md), [ICPlan](../architecture/components/icplan/README.md), Runner, агент | контекст запуска, S1, S4 | см. [потоки памяти](..\architecture\components\memory\docs\how.md) | [Harness](../architecture/components/harness/README.md) | профиль памяти, область видимости, маскирование | M0 — запуск; M1 30 д; M2 180 д; M3 — до закрытия задачи |
| **Т3** | Документы и файлы | документы проекта (M6), вложения, файлы рабочего пространства, артефакты, код | пользователи, агент, git | S1, S7, S10, git | пользователи; агент — своя подпапка, ветка | агент (по политике), пользователи | политика доступа, токены на запуск, egress-прокси, проверка секретов при публикации | по [ICPlan](../architecture/components/icplan/README.md) и git; `/workspace` — запуск |
| **Т4** | Конфигурация | параметры L0–L3, определения агентов, процессы, политики доступа, правила Rego, values Helm | администратор, эксплуатация | S9, S2, S1, S8 | администратор, эксплуатация | все модули | права на настройки, журнал изменений, версии | версии |
| **Т5** | Секреты | ключи провайдеров, virtual keys, токены git, ключи агентов [ICPlan](../architecture/components/icplan/README.md), пароли БД, ключи S3 | эксплуатация, [Platform module](../architecture/components/platform-module/README.md), git-провайдер | Secret кластера, S6 (virtual keys) | эксплуатация, [Platform module](../architecture/components/platform-module/README.md) | сервисы по ссылке; в sandbox — через прокси | не в git и не в БД платформы; маскирование; ротация без простоя | до ротации; токен запуска — время запуска |
| **Т6** | Управляющие сообщения | [`Run`](../architecture/data/model-Run.yaml), [`RunBundle`](../architecture/data/model-RunBundle.yaml), [`ApprovalDecision`](../architecture/data/model-ApprovalDecision.yaml), [`UserMessage`](../architecture/data/model-UserMessage.yaml), отмена, [`PolicyInput`](../architecture/data/model-PolicyInput.yaml) / [`PolicyDecision`](../architecture/data/model-PolicyDecision.yaml), heartbeat | [ICPlan](../architecture/components/icplan/README.md), Runner, OPA | S1 (`agent_run`), память сервисов | [ICPlan](../architecture/components/icplan/README.md), Runner, OPA | Runner, [Harness](../architecture/components/harness/README.md) | аутентификация интерфейса, идемпотентность | по `agent_run` |
| **Т7** | Телеметрия и учёт | [`RunEvent`](../architecture/data/model-RunEvent.yaml), трассы, затраты, аудит guardrails, журнал изменений, статистика | [Harness](../architecture/components/harness/README.md), Runner, LiteLLM, OPA | S3, S6, журналы | [Harness](../architecture/components/harness/README.md), Runner, LiteLLM | [Observability](../architecture/components/observability/README.md), пользователи, администратор | маскирование, `events.level` | 90 дней (`retention_days`) |
| **Т8** | Ответы модели и тулов | текст ответа, вызовы тулов, размышления, вывод тулов | провайдер модели, MCP-серверы | M0; итог — M2 и комментарий | LiteLLM, MCP | [Harness](../architecture/components/harness/README.md), пользователь (итог) | обрезка `max_result_kb`; размышления и полные ответы — в событиях запуска S3 при `events.level: всё` (по умолчанию, [AD-18](../architecture/decisions/AD-18.yaml)), маскируются; G4 | M0 — запуск; итог — по M2 |

## Матрица интерфейсов

Какие типы данных идут по каждому интерфейсу. Стороны, назначение и модели — из `html-view/datamodel.py` (INTEG), типы — INTEG_TYPES; таблица генерируется.

<!-- iface-matrix -->
