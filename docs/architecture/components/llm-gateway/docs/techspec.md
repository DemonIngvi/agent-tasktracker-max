# Deploy: LiteLLM gateway

← компонент · методология

**Что разворачивается:** LiteLLM Proxy: алиасы, бюджеты, учёт; mock-LLM для разработки.

## Образы

| Образ | База | Что внутри | Как собирается | Откуда берём | Тег | Пользователь | Порты | Проверка готовности |
|---|---|---|---|---|---|---|---|---|
| litellm | официальный `ghcr.io/berriai/litellm:v1.104.2-stable` | LiteLLM Proxy | официальный образ | GHCR BerriAI, закреплён digest | v1.104.2 | non-root | 4000 | `GET /health/liveliness`, `/health/readiness` |
| mock-llm | `python:3.12-slim` | OpenAI-совместимый mock со сценариями | `mock-llm/Dockerfile` | `ghcr.io/demoningvi/mock-llm` | semver платформы | uid 10001 | 8000 | `GET /health` |

## Запуск

| | |
|---|---|
| **Реплики** | LiteLLM 2 |
| **Конфиг** | `config.yaml` из ConfigMap (`model_list`, `fallbacks`, `drop_params: true`) |
| **БД** | Postgres `litellm` через PgBouncer (`pgbouncer=true`), миграции — прямым подключением |

## Переменные и секреты

| Переменная | Зачем | Откуда |
|---|---|---|
| `LITELLM_MASTER_KEY` | админ-ключ | Secret |
| ключи провайдеров | провайдеры | Secret `llm-providers` |
| `DATABASE_URL`, `DIRECT_URL` | база `litellm`, роль `litellm`: работа через PgBouncer и миграции напрямую ([AD-22](../../../decisions/AD-22.yaml)) | Secret |

## Сборка и поставка

1. mock-LLM: сценарии в git, сборка как Python-сервис
2. Сборка в GitHub Actions по тегу `vX.Y.Z` репозитория компонента; базовые образы закреплены по digest
3. Многостадийный Dockerfile: стадия сборки → минимальный образ запуска без компиляторов и менеджеров пакетов
4. SBOM (`syft`) и проверка уязвимостей (`trivy`, блокирует выпуск при critical)
5. Публикация в `ghcr.io/demoningvi/<имя>:<версия>` и `:<версия>-<sha>`; тег `latest` не используется
6. Кластер тянет образы с pull-секретом `ghcr-pull` (Secret в namespace)

## Обновление и откат

Данные шлюза — БД `litellm` (S6): virtual keys, бюджеты, журнал затрат; конфиг алиасов и резервных моделей — `config.yaml` в ConfigMap (S9, в git). Точка восстановления — базовые копии и WAL Postgres в S3 вне узла.

1. Порядок: новый тег образа LiteLLM закрепляется по digest; миграции схемы БД `litellm` идут прямым подключением (`DIRECT_URL`), затем обновляются реплики — две реплики по одной, вызовы [Harness](../../harness/README.md) проходят через вторую.
2. Конфиг (`model_list`, `fallbacks`) меняется отдельно от образа: переназначение алиаса не требует обновления агентов.
3. Откат — прежний тег и digest образа; если миграция новой версии уже прошла, откат образа возможен только на версию, совместимую со схемой, иначе — восстановление БД `litellm` из копии на момент до обновления.
4. Ключ, без которого данные не прочитать и ключи не обновить, — `LITELLM_MASTER_KEY` (Secret): при смене [Platform module](../../platform-module/README.md) получает новый ключ вместе с перезапуском api, до этого изменения бюджетов повторяются ([FR-108](../../platform-module/prd.md)).
5. Пока БД `litellm` недоступна при обновлении, вызовы отклоняются (FMEA «БД `litellm` недоступна»).

## Проверка после развёртывания

- [ ] Вызов алиаса `team-default` → ответ mock
- [ ] Затраты по `metadata.run_id` видны

## Пример конфигурации

Как настройки лежат в развёртывании. Значения и границы параметров — в `interfaces.md` спеки (здесь новых не вводится); поля контрактов — в Модели данных.

Конфиг алиасов (mock для разработки):

```yaml
model_list:
  - model_name: team-default
    litellm_params: { model: openai/mock, api_base: http://mock-llm:8000/v1 }
  - model_name: team-default-fallback
    litellm_params: { model: anthropic/claude-sonnet-5 }
router_settings:
  fallbacks: [{ team-default: [team-default-fallback] }]
```

Сценарий mock-LLM (задача [1.1](..\..\..\..\source\tasks\1.1-mock-llm-litellm.md)):

```yaml
- match: "MKT-42"
  steps:
    - tool_call: { name: add_comment, arguments: { issue: MKT-42, body: "Готово" } }
    - text: "Комментарий оставлен."
```
