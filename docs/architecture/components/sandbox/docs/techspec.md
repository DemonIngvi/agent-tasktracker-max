# Deploy: Sandbox

← компонент · методология

**Что разворачивается:** одноразовый контейнер запуска на образе [Harness](../../harness/README.md); тёплый пул; сеть только через egress-прокси.

## Образы

| Образ | База | Что внутри | Как собирается | Откуда берём | Тег | Пользователь | Порты | Проверка готовности |
|---|---|---|---|---|---|---|---|---|
| agent-harness (образ среды) | см. [Harness](../../harness/README.md) | [Harness](../../harness/README.md) + инструменты агента: git, ripgrep, python, node | см. [Harness](../../harness/README.md) | `ghcr.io/demoningvi/agent-harness` | версия [Harness](../../harness/README.md) | uid 10001, без sudo | 8090 ([I7](../../agent-runner/integrations/I7.yaml)) | `GET /ready` [Harness](../../harness/README.md) |
| egress-proxy | `ubuntu/squid:6` | Squid с allowlist доменов | конфиг из ConfigMap | Docker Hub `ubuntu/squid` (закреплён digest) | 6.x | squid | 3128 | TCP 3128 |

## Запуск

| | |
|---|---|
| **Изоляция** | read-only rootfs, `/workspace` — tmpfs / emptyDir по профилю, `no-new-privileges`, drop ALL capabilities, seccomp RuntimeDefault |
| **Сеть** | внутренняя сеть sandbox; выход только через `egress-proxy`; NetworkPolicy deny all, кроме прокси и Runner |
| **Профили** | `light` 1 CPU / 1 ГБ / 2 ГБ диска; `standard`, `heavy` — по таблице параметров |
| **Пул** | `pool.size` тёплых контейнеров на профиль |

## Переменные и секреты

| Переменная | Зачем | Откуда |
|---|---|---|
| `RUN_TOKEN` | одноразовый токен запуска ([I7](../../agent-runner/integrations/I7.yaml), [I12](../../harness/integrations/I12.yaml)) | Runner на запуск |
| `HTTPS_PROXY` | egress-прокси | Runner |
| токены git | не в env: подставляет прокси | — |
| ключи MCP-серверов | не в env и не в прокси: подставляет MCP-прокси Runner ([AD-19](../../../decisions/AD-19.yaml)) | — |
| секреты приватных реестров | только в контейнере подготовки ([AD-19](../../../decisions/AD-19.yaml)), в среду агента не передаются | Secret проекта |

Squid: две подсети источника — `sbx-agent` (только сервисы платформы и allowlist профиля) и `sbx-setup` (плюс `setup.registries`); правила `acl … src` + `dstdomain` ([AD-19](../../../decisions/AD-19.yaml)).

## Сборка и поставка

1. Образ среды = образ [Harness](../../harness/README.md)
2. Squid: конфиг allowlist генерируется из политики доступа
3. Сборка в GitHub Actions по тегу `vX.Y.Z` репозитория компонента; базовые образы закреплены по digest
4. Многостадийный Dockerfile: стадия сборки → минимальный образ запуска без компиляторов и менеджеров пакетов
5. SBOM (`syft`) и проверка уязвимостей (`trivy`, блокирует выпуск при critical)
6. Публикация в `ghcr.io/demoningvi/<имя>:<версия>` и `:<версия>-<sha>`; тег `latest` не используется
7. Кластер тянет образы с pull-секретом `ghcr-pull` (Secret в namespace)

## Обновление и откат

Постоянных данных у [Sandbox](../README.md) нет: `/workspace` (S10) удаляется вместе с контейнером, результаты сохраняются вне среды — ветка и PR, вложения задачи, подпапка шага в RustFS (S7, выгружает Runner) ([FR-84](../prd.md), [FR-91](../prd.md)). Профили (`sandbox_profile`) — таблица [Platform module](../../platform-module/README.md), их откат — по Deploy [ICPlan](..\..\icplan\docs\techspec.md).

1. Новый образ среды (`HARNESS_IMAGE`) — пул пересоздаёт тёплые контейнеры, новые запуски идут на новом образе, активные доделываются ([FR-94](../prd.md)).
2. Новая версия `egress-proxy` — прокси заменяется без разрыва активных соединений дольше переподключения; пока прокси нет, исходящий трафик запрещён (fail-closed).
3. Откат — прежний тег и digest образа среды или `egress-proxy`; пул пересоздаётся так же, как при обновлении. Миграций нет, откатывать данные не нужно.
4. Ключей, без которых данные не прочитать, нет: секреты в среду и на её диск не попадают ([FR-88](../prd.md), [FR-91](../prd.md)).

## Проверка после развёртывания

- [ ] Запрос к домену вне allowlist отклонён
- [ ] Контейнер удалён после запуска

## Пример конфигурации

Как настройки лежат в развёртывании. Значения и границы параметров — в `interfaces.md` спеки (здесь новых не вводится); поля контрактов — в Модели данных.

Профиль sandbox:

```yaml
profile: light
image: agent-harness:0.3.1
resources: { cpu: 1, memory_mb: 1024, disk_gb: 2 }
network:
  egress_allow: [litellm, api, memory, opa, github.com]
pool: { size: 2 }
```
