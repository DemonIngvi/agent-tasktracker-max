# Guardrails

> Файл собирается командой `arch.py assemble` из единиц компонента.

Ограничения: что агенту можно и что нельзя — в четырёх точках, каждая включается отдельно.

## Что делает

- G1 — допуск и бюджет до запуска (Runner)
- G2 — проверка каждого действия и approve (Harness)
- G3 — изоляция сети, файлов, ресурсов (Sandbox)
- G4 — проверка запросов к модели (LiteLLM)
- OPA как движок, Rego в git, аудит каждого решения

## Входы

- [I5](../agent-runner/integrations/I5.yaml): Agent Runner, допуск запуска G1
- [I10](../harness/integrations/I10.yaml): Harness, проверка действия G2 (для MCP — повторно в Runner)
- [I16](../platform-module/integrations/I16.yaml): Platform module, бандл правил: данные из Platform module + Rego из git

## Из чего состоит

- [Требования](prd.md)
- [Истории](stories)
- [Процессы](processes)
- [Блоки](blocks)
- [Функции](functions)
- [Хранилища](stores)
- [Сценарии](sequences)
- [Эндпоинты](endpoints.yaml)
- [Подтверждения](approvals.yaml)
- [guardrails-architecture](docs/guardrails-architecture.md)
- [guardrails-interfaces](docs/guardrails-interfaces.md)
- [how](docs/how.md)
- [techspec](docs/techspec.md)
