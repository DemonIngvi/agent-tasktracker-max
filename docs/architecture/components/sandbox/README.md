# Sandbox

> Файл собирается командой `arch.py assemble` из единиц компонента.

Изоляция: каждый запуск агента идёт в своём одноразовом контейнере и не видит другие запуски и хост.

## Что делает

- Держит тёплый пул готовых контейнеров
- Ограничивает CPU, память, диск по профилю (G3)
- Даёт эфемерный /workspace и клон нужных репозиториев
- Пускает трафик только через egress-прокси; реестры пакетов — только шагу подготовки
- Секретов в среде нет: ключи подставляют egress-прокси и MCP-прокси Runner

## Входы

- [I23](../agent-runner/integrations/I23.yaml): Agent Runner, среды запусков через Kubernetes API (этап 4)
- [I6](../agent-runner/integrations/I6.yaml): Agent Runner, Runner создаёт и уничтожает среду (Docker API) по `SandboxClaim`; `RepoGrant` задаёт правила git-прокси этой среды (какие репозитории и ветки), сам токен в среду не попадает

## Выходы

- [I17](integrations/I17.yaml): external-hosts, исходящий трафик через egress-прокси (allowlist)

## Из чего состоит

- [Требования](prd.md)
- [Истории](stories)
- [Процессы](processes)
- [Блоки](blocks)
- [Функции](functions)
- [Интеграции](integrations)
- [Сценарии](sequences)
- [Эндпоинты](endpoints.yaml)
- [Подтверждения](approvals.yaml)
- [agent-sandbox-architecture](docs/agent-sandbox-architecture.md)
- [agent-sandbox-interfaces](docs/agent-sandbox-interfaces.md)
- [findings](docs/findings.md)
- [how](docs/how.md)
- [techspec](docs/techspec.md)
