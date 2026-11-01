# MCP / Tools

> Файл собирается командой `arch.py assemble` из единиц компонента.

Руки агента: действия во внешних системах — задачи, документы, git.

## Что делает

- MCP ICPlan: читать задачу, писать комментарий, менять статус
- MCP git-провайдера: ветки и PR
- Тул памяти для записи M3
- Allowlist в MCP-прокси Runner вне sandbox (AD-19), таймауты
- Правила R1–R7: когда MCP, когда прямой вызов

## Входы

- [I9](../harness/integrations/I9.yaml): Harness, вызов тулов MCP через MCP-прокси Runner (AD-19)

## Из чего состоит

- [Требования](prd.md)
- [Истории](stories)
- [Процессы](processes)
- [Блоки](blocks)
- [Функции](functions)
- [Сценарии](sequences)
- [Эндпоинты](endpoints.yaml)
- [Подтверждения](approvals.yaml)
- [how](docs/how.md)
- [techspec](docs/techspec.md)
- [tool-integration-architecture](docs/tool-integration-architecture.md)
- [tool-integration-interfaces](docs/tool-integration-interfaces.md)
