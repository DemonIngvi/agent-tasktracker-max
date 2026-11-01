# Deploy: Harness

← компонент · методология

**Что разворачивается:** Python-процесс агентского цикла (LangGraph) внутри sandbox.

## Образы

| Образ | База | Что внутри | Как собирается | Откуда берём | Тег | Пользователь | Порты | Проверка готовности |
|---|---|---|---|---|---|---|---|---|
| agent-harness | `python:3.12-slim` (закреплён digest) | [Harness](../README.md), LangGraph 1.2.14, `langchain[mcp]` 1.4.4, системный промпт платформы (`prompt.platform_version`), инструменты агента | `harness/Dockerfile`: `uv sync --frozen` по `uv.lock` → копия в slim | `ghcr.io/demoningvi/agent-harness` | semver [Harness](../README.md) = версия системного промпта | uid 10001 | 8090 (HTTP [I7](../../agent-runner/integrations/I7.yaml)) | `GET /ready` |

## Запуск

| | |
|---|---|
| **Запуск** | Runner стартует контейнер на запуск (или берёт из пула) и передаёт [`RunBundle`](../../../data/model-RunBundle.yaml) по [I7](../../agent-runner/integrations/I7.yaml) |
| **Сеть** | LiteLLM, MCP, OPA, [Memory](../../memory/README.md) API — внутри кластера; внешнее — через прокси |
| **Состояние** | checkpoint только через Runner ([I12](../integrations/I12.yaml)) |

## Переменные и секреты

| Переменная | Зачем | Откуда |
|---|---|---|
| `RUNNER_URL`, `RUN_TOKEN` | связь с Runner | Runner на запуск |
| `LITELLM_URL`, ключ агента | вызов моделей ([I8](../integrations/I8.yaml)) | Runner на запуск |
| `OPA_URL`, `MEMORY_URL` | G2, память | values |

## Сборка и поставка

1. `uv.lock` закреплён; версии в TECHNOLOGIES.md
2. Системный промпт платформы — файл в образе, версия = версия образа
3. Тесты сценариев на mock-LLM перед публикацией
4. Сборка в GitHub Actions по тегу `vX.Y.Z` репозитория компонента; базовые образы закреплены по digest
5. Многостадийный Dockerfile: стадия сборки → минимальный образ запуска без компиляторов и менеджеров пакетов
6. SBOM (`syft`) и проверка уязвимостей (`trivy`, блокирует выпуск при critical)
7. Публикация в `ghcr.io/demoningvi/<имя>:<версия>` и `:<версия>-<sha>`; тег `latest` не используется
8. Кластер тянет образы с pull-секретом `ghcr-pull` (Secret в namespace)

## Обновление и откат

Своих данных и миграций у [Harness](../README.md) нет: рабочие файлы — в `/workspace` среды (S10, удаляется с контейнером), состояние цикла — таблица `run_checkpoint` схемы `harness_ckpt` (S5), которую пишет и мигрирует [Agent Runner](../../agent-runner/README.md) ([I12](../integrations/I12.yaml), [FR-32](../prd.md)).

1. Обновление — новый образ `agent-harness:<версия>` в `HARNESS_IMAGE` (values [Agent Runner](../../agent-runner/README.md)): новые запуски идут на новом образе, активные доделываются на прежнем ([FR-35](../prd.md)); тёплый пул пересоздаёт контейнеры ([FR-94](../../sandbox/prd.md)).
2. Откат образа — прежний тег и digest в `HARNESS_IMAGE`; новые запуски стартуют на прежнем образе, пул пересоздаётся.
3. Откат после миграции схемы `harness_ckpt` — по Deploy [Agent Runner](..\..\agent-runner\docs\techspec.md): миграции и точка восстановления — у него.
4. Запуск на паузе, начатый новой версией и продолженный прежней, восстанавливается из checkpoint этой версии; совместимость формата checkpoint между версиями [Harness](../README.md) в документах не задана — проверять на тестовых задачах перед откатом (LangGraph закреплён, 1.2.14).
5. Ключей шифрования у [Harness](../README.md) нет: секретов в checkpoint и `/workspace` нет ([FR-32](../prd.md)).

## Проверка после развёртывания

- [ ] Сценарий mock-LLM проходит: шаги, вызов тула, итог

## Пример конфигурации

Как настройки лежат в развёртывании. Значения и границы параметров — в `interfaces.md` спеки (здесь новых не вводится); поля контрактов — в Модели данных.

Параметры уровня L0 (S9, `values.yaml` [Agent Runner](../../agent-runner/README.md), в git, без секретов):

```yaml
harness:
  image: "agent-harness:<версия>"    # HARNESS_IMAGE; prompt.platform_version = версия образа
  prompt: { cache: true }            # false — если провайдер не поддерживает кэш префикса
  request: { timeout_s: 120 }        # 10–600
  hooks: [G2]                        # G2 | аудит | маскирование
  checkpoint: { ttl: 7d }            # от approval_timeout (24 ч) до 30 дней
```
