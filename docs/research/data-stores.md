# R&D: Хранилища данных (Postgres и объектное хранилище)

← [Все R&D](README.md) · методология R&D v3.1 · компонент: **[Инфраструктура](../architecture/components/infrastructure/README.md)** · решение: [design AD-4, AD-15, AD-18](..\source\design\define-agent-platform\design.md) · спека: platform-infrastructure

<div class="rnd-hero" markdown>
<div class="rnd-q">Вопрос</div>
На чём держать реляционные данные ([ICPlan](../architecture/components/icplan/README.md), схемы платформы, LiteLLM, checkpoint) и объекты (вложения, артефакты, бэкапы), чтобы бэкапы и пул соединений были из коробки, а [ICPlan](../architecture/components/icplan/README.md) не пришлось перенастраивать?

<div class="rnd-a">Ответ: PostgreSQL 17 под CloudNativePG (стандартный образ с pgvector, PgBouncer в режиме transaction, WAL и копии в S3 вне узла) и RustFS как в [ICPlan](../architecture/components/icplan/README.md). MinIO отпал: репозиторий архивирован.</div>

<span class="rnd-badge adopt">Adopt</span> PostgreSQL 17, RustFS 1.0.x · <span class="rnd-badge trial">Trial</span> CloudNativePG v1.30.1 · 0 $ · данные 11.10.2026
</div>

```deck
# Покрытие потребностей П1–П7
> CloudNativePG + RustFS закрывает всё и совпадает с ICPlan
stack CloudNativePG + RustFS: 7 ok, 0 part, 0 no
stack Crunchy PGO + RustFS: 6 ok, 1 part, 0 no
stack Zalando + RustFS: 5 ok, 2 part, 0 no
stack CloudNativePG + SeaweedFS: 6 ok, 1 part, 0 no
stack StatefulSet ICPlan + RustFS: 4 ok, 1 part, 2 no
# Что уже совпадает с ICPlan
> RustFS и pgvector уже в ICPlan; меняется только способ запуска Postgres
bar RustFS: 1/1 как в ICPlan ok
bar pgvector: 1/1 стандартный образ CNPG ok
bar Postgres: 0/1 StatefulSet → кластер CNPG part
# Объём доработки
> CloudNativePG + RustFS — задача 4.7, 30 ч по подзадачам; у остальных кандидатов оценок задач нет
bar 4.7.1 CloudNativePG и кластер: 6/30 ч ok
bar 4.7.2 PgBouncer и session-клиенты: 4/30 ч ok
bar 4.7.3 роли и схемы: 3/30 ч ok
bar 4.7.4 RustFS: 3/30 ч ok
bar 4.7.5 бэкап вне узла: 6/30 ч ok
bar 4.7.6 проверка восстановления (PITR): 4/30 ч ok
bar 4.7.7 очистка запусков и тредов чата: 4/30 ч ok
# Позиции ролей
side CloudNativePG | Crunchy PGO
pos DevOps: -1 | бэкап WAL и пулер — ресурсы оператора
pos Архитектор: -1 | один кластер для всех схем
pos Разработчик: 0 | PgBouncer transaction проверен по коду
pos Безопасность: 0 | роли на схему у обоих
pos Тестировщик: 1 | у PGO зрелее восстановление (pgBackRest)
# Что меняется
> AD-18 подтверждён; проверка восстановления — в задаче инфраструктуры
stack Документы: 3 ok, 0 part, 4 mute
- ✅ TECHNOLOGIES: MinIO — архивирован 24.04.2026 · ✅ подтверждено AD-18
```

**Почему CloudNativePG + RustFS.** Три вывода:

<div class="rnd-grid" markdown>
<div markdown>
**1. Бэкап и пулер — объекты оператора**

CloudNativePG держит непрерывный архив WAL и базовые копии в S3 вне узла и пулер PgBouncer как ресурс `Pooler`. С обычным StatefulSet из чарта [ICPlan](../architecture/components/icplan/README.md) бэкапы пришлось бы писать скриптами — это главный риск своего сервера ([AD-18](../architecture/decisions/AD-18.yaml)) ([Э9](#e9)).
</div>
<div markdown>
**2. С [ICPlan](../architecture/components/icplan/README.md) совпадает всё, кроме запуска Postgres**

[ICPlan](../architecture/components/icplan/README.md) уже работает с RustFS и pgvector. Меняется только то, как поднят Postgres: кластер CNPG вместо StatefulSet. [ICPlan](../architecture/components/icplan/README.md) подключается через PgBouncer в режиме transaction: `postgres-js` с `prepare:false`, LiteLLM — Prisma с `pgbouncer=true` ([AD-18](../architecture/decisions/AD-18.yaml)) ([Э7](#e7)).
</div>
<div markdown>
**3. Объектное хранилище — без смены**

MinIO архивирован (последний релиз — 15.10.2025). RustFS и SeaweedFS живы, но SeaweedFS потребовал бы перенастройки [ICPlan](../architecture/components/icplan/README.md). Garage интересен репликацией между площадками, но для копий вне узла хватает любого S3 ([Э4](#e4)).
</div>
</div>

<div class="rnd-grid" markdown>
<div class="take" markdown>
**Берём**

- PostgreSQL 17, одна инстанция: БД `itsaplan` (схемы `public`, `platform`, `harness_ckpt`) и `litellm`;
- CloudNativePG: WAL, копии, `Pooler`;
- RustFS (S3 API) как в [ICPlan](../architecture/components/icplan/README.md);
- pgvector из стандартного образа.
</div>
<div class="adapt" markdown>
**Адаптируем**

- восстановление на момент времени (PITR, есть у всех операторов) → проверка восстановления в задаче инфраструктуры;
- репликация между площадками (Garage) → копии вне узла — любой S3 на другой площадке ([AD-18](../architecture/decisions/AD-18.yaml)).
</div>
<div class="drop" markdown>
**Не берём**

- MinIO: архивирован;
- HA Postgres на этапах 1–3: один узел ([AD-18](../architecture/decisions/AD-18.yaml)), HA — этап 4;
- Ceph: тяжело для одного узла.
</div>
</div>

<div class="rnd-grid" markdown>
<div class="no" markdown>
**Отсеяны до сравнения**

- **MinIO** — репозиторий архивирован 24.04.2026.
- **Облачные БД и S3** — своё размещение ([AD-18](../architecture/decisions/AD-18.yaml)).
</div>
<div class="risk" markdown>
**Риски и пересмотр**

- Один экземпляр Postgres — RPO минуты за счёт WAL, HA на этапе 4.
- CloudNativePG — Trial до проверки восстановления.
- Пересмотр: восстановление из WAL не уложится в целевое время → Crunchy PGO (pgBackRest).
</div>
</div>

<div class="rnd-chain" markdown>
<div markdown>**Э1 Вопрос**<span class="gate">G1</span></div>
<div markdown>**Э2 Потребности**7 <span class="gate">G2</span></div>
<div markdown>**Э3 CNPG + RustFS**6 функций <span class="gate">G3</span></div>
<div markdown>**Э4 Альтернативы**9 <span class="gate">G4</span></div>
<div markdown>**Э5 Ценность**<span class="gate">G5</span></div>
<div markdown>**Э6 Перенос**3 MUST <span class="gate">G6</span></div>
<div markdown>**Э7 Встраивание**[I14](../architecture/components/llm-gateway/integrations/I14.yaml), [I19](../architecture/components/agent-runner/integrations/I19.yaml), [I22](../architecture/integrations/I22.yaml) <span class="gate">G7</span></div>
<div markdown>**Э8 Спор**5 ролей <span class="gate">G8</span></div>
<div markdown>**Э9 Выбор**<span class="gate">G9</span></div>
<div markdown>**Э10 Последствия**7 <span class="gate">G10</span></div>
</div>

---

Дальше — как получен ответ, этап за этапом.

## Э1. Вопрос {#e1}

**Ситуация.** [ICPlan](../architecture/components/icplan/README.md) уже использует Postgres с pgvector (`pgvector/pgvector:pg17`) и RustFS (`rustfs/rustfs:1.0.0`). Платформа добавляет свои схемы, БД LiteLLM и checkpoint.

**Осложнение.** Сервер свой ([AD-18](../architecture/decisions/AD-18.yaml)): бэкапы вне узла, восстановление и пул соединений — наша ответственность. MinIO, который часто берут для S3, перестал развиваться.

**Вопрос.** На чём держать Postgres и объекты?

**Решает:** владелец продукта с DevOps. **Не решаем:** кластер Kubernetes ([K8s](kubernetes-runtime.md)), профиль нагрузки ([нагрузка](load-profile.md)).

<span class="gate">G1</span> ✅ вопрос — выбор; есть владелец; связан с [AD-4](../architecture/decisions/AD-4.yaml), [AD-15](../architecture/decisions/AD-15.yaml), [AD-18](../architecture/decisions/AD-18.yaml).

## Э2. Потребности {#e2}

| # | Потребность | Откуда | Что ломается без неё |
|---|---|---|---|
| П1 | бэкап вне узла и восстановление на момент времени | [FR-165](../architecture/components/infrastructure/prd.md), [AD-18](../architecture/decisions/AD-18.yaml) | потеря узла = потеря данных |
| П2 | пул соединений для api [ICPlan](../architecture/components/icplan/README.md), LiteLLM, Runner, [Memory](../architecture/components/memory/README.md) | [FR-163](../architecture/components/infrastructure/prd.md) | исчерпание `max_connections` |
| П3 | совместимость с [ICPlan](../architecture/components/icplan/README.md) без перенастройки | [AD-18](../architecture/decisions/AD-18.yaml) | правки форка ради хранилища |
| П4 | pgvector для M4 и RAG позже | [AD-13](../architecture/decisions/AD-13.yaml), [FR-41](../architecture/components/memory/prd.md) | второй движок векторов |
| П5 | роль БД на схему (наименьшие права) | [FR-163](../architecture/components/infrastructure/prd.md), хранилища спек | сервис читает чужие таблицы |
| П6 | объектное хранилище S3 с живым проектом | [FR-164](../architecture/components/infrastructure/prd.md) | хранилище без обновлений безопасности |
| П7 | эксплуатация одной командой на одном узле | [AD-15](../architecture/decisions/AD-15.yaml) | тяжёлые распределённые системы |

<span class="gate">G2</span> ✅ у потребностей есть требования и решения.

## Э3. Опорное решение: CloudNativePG + RustFS {#e3}

| # | Функция | Что делает | Потребность |
|---|---|---|---|
| F1 | Кластер Postgres как ресурс K8s | оператор поднимает и обновляет Postgres | П7 |
| F2 | Архив WAL и базовые копии в S3 | восстановление на момент времени | П1 |
| F3 | Ресурс `Pooler` (PgBouncer) | пул в режиме transaction | П2 |
| F4 | Стандартный образ с pgvector | `CREATE EXTENSION vector` | П4 |
| F5 | Роли и БД декларативно | роль на схему | П5 |
| F6 | RustFS (S3 API) | вложения, артефакты, цель бэкапов | П3, П6 |

**Вывод этапа.** Опорное решение закрывает все потребности функциями оператора и тем, что уже есть в [ICPlan](../architecture/components/icplan/README.md).

<span class="gate">G3</span> ✅ функции из документации CNPG (Б) и [AD-18](../architecture/decisions/AD-18.yaml) (А).

## Э4. Альтернативы и их ключевые функции {#e4}

Поиск 11.10.2026: GitHub, CNCF Landscape (операторы баз данных, объектные хранилища).

| Кандидат | Ключевые функции | Чего нет у опорного | Уровень |
|---|---|---|---|
| **Crunchy PGO** (Apache-2.0, 4 450★, v6.0.2) | оператор Postgres; бэкапы pgBackRest (полные, разностные, PITR); PgBouncer | pgBackRest | Б |
| **Zalando postgres-operator** (MIT, 5 254★, v2.0.3) | Patroni / Spilo, логические копии, пулер | — | Б |
| **StatefulSet из чарта [ICPlan](../architecture/components/icplan/README.md)** | Postgres как обычный под; бэкапы — свои скрипты | — | А |
| **SeaweedFS** (Apache-2.0, 35 387★, 4.48) | распределённое хранилище с S3 API, много объектов | масштаб | Б |
| **Garage** (AGPL-3.0, 4 670★, v2.4.1) | лёгкий S3 с репликацией между площадками | гео-репликация | Б |
| **RustFS** (Apache-2.0, 34 706★, 1.0.1) | S3 на Rust; уже в [ICPlan](../architecture/components/icplan/README.md) | — | Б |
| **MinIO** (AGPL-3.0, 61 328★) | S3; **репозиторий архивирован 24.04.2026**, последний релиз 15.10.2025 | — | Б |
| **Ceph RGW** | S3 поверх Ceph | — | Б |
| **Облачные БД и S3** | управляемые сервисы | — | Б |

**Вывод этапа.** Операторы отличаются инструментом бэкапа (WAL в S3, pgBackRest, Patroni). Объектные хранилища — масштабом и репликацией; для одного узла хватает RustFS.

<span class="gate">G4</span> ✅ 9 кандидатов, включая «как есть»; источники трёх видов; дата есть.

## Э5. Ценность функций {#e5}

| Функция | Потребность | Почему ценна | Доказательство | Класс |
|---|---|---|---|---|
| Бэкап WAL вне узла, PITR | П1 | RPO — минуты | CNPG, PGO, Zalando (Б) | базовая |
| Пулер как ресурс | П2 | не нужен отдельный деплой | CNPG `Pooler`, PGO (Б) | базовая |
| Совместимость с [ICPlan](../architecture/components/icplan/README.md) | П3 | форк не меняется | RustFS и pgvector в [ICPlan](../architecture/components/icplan/README.md) (А) | базовая |
| Живой проект S3 | П6 | обновления безопасности | MinIO архивирован (Б) | базовая |
| pgvector в образе | П4 | без второго движка | CNPG (Б), [AD-18](../architecture/decisions/AD-18.yaml) | линейная |
| pgBackRest (разностные копии) | П1 | быстрее восстановление больших БД | PGO (Б) | линейная |
| Гео-репликация объектов | П1 | копии на другой площадке | Garage (Б) | привлекательная |
| HA Postgres | — | — | этап 4 ([AD-18](../architecture/decisions/AD-18.yaml)) | безразличная на этапах 1–3 |

**Вывод этапа.** Базовые функции у CNPG и PGO есть; у StatefulSet нет бэкапа из коробки. Объектное хранилище должно быть живым и совместимым с [ICPlan](../architecture/components/icplan/README.md).

<span class="gate">G5</span> ✅ у функций есть доказательство уровня Б и выше.

## Э6. Перенос и критерии {#e6}

| Функция | Решение | Как | Где |
|---|---|---|---|
| CNPG: WAL, копии, `Pooler`, pgvector | оставить | [AD-18](../architecture/decisions/AD-18.yaml) | [FR-163](../architecture/components/infrastructure/prd.md), [FR-165](../architecture/components/infrastructure/prd.md) |
| PITR | адаптировать | проверка восстановления на момент времени в задаче инфраструктуры | [задача 4.7](..\source\tasks\4.7-postgres-storage-backup.md) (подзадача 4.7.6) |
| Гео-репликация (Garage) | не брать | копии вне узла — любой S3 на другой площадке | [AD-18](../architecture/decisions/AD-18.yaml) |
| MinIO, HA, Ceph | не брать | Э5 | — |

**Критерии:**

| Критерий | Цепочка | Как проверяем |
|---|---|---|
| **M1** бэкап вне узла с PITR | П1 → базовая | документация оператора |
| **M2** живой проект | П6 | не архивирован |
| **M3** своё размещение | [AD-18](../architecture/decisions/AD-18.yaml) | без облака |
| **К1** совместимость с [ICPlan](../architecture/components/icplan/README.md) | П3 | что перенастраивать |
| **К2** пулер | П2 | ресурс или отдельно |
| **К3** эксплуатация на одном узле | П7 | компоненты |

<span class="gate">G6</span> ✅ у функций есть решения; критерии с цепочкой.

## Э7. Отсев и встраивание {#e7}

### Отсев по MUST

| Кандидат | M1 бэкап, PITR | M2 жив | M3 у нас | Итог |
|---|---|---|---|---|
| CloudNativePG + RustFS | да | да | да | проходит |
| Crunchy PGO + RustFS | да | да | да | проходит |
| Zalando + RustFS | да | да | да | проходит |
| CloudNativePG + SeaweedFS | да | да | да | проходит |
| StatefulSet [ICPlan](../architecture/components/icplan/README.md) + RustFS | **нет**: свои скрипты | да | да | ✗ |
| … + MinIO | да | **нет** | да | ✗ |
| Облачные сервисы | да | да | **нет** | ✗ |

### Как встаёт в схему

```
 api ICPlan, worker ─┐
 LiteLLM (Prisma) ───┼──I22──▶ PgBouncer (Pooler, transaction) ──▶ Postgres 17 (CNPG)
 Runner, Memory ─────┘                                              ├ БД itsaplan: public (S1), platform (S2–S4), harness_ckpt (S5)
                                                                    └ БД litellm (S6) ◀──I14── LiteLLM
                                    WAL + базовые копии ──▶ S3 вне узла (другая площадка)
 Runner / ICPlan ──I19 S3 API──▶ RustFS (вложения, артефакты)
```

| Стык | CNPG + RustFS | PGO + RustFS | Zalando + RustFS | CNPG + SeaweedFS |
|---|---|---|---|---|
| [I22](../architecture/integrations/I22.yaml) через PgBouncer | И2: transaction проверен по коду [ICPlan](../architecture/components/icplan/README.md) и Prisma ([AD-18](../architecture/decisions/AD-18.yaml)) | И2 | И2 | И2 |
| [I14](../architecture/components/llm-gateway/integrations/I14.yaml) LiteLLM → БД | И2 | И2 | И2 | И2 |
| [I19](../architecture/components/agent-runner/integrations/I19.yaml) S3 | И4: RustFS как в [ICPlan](../architecture/components/icplan/README.md) | И4 | И4 | И1: перенастроить [ICPlan](../architecture/components/icplan/README.md) |
| Бэкап в S3 вне узла | И2: `barmanObjectStore` | И2: pgBackRest | И2: WAL-G | И2 |

**Изменения у соседей:** при любом операторе — чарт [ICPlan](../architecture/components/icplan/README.md) подключается к внешнему кластеру вместо своего StatefulSet (техспека [ICPlan](../architecture/components/icplan/README.md), инфраструктура). При SeaweedFS — ещё и настройки S3 в [ICPlan](../architecture/components/icplan/README.md).

**Вывод этапа.** ==Все операторы встают одинаково; отличие — в инструменте бэкапа.== RustFS совпадает с [ICPlan](../architecture/components/icplan/README.md), поэтому объектное хранилище не меняем.

<span class="gate">G7</span> ✅ отсев; готовность стыков; изменения у соседей.

## Э8. Спор ролей {#e8}

Роли 🤖. Оппонент — Тестировщик за Crunchy PGO, «адвокат дьявола» атакует один экземпляр Postgres.

| Роль | За | Довод | Опасение | Согласится, если |
|---|---|---|---|---|
| DevOps 🤖 | CNPG | WAL, копии и пулер — ресурсы оператора; CNCF | — | — |
| Архитектор 🤖 | CNPG | одна инстанция для всех схем, роли на схему | — | — |
| Разработчик 🤖 | нейтрально | transaction-режим проверен по коду [ICPlan](../architecture/components/icplan/README.md) и Prisma | миграции через пулер | миграции — прямым подключением ([AD-18](../architecture/decisions/AD-18.yaml)) |
| Безопасность 🤖 | нейтрально | роли на схему у всех операторов | — | — |
| Тестировщик 🤖 (оппонент) | Crunchy PGO | pgBackRest зрелее для восстановления | восстановление не проверено | проверка PITR в задаче бэкапов |

| Спор | Разрешение |
|---|---|
| Тестировщик: «восстановление не проверено» | **условие:** CNPG — Trial до проверки PITR в задаче бэкапов; провал → PGO |
| Адвокат дьявола: «один экземпляр — единая точка отказа» | **условие:** RPO минуты за счёт WAL, HA — этап 4 ([AD-18](../architecture/decisions/AD-18.yaml)) |

**Вывод этапа.** Спор о восстановлении сведён к проверке; статус CNPG — Trial до неё.

<span class="gate">G8</span> ✅ у каждого спора есть разрешение.

## Э9. Выбор {#e9}

| Потребность | CNPG + RustFS | PGO + RustFS | Zalando + RustFS | CNPG + SeaweedFS | StatefulSet |
|---|---|---|---|---|---|
| П1 бэкап, PITR | закрывает | закрывает | закрывает | закрывает | не закрывает |
| П2 пулер | закрывает | закрывает | закрывает | закрывает | с доработкой |
| П3 совместимость с [ICPlan](../architecture/components/icplan/README.md) | закрывает | закрывает | закрывает | частично: S3 | закрывает |
| П4 pgvector | закрывает | закрывает: свой образ | частично: Spilo | закрывает | закрывает |
| П5 роли на схему | закрывает | закрывает | закрывает | закрывает | с доработкой |
| П6 живой S3 | закрывает | закрывает | закрывает | закрывает | закрывает |
| П7 один узел, одна команда | закрывает | с доработкой: больше компонентов | частично: Patroni | закрывает | закрывает |

- **Утверждение.** PostgreSQL 17 под CloudNativePG и RustFS ([AD-18](../architecture/decisions/AD-18.yaml)).
- **Основания.** Закрывает все 7 потребностей; совпадает с [ICPlan](../architecture/components/icplan/README.md) по S3 и pgvector.
- **Связка.** Бэкап вне узла — главная обязанность своего сервера. Операторы дают его из коробки, а CNPG проще на одном узле.
- **Опровержение.** Вывод неверен, если проверка PITR покажет, что восстановление не укладывается в целевое время. Тогда — Crunchy PGO с pgBackRest.

<span class="gate">G9</span> ✅ вывод следует из покрытия, встраивания и спора; есть опровержение.

## Э10. Последствия {#e10}

| Изменение | Документ | Статус |
|---|---|---|
| MinIO — архивирован 24.04.2026 | [TECHNOLOGIES](..\source\TECHNOLOGIES.md) | ✅ внесено |
| CloudNativePG — Trial до проверки PITR; проверка — на момент времени, с замером времени восстановления | TECHNOLOGIES, [задача 4.7](..\source\tasks\4.7-postgres-storage-backup.md) | ✅ внесено: уточнена подзадача 4.7.6 |
| Решения [AD-4](../architecture/decisions/AD-4.yaml), [AD-15](../architecture/decisions/AD-15.yaml), [AD-18](../architecture/decisions/AD-18.yaml) | design | ✅ подтверждено, без изменений |
| Стыки [I14](../architecture/components/llm-gateway/integrations/I14.yaml), [I19](../architecture/components/agent-runner/integrations/I19.yaml), [I22](../architecture/integrations/I22.yaml) | спека platform-infrastructure | — не требуется |
| Бэкапы и восстановление | [FR-165](../architecture/components/infrastructure/prd.md) | — не требуется: PITR уже в требовании |
| Техспека инфраструктуры | [техспека](..\architecture\components\infrastructure\docs\techspec.md) | — не требуется |
| Поток инфраструктуры | [поток](..\architecture\components\infrastructure\docs\how.md) | — не требуется |

<span class="gate">G10</span> ✅ у каждого изменения есть документ и статус.

<details markdown>
<summary>Приложение A. Карточки кандидатов</summary>

GitHub API на 11.10.2026.

| Технология | Лицензия | ★ | Релиз | Активность |
|---|---|---|---|---|
| MinIO | AGPL-3.0 | 61 328 | RELEASE.2025-10-15 | **архивирован**, 24.04.2026 |
| SeaweedFS | Apache-2.0 | 35 387 | 4.48 | 11.10.2026 |
| RustFS | Apache-2.0 | 34 706 | 1.0.1 | 11.10.2026 |
| pgvector | PostgreSQL | 23 300 | — | 08.10.2026 |
| CloudNativePG | Apache-2.0 | 9 425 | v1.30.1 | 10.10.2026 |
| Zalando postgres-operator | MIT | 5 254 | v2.0.3 | 02.10.2026 |
| Garage | AGPL-3.0 | 4 670 | v2.4.1 | 08.10.2026 |
| Crunchy PGO | Apache-2.0 | 4 450 | v6.0.2 | 07.10.2026 |
</details>

## Источники

Поиск и чтение — 11.10.2026; в скобках уровень доказательства.

- [CloudNativePG](https://github.com/cloudnative-pg/cloudnative-pg) (Б) · [Crunchy PGO](https://github.com/CrunchyData/postgres-operator) (Б) · [Zalando postgres-operator](https://github.com/zalando/postgres-operator) (Б)
- [RustFS](https://github.com/rustfs/rustfs) (Б) · [SeaweedFS](https://github.com/seaweedfs/seaweedfs) (Б) · [Garage](https://github.com/deuxfleurs-org/garage) (Б) · [MinIO — архивирован](https://github.com/minio/minio) (Б) · [pgvector](https://github.com/pgvector/pgvector) (Б)
- Наши: [AD-4, AD-15, AD-18](..\source\design\define-agent-platform\design.md) (А)
