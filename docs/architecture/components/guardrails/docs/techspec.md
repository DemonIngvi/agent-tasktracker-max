# Deploy: Guardrails

← компонент · методология

**Что разворачивается:** OPA рядом с Runner и [Harness](../../harness/README.md); правила Rego из git; данные из [Platform module](../../platform-module/README.md).

## Образы

| Образ | База | Что внутри | Как собирается | Откуда берём | Тег | Пользователь | Порты | Проверка готовности |
|---|---|---|---|---|---|---|---|---|
| opa | `openpolicyagent/opa:1.21.1-static` | OPA | официальный образ | Docker Hub, закреплён digest; копия в GHCR платформы | 1.21.1 | nonroot | 8181 | `GET /health?bundles` |
| opa-bundle | — | tar.gz: Rego из git + данные агентов | CI: `opa test` → `opa build`; данные — [Platform module](../../platform-module/README.md) | объектное хранилище (S3) / HTTP [Platform module](../../platform-module/README.md) | sha коммита правил | — | — | OPA сообщает версию бандла |

## Запуск

| | |
|---|---|
| **Реплики** | 2 |
| **Задержка** | на том же узле; p95 ≤ 20 мс; кэш решений `opa.cache_ttl_s` |

## Переменные и секреты

| Переменная | Зачем | Откуда |
|---|---|---|
| `OPA_BUNDLE_URL` | источник бандла | values |

## Сборка и поставка

1. Правила в git с тестами `opa test` (обязательно)
2. Сборка бандла в CI и публикация
3. Сборка в GitHub Actions по тегу `vX.Y.Z` репозитория компонента; базовые образы закреплены по digest
4. Многостадийный Dockerfile: стадия сборки → минимальный образ запуска без компиляторов и менеджеров пакетов
5. SBOM (`syft`) и проверка уязвимостей (`trivy`, блокирует выпуск при critical)
6. Публикация в `ghcr.io/demoningvi/<имя>:<версия>` и `:<версия>-<sha>`; тег `latest` не используется
7. Кластер тянет образы с pull-секретом `ghcr-pull` (Secret в namespace)

## Обновление и откат

Своих таблиц и миграций у [Guardrails](../README.md) нет: правила — Rego в git (S8), данные агентов — [Platform module](../../platform-module/README.md) (S2), OPA держит бандл в памяти (S11) и пересобирает его при старте ([FR-128](../prd.md)).

1. Новые правила: PR в репозиторий политик → `opa test` → `opa build` → публикация бандла с версией = sha коммита; OPA подхватывает бандл опросом раз в 30 с ([I16](../../platform-module/integrations/I16.yaml)), без перезапуска.
2. Обновление образа `opa` — по одной реплике из двух; пока одна реплика недоступна, вызовы идут на другую, при отказе обеих действует `on_engine_error` (deny).
3. Откат правил — revert коммита и новый бандл; откат образа — прежний тег и digest. Данных для отката нет: S11 не источник правды.
4. Битый Rego не применяется: OPA остаётся на прежнем бандле (FMEA «Битый Rego»); миграций схем нет, откатывать данные не нужно.
5. Изменение `g1…g4.enabled` и `on_engine_error` (values, L0) применяется после перезапуска модуля; выключение G2 в prod сопровождается предупреждением.

## Проверка после развёртывания

- [ ] Запрещённый тул → deny
- [ ] Без бандла → deny (`on_engine_error`)

## Пример конфигурации

Как настройки лежат в развёртывании. Значения и границы параметров — в `interfaces.md` спеки (здесь новых не вводится); поля контрактов — в Модели данных.

Правило (Rego, в git):

```rego
package agent.g2
default allow := false
allow if input.tool in data.agents[input.agent].tools_allow
confirm if input.tool in data.agents[input.agent].approval
```

Конфиг деплоя:

```yaml
guardrails:
  engine: opa
  g1: { enabled: true,  on_engine_error: deny }
  g2: { enabled: true,  on_engine_error: deny, approval: true }
  g3: { enabled: true }
  g4: { enabled: false }
```
