# Platform module

> Файл собирается командой `arch.py assemble` из единиц компонента.

Хранит внутри ICPlan наши настройки, которых в ICPlan нет, и отдаёт их исполнителям.

## Что делает

- Алиасы моделей и бюджеты агентов
- Профили sandbox и памяти
- Данные правил guardrails (allowlist, лимиты)
- Версии определений агентов, экспорт и импорт YAML

## Входы

- [I4](../agent-runner/integrations/I4.yaml): Agent Runner, настройки, определение версии запуска (`GET /platform/runs/:runId/agent`, AD-23), манифест

## Выходы

- [I15](integrations/I15.yaml): LiteLLM gateway, выдача virtual key, бюджеты
- [I16](integrations/I16.yaml): Guardrails, бандл правил: данные из Platform module + Rego из git

## Из чего состоит

- [Требования](prd.md)
- [Истории](stories)
- [Процессы](processes)
- [Блоки](blocks)
- [Функции](functions)
- [Данные](data)
- [Хранилища](stores)
- [Интеграции](integrations)
- [Потоки](flows)
- [Сценарии](sequences)
- [Эндпоинты](endpoints.yaml)
- [Подтверждения](approvals.yaml)
- [agent-registry-architecture](docs/agent-registry-architecture.md)
- [agent-registry-interfaces](docs/agent-registry-interfaces.md)
- [control-plane-architecture](docs/control-plane-architecture.md)
- [control-plane-interfaces](docs/control-plane-interfaces.md)
- [findings](docs/findings.md)
- [how](docs/how.md)
- [techspec](docs/techspec.md)
