# Deploy: Инфраструктура

← компонент · методология

**Что разворачивается:** k3s на одном узле, Helm-чарты, Traefik, CloudNativePG + PgBouncer, RustFS, бэкапы вне площадки.

## Образы

| Образ | База | Что внутри | Как собирается | Откуда берём | Тег | Пользователь | Порты | Проверка готовности |
|---|---|---|---|---|---|---|---|---|
| k3s | установщик `get.k3s.io`, версия `v1.37.1+k3s1` | Kubernetes, Traefik, local-path | скрипт установки с закреплённой версией | github.com/k3s-io/k3s releases | v1.37.1+k3s1 | — | 6443 | `kubectl get --raw /readyz` |
| postgresql | `ghcr.io/cloudnative-pg/postgresql:17` (pgvector в комплекте) | Postgres 17 | оператор CloudNativePG | GHCR CloudNativePG, закреплён digest | 17.x | postgres | 5432 | проверки оператора |
| pgbouncer | Pooler CloudNativePG | PgBouncer transaction | ресурс `Pooler` | образ оператора | версия оператора | — | 5432 | проверки оператора |
| rustfs | `rustfs/rustfs:1.0.0` | S3-совместимое хранилище | официальный образ | Docker Hub, закреплён digest | 1.0.0 | non-root | 9000 | `/health` |

## Запуск

| | |
|---|---|
| **Порядок** | CNPG → Postgres → PgBouncer → RustFS → ICPlan → LiteLLM, OPA → Runner |
| **Бэкап** | WAL-архив и копии CNPG в внешнее S3 на другой площадке |
| **Секреты** | Secret кластера; ротация без простоя |

## Переменные и секреты

| Переменная | Зачем | Откуда |
|---|---|---|
| `values.yaml` | параметры L0 платформы | git платформы (без секретов) |

## Сборка и поставка {#build}

1. Чарты в git платформы, `helm lint` и `values.schema.json` в CI
2. Сборка в GitHub Actions по тегу `vX.Y.Z` репозитория компонента; базовые образы закреплены по digest
3. Многостадийный Dockerfile: стадия сборки → минимальный образ запуска без компиляторов и менеджеров пакетов
4. SBOM (`syft`) и проверка уязвимостей (`trivy`, блокирует выпуск при critical)
5. Публикация в `ghcr.io/demoningvi/<имя>:<версия>` и `:<версия>-<sha>`; тег `latest` не используется
6. Кластер тянет образы с pull-секретом `ghcr-pull` (Secret в namespace)

## Обновление и откат

Данные слоя — кластер PostgreSQL 17 (CloudNativePG, БД `itsaplan` и `litellm`), бакет `planner-attachments` в RustFS и их копии: базовые копии и WAL Postgres, копия RustFS — в S3 вне узла. Миграции схем выполняют сами компоненты (ICPlan, LiteLLM, Memory) до старта новых реплик, схема `platform` при обновлении ICPlan не затрагивается (FR-163).

1. Порядок: перед обновлением проверяется свежая базовая копия и WAL в S3 вне узла; затем чарты по зависимостям (CNPG, Postgres, PgBouncer, RustFS, затем сервисы).
2. Сервисы с двумя и более репликами обновляются по одной, проверки готовности зелёные; без простоя (FR-160).
3. Откат чарта — `helm rollback` на предыдущую ревизию; версия, не прошедшая проверки готовности, откатывается так же. Миграции схем назад не откатываются: после миграции возврат к данным до неё — восстановление на момент времени (PITR) из копии в отдельный namespace (задача 4.7.6).
4. Обновление k3s и оператора CloudNativePG — отдельным шагом с закреплённой версией; проверка узла kube-bench после обновления k3s.
5. Ключи, без которых данные не прочитать: пароли ролей БД и ключи RustFS в Secret кластера, ключи доступа к S3 вне узла. Секреты создаются скриптом из локального `.env` и хранятся вне git (FR-166).

## Проверка после развёртывания

- [ ] `helm install` на чистом сервере проходит
- [ ] Восстановление БД из копии на тестовом узле

## Пример конфигурации {#example}

Как настройки лежат в развёртывании. Значения и границы параметров — в `interfaces.md` спеки (здесь новых не вводится); поля контрактов — в Модели данных.

Фрагмент `values-server.yaml`:

```yaml
ingress:
  host: plan.example.com
  tls: { acme: true }
api:      { replicas: 2, resources: { requests: { cpu: 300m, memory: 512Mi }, limits: { cpu: "1", memory: 1Gi } } }
litellm:  { replicas: 2, resources: { requests: { cpu: 300m, memory: 800Mi } } }
opa:      { replicas: 2, resources: { requests: { cpu: 50m, memory: 128Mi } } }
pgbouncer: { poolMode: transaction, defaultPoolSize: 30 }
postgres:
  backup: { target: s3://backup-offsite/itsaplan, schedule: "0 3 * * *" }
objectStorage: { endpoint: http://rustfs.itsaplan-data:9000, bucket: planner-attachments }
existingSecret: itsaplan-secrets
networkPolicy: { enabled: true }
```
