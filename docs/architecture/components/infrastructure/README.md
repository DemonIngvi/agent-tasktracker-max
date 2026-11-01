# Инфраструктура

> Файл собирается командой `arch.py assemble` из единиц компонента.

Основание платформы: где и как всё запущено, как распределяется нагрузка, где лежат данные и как они сохраняются.

## Что делает

- Кластер k3s на одном узле, namespaces по зонам
- Вход только через Traefik по HTTPS
- Балансировка между репликами — Service
- PostgreSQL 17 под CloudNativePG, пул PgBouncer
- RustFS (S3) для вложений и копий
- Секреты, сетевые политики, бэкапы вне узла

## Входы

- [I22](../../integrations/I22.yaml): platform-services, Postgres через PgBouncer
- [I19](../agent-runner/integrations/I19.yaml): Agent Runner, файлы задачи и артефакты в RustFS (S3 API)
- [I14](../llm-gateway/integrations/I14.yaml): LiteLLM gateway, ключи, бюджеты, журнал затрат в БД `litellm`

## Из чего состоит

- [Требования](prd.md)
- [Истории](stories)
- [Процессы](processes)
- [Блоки](blocks)
- [Функции](functions)
- [Хранилища](stores)
- [Потоки](flows)
- [Сценарии](sequences)
- [Эндпоинты](endpoints.yaml)
- [Подтверждения](approvals.yaml)
- [how](docs/how.md)
- [platform-infrastructure-architecture](docs/platform-infrastructure-architecture.md)
- [platform-infrastructure-interfaces](docs/platform-infrastructure-interfaces.md)
- [techspec](docs/techspec.md)
