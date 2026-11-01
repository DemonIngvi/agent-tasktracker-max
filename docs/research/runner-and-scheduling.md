# R&D: Runner и очередь запусков

← [Все R&D](README.md) · методология R&D v3.1 · компонент: **[Agent Runner](../architecture/components/agent-runner/README.md)** · решение: [design AD-8, AD-14](..\source\design\define-agent-platform\design.md) · спека: agent-runner

<div class="rnd-hero" markdown>
<div class="rnd-q">Вопрос</div>
Кто забирает запуски из очереди [ICPlan](../architecture/components/icplan/README.md) и как решает, когда их стартовать — с лимитами на модель, агента и задачу, без простоя слотов на ожидании подтверждения?

<div class="rnd-a">Ответ: свой [Agent Runner](../architecture/components/agent-runner/README.md) на Go как внешний раннер [ICPlan](../architecture/components/icplan/README.md) и свои слоты в Postgres. Внешний движок очередей не берём: очередь уже есть в [ICPlan](../architecture/components/icplan/README.md), а движок стал бы второй очередью.</div>

<span class="rnd-badge adopt">Adopt</span> Go · слоты в S3 (Postgres [ICPlan](../architecture/components/icplan/README.md)) · 0 $ · данные 11.10.2026
</div>

```deck
# Покрытие потребностей П1–П9
> слоты в Postgres закрывают всё без нового сервиса; движки закрывают с доработкой и новой инфраструктурой
stack Свои слоты в Postgres: 8 ok, 1 part, 0 no
stack Hatchet: 6 ok, 2 part, 1 no
stack River + Pro: 6 ok, 2 part, 1 no
stack Temporal: 5 ok, 3 part, 1 no
stack Kueue (этап 4): 3 ok, 3 part, 3 no
stack Очередь на агента: 4 ok, 1 part, 4 no
# Новая инфраструктура
> свои слоты — 0 новых сервисов; Temporal — кластер
bar Свои слоты: 0/4 новых сервисов ok
bar River + Pro: 0/4 платная лицензия part
bar Hatchet: 2/4 движок + своя БД no
bar Temporal: 4/4 кластер из 4 служб + БД no
# Объём доработки
> выбранный вариант (свои слоты в Postgres) — задача 2.7, 31 ч ≈ 3.9 дн; движки не оценены — отсеяны по новой инфраструктуре
bar 2.7.1 конфиг scheduling и валидация: 3/31 ч ok
bar 2.7.2 слоты и проверка «все свободны»: 6/31 ч ok
bar 2.7.3 queued, порядок fifo / priority: 4/31 ч ok
bar 2.7.4 общие слоты в Postgres, scheduler_slot: 6/31 ч ok
bar 2.7.5 причина ожидания в событиях: 3/31 ч ok
bar 2.7.6 тесты сценариев приёмки: 5/31 ч ok
bar 2.7.7 конкурентный тест и голодание: 4/31 ч ok
# Позиции ролей
side Свои слоты | Hatchet
pos DevOps: -2 | без новых сервисов
pos Архитектор: -2 | очередь одна — в ICPlan
pos Владелец продукта: -1 | без платных лицензий
pos Разработчик: 1 | гонки слотов писать самим
pos Тестировщик: 1 | готовый движок проверен
# Что меняется
> AD-8 и AD-14 подтверждены; в задачу 2.7 добавлен тест гонок и голодания
stack Документы: 5 ok, 0 part, 3 mute
- ✅ задача 2.7: конкурентный тест слотов и проверка `aging_s`
- ✅ design AD-14: альтернативы · ✅ бэклог: справедливая доля проектов (Kueue)
```

**Почему свой Runner со слотами.** Три вывода:

<div class="rnd-grid" markdown>
<div markdown>
**1. Очередь уже есть — в [ICPlan](../architecture/components/icplan/README.md)**

[ICPlan](../architecture/components/icplan/README.md) держит очередь каждого агента с арендой (`claim → heartbeat → result`, аренда 300 с). Runner забирает запуск и решает только одно — **когда стартовать**. Внешний движок (Hatchet, Temporal) стал бы второй очередью с двойным учётом статусов ([Э7](#e7)).
</div>
<div markdown>
**2. Лимит на модель и на задачу — наша специфика**

Запуск стартует, когда свободны все его слоты: глобальный, агента, модели и задачи. Лимит модели — это rate limit ключа провайдера, общий для всех агентов. Ключи параллельности по выражению это умеют только в Hatchet и River Pro, а River Pro платный ([Э4](#e4)).
</div>
<div markdown>
**3. Цена своих слотов — тесты на гонки**

Своя логика слотов — главный риск. Он закрывается конкурентным тестом: несколько Runner и много запусков, лимиты не превышены ни разу. Голодание закрывает повышение приоритета `aging_s` ([AD-18](../architecture/decisions/AD-18.yaml)). Тест добавлен в задачу 2.7 ([Э10](#e10)).
</div>
</div>

<div class="rnd-grid" markdown>
<div class="take" markdown>
**Берём**

- протокол раннера [ICPlan](../architecture/components/icplan/README.md): pull, аренда, heartbeat;
- слоты: глобальный, агента, модели, задачи;
- аренду слотов в Postgres — упавший Runner освобождает их по сроку;
- статусы запуска [FR-72](../architecture/components/agent-runner/prd.md).
</div>
<div class="adapt" markdown>
**Адаптируем**

- ключ параллельности по выражению (Hatchet) → ключи слотов `agent`, `model`, `issue`;
- «очередь с распределением по кругу между ключами» (Hatchet) → порядок `fifo` / `priority` с `aging_s`;
- справедливую долю по истории использования (Kueue) → в бэклог: доля проектов.
</div>
<div class="drop" markdown>
**Не берём**

- «отменить идущий запуск ради нового» (Hatchet): теряется работа агента;
- durable workflow (Temporal): процесс ведёт [ICPlan](../architecture/components/icplan/README.md) ([AD-17](../architecture/decisions/AD-17.yaml));
- `@itsaplan/runner` как исполнитель: нет изоляции, LiteLLM и guardrails;
- River Pro: платная лицензия ради одной функции.
</div>
</div>

<div class="rnd-grid" markdown>
<div class="no" markdown>
**Отсеяны до сравнения**

- **`@itsaplan/runner` как есть** — исполняет агента без sandbox, LiteLLM и G1.
- **Очередь на агента без общих слотов** — нет лимита на модель и общей ёмкости.
</div>
<div class="risk" markdown>
**Риски и пересмотр**

- Гонки слотов — конкурентный тест в 2.7.
- Пересмотр: на этапе 4 (Kubernetes) — Kueue для ёмкости узлов поверх наших слотов модели.
</div>
</div>

<div class="rnd-chain" markdown>
<div markdown>**Э1 Вопрос**<span class="gate">G1</span></div>
<div markdown>**Э2 Потребности**9 <span class="gate">G2</span></div>
<div markdown>**Э3 Раннер [ICPlan](../architecture/components/icplan/README.md)**6 функций <span class="gate">G3</span></div>
<div markdown>**Э4 Альтернативы**7 <span class="gate">G4</span></div>
<div markdown>**Э5 Ценность**<span class="gate">G5</span></div>
<div markdown>**Э6 Перенос**3 MUST <span class="gate">G6</span></div>
<div markdown>**Э7 Встраивание**[I1](../architecture/components/agent-runner/integrations/I1.yaml)–[I7](../architecture/components/agent-runner/integrations/I7.yaml), [I22](../architecture/integrations/I22.yaml) <span class="gate">G7</span></div>
<div markdown>**Э8 Спор**6 ролей <span class="gate">G8</span></div>
<div markdown>**Э9 Выбор**<span class="gate">G9</span></div>
<div markdown>**Э10 Последствия**8 <span class="gate">G10</span></div>
</div>

---

Дальше — как получен ответ, этап за этапом.

## Э1. Вопрос {#e1}

**Ситуация.** [ICPlan](../architecture/components/icplan/README.md) ставит запуски агентов в очередь и отдаёт их внешним раннерам по протоколу `@itsaplan/runner` ([AD-8](../architecture/decisions/AD-8.yaml)). Агентов несколько, они делят модели с лимитами провайдера.

**Осложнение.** Раннер [ICPlan](../architecture/components/icplan/README.md) из коробки исполняет агента без изоляции. Очереди с лимитами есть в готовых движках (Hatchet, Temporal, River), но у нас очередь уже есть в [ICPlan](../architecture/components/icplan/README.md).

**Вопрос.** Кто исполняет запуски и как решает, когда их стартовать?

**Решает:** владелец продукта по предложению архитектора. **Не решаем:** изоляцию среды ([Sandbox](sandbox-isolation.md)), цикл агента ([фреймворк](harness-framework.md)), переход на Kubernetes ([K8s](kubernetes-runtime.md)).

<span class="gate">G1</span> ✅ вопрос — выбор; есть владелец; связан с [AD-8](../architecture/decisions/AD-8.yaml), [AD-14](../architecture/decisions/AD-14.yaml) и требованиями agent-runner.

## Э2. Потребности {#e2}

| # | Потребность | Откуда | Что ломается без неё |
|---|---|---|---|
| П1 | брать запуски из очереди [ICPlan](../architecture/components/icplan/README.md) по протоколу раннера: pull, аренда, heartbeat | [FR-66](../architecture/components/agent-runner/prd.md), [I1](../architecture/components/agent-runner/integrations/I1.yaml)–[I3](../architecture/components/agent-runner/integrations/I3.yaml), [AD-8](../architecture/decisions/AD-8.yaml) | [ICPlan](../architecture/components/icplan/README.md) пришлось бы менять под исполнителя |
| П2 | лимиты: глобальный, на агента, на модель, на задачу | [FR-67](../architecture/components/agent-runner/prd.md), [FR-70](../architecture/components/agent-runner/prd.md) | провайдер режет запросы, гонки в задаче |
| П3 | переключатель «всё последовательно / параллельно» | [FR-68](../architecture/components/agent-runner/prd.md) | нельзя разобрать проблему по одному запуску |
| П4 | ожидание подтверждения не держит слоты | [FR-69](../architecture/components/agent-runner/prd.md) | подтверждение на 24 ч блокирует ёмкость |
| П5 | общие слоты для нескольких Runner, освобождение по аренде | [FR-71](../architecture/components/agent-runner/prd.md) | два Runner превышают лимит вдвое |
| П6 | изоляция запуска и допуск G1 до старта | [I5](../architecture/components/agent-runner/integrations/I5.yaml), [I6](../architecture/components/agent-runner/integrations/I6.yaml), [FR-110](../architecture/components/guardrails/prd.md) | агент исполняется на узле без защиты |
| П7 | статусы, результат, отмена, очистка среды | [FR-72](../architecture/components/agent-runner/prd.md) – [FR-75](../architecture/components/agent-runner/prd.md) | [ICPlan](../architecture/components/icplan/README.md) не знает, что с запуском |
| П8 | без новой инфраструктуры на этапе 2 | [AD-15](../architecture/decisions/AD-15.yaml), [профиль нагрузки](load-profile.md) | ещё один сервис в эксплуатации |
| П9 | приоритет без голодания | `scheduling.order`, `aging_s` ([AD-18](../architecture/decisions/AD-18.yaml)) | низкий приоритет не стартует никогда |

<span class="gate">G2</span> ✅ у каждой потребности есть требование или решение.

## Э3. Опорное решение: раннер ICPlan {#e3}

Опорное решение — то, что есть в [ICPlan](../architecture/components/icplan/README.md): очередь запусков и раннер `@itsaplan/runner`.

| # | Функция | Что делает | Потребность |
|---|---|---|---|
| F1 | Очередь запусков агента | порядок по приоритету, затем по времени ([AD-17](../architecture/decisions/AD-17.yaml)) | П1, П9 |
| F2 | Аренда запуска | `claim` выдаёт запуск на 300 с; `heartbeat` продлевает; повтор до 3 попыток | П1, П5 |
| F3 | Возврат итога | `result` со статусом `success` / `failed` / `canceled` | П7 |
| F4 | Отмена через heartbeat | `heartbeat` возвращает `false`, если запуск больше не активен | П7 |
| F5 | Ключ агента | раннер обслуживает агентов по их API-ключам | П1 |
| F6 | Исполнение агента | раннер запускает агента локально | П6 ✗: без sandbox, LiteLLM, G1 |

**Вывод этапа.** Протокол [ICPlan](../architecture/components/icplan/README.md) (F1–F5) закрывает получение работы и возврат итога. Исполнение (F6) и слоты (П2–П5) — то, чего нет.

<span class="gate">G3</span> ✅ функции из кода [ICPlan](../architecture/components/icplan/README.md) (А) и протокола раннера (Б).

## Э4. Альтернативы и их ключевые функции {#e4}

Поиск 11.10.2026: GitHub (job queue, workflow engine, Go, Postgres), документация движков, CNCF Landscape (Kueue). Celery исключён без разбора: Python-очередь с брокером, а Runner на Go ([AD-3](../architecture/decisions/AD-3.yaml)).

| Кандидат | Ключевые функции | Чего нет в опорном решении | Уровень |
|---|---|---|---|
| **Свой Runner + слоты в Postgres** | слоты глобальный / агента / модели / задачи; аренда слотов; режимы; `aging_s` | слоты, изоляция, G1 | А ([AD-14](../architecture/decisions/AD-14.yaml)) |
| **Hatchet** (MIT, 8 099★, v0.110.5) | ключ параллельности — выражение CEL от входа; `max_runs` на ключ; стратегии: распределение по кругу между ключами, отмена идущего, отмена новых; лимиты частоты | ключ по выражению, стратегии конфликта | Б |
| **River** (Go + Postgres, MPL-2.0, 5 765★) | очередь в Postgres, постановка в транзакции; лимиты параллельности глобальные и по аргументам — **только River Pro (платно)** | лимит по аргументам | Б |
| **Temporal** (MIT, 23 596★, v1.32.1) | durable workflow, ожидание сигналов днями, повторы | долгие процессы с ожиданиями | Б |
| **Kueue** (Apache-2.0, 3 051★, v0.20.1) | квоты ресурсов ClusterQueue, допуск Job по квоте, вытеснение, справедливая доля по истории использования | справедливая доля | Б |
| **Очередь на агента** ([ICPlan](../architecture/components/icplan/README.md) как есть + свой исполнитель) | каждый агент берёт свои запуски по одному | — | А |
| **`@itsaplan/runner` как есть** | исполнение без изоляции | — | Б |

**Вывод этапа.** Лимит по ключу есть у Hatchet и River Pro, справедливая доля — у Kueue, долгие ожидания — у Temporal. Но все движки держат **свою** очередь, а у нас она в [ICPlan](../architecture/components/icplan/README.md).

<span class="gate">G4</span> ✅ 7 кандидатов, включая «сделать самим» и «как есть»; источники трёх видов; дата есть.

## Э5. Ценность функций {#e5}

| Функция | Потребность | Почему ценна | Доказательство | Класс |
|---|---|---|---|---|
| Pull-протокол [ICPlan](../architecture/components/icplan/README.md) с арендой | П1 | [ICPlan](../architecture/components/icplan/README.md) не меняется ради исполнителя | [AD-8](../architecture/decisions/AD-8.yaml); код [ICPlan](../architecture/components/icplan/README.md) (А) | базовая |
| Изоляция и G1 до старта | П6 | агент — недоверенный код | [AD-18](../architecture/decisions/AD-18.yaml), [FR-110](../architecture/components/guardrails/prd.md) (А) | базовая |
| Лимит по ключу (модель, задача) | П2 | rate limit провайдера общий для всех агентов | Hatchet, River Pro (Б); `models.<alias>.max` (А) | базовая |
| Аренда слотов в общей БД | П5 | упавший экземпляр не держит ёмкость | River и Hatchet на Postgres (Б); [FR-71](../architecture/components/agent-runner/prd.md) (А) | базовая |
| Освобождение слота на ожидании | П4 | подтверждение ждёт до 24 ч | [FR-69](../architecture/components/agent-runner/prd.md) (А) | базовая |
| Распределение по кругу между ключами | П9 | ни один ключ не голодает | Hatchet (Б) | линейная |
| Повышение приоритета ждущего (aging) | П9 | низкий приоритет стартует за ~30 мин | [AD-18](../architecture/decisions/AD-18.yaml) (А) | линейная |
| Справедливая доля по истории использования | П9 | проект, который много потребил, уступает | Kueue (Б) | привлекательная |
| Отмена идущего ради нового | — | — | теряется работа агента; [FR-70](../architecture/components/agent-runner/prd.md): второй ждёт | обратная |
| Durable workflow | — | — | процесс задачи ведёт [ICPlan](../architecture/components/icplan/README.md) ([AD-17](../architecture/decisions/AD-17.yaml)) | безразличная |
| Новый сервис очередей | П8 | — | ещё одна система в эксплуатации | обратная на этапе 2 |

**Вывод этапа.** Базовые функции: pull-протокол, изоляция, лимит по ключу, аренда слотов и освобождение на ожидании. Справедливая доля — привлекательная на будущее.

<span class="gate">G5</span> ✅ у функций есть доказательство уровня Б и выше.

## Э6. Перенос и критерии {#e6}

| Функция | Решение | Как | Где |
|---|---|---|---|
| Протокол раннера [ICPlan](../architecture/components/icplan/README.md) | брать | клиент протокола в Runner | [FR-66](../architecture/components/agent-runner/prd.md), задача 2.1 |
| Слоты по ключам | адаптировать | ключи `global`, `agent`, `model`, `issue` в таблице `scheduler_slot` (S3) | [FR-67](../architecture/components/agent-runner/prd.md), задача 2.7 |
| Аренда слотов | брать | срок аренды; упавший Runner освобождает по сроку | [FR-71](../architecture/components/agent-runner/prd.md) |
| Распределение по кругу | адаптировать | `fifo` / `priority` + `aging_s` | [FR-67](../architecture/components/agent-runner/prd.md), [AD-18](../architecture/decisions/AD-18.yaml) |
| Справедливая доля (Kueue) | не брать сейчас | в бэклог: доля проектов по истории | [BACKLOG](..\source\BACKLOG.md) |
| Отмена идущего ради нового | не брать | второй запуск ждёт ([FR-70](../architecture/components/agent-runner/prd.md)) | — |
| Durable workflow, новый сервис очередей | не брать | процесс в [ICPlan](../architecture/components/icplan/README.md), П8 | — |

**Критерии:**

| Критерий | Цепочка | Как проверяем |
|---|---|---|
| **M1** работает поверх очереди [ICPlan](../architecture/components/icplan/README.md) (pull) | П1 → базовая | не требует менять [ICPlan](../architecture/components/icplan/README.md) |
| **M2** изоляция и G1 до старта | П6 → базовая | запуск в sandbox после G1 |
| **M3** лимит на модель и на задачу | П2 → базовая | ключ параллельности |
| **К1** без новой инфраструктуры | П8 | сколько новых сервисов |
| **К2** общие слоты и аренда | П5 | несколько экземпляров, освобождение |
| **К3** ожидание без слота | П4 | слот освобождается на `waiting_approval` |
| **К4** приоритет без голодания | П9 | aging, распределение |
| **К5** сколько своего кода и риск гонок | П2–П5 | что писать, как проверить |

<span class="gate">G6</span> ✅ у функций есть решения; критерии с цепочкой.

## Э7. Отсев и встраивание {#e7}

### Отсев по MUST

| Кандидат | M1 поверх [ICPlan](../architecture/components/icplan/README.md) | M2 изоляция и G1 | M3 лимит модели и задачи | Итог |
|---|---|---|---|---|
| Свой Runner + слоты | да | да | да | проходит |
| Свой Runner + Hatchet | да: Runner кладёт в Hatchet | да | да: ключ CEL | проходит |
| Свой Runner + River Pro | да | да | да: `ByArgs` | проходит |
| Свой Runner + Temporal | да | да | частично: своими средствами | проходит |
| Kueue (этап 4) | да | да | частично: квоты ресурсов, не моделей | проходит |
| Очередь на агента | да | да | **нет**: нет общих лимитов | ✗ |
| `@itsaplan/runner` как есть | да | **нет** | **нет** | ✗ |

### Как встаёт в схему

```
 ICPlan api ◀──I1 claim / I2 итог / I3 отмена, указания──▶ Agent Runner (Go) ──I4──▶ Platform module
                                                              │   │   └──I5──▶ OPA (G1)
                                     слоты* ──I22──▶ Postgres S3 (scheduler_slot)  │
                                                              │   └──I6 / I23──▶ Docker / K8s → sandbox
                                                              └──I7──▶ Harness ──I12 checkpoint──▶ Runner → S5
  * — слоты: своя таблица; при движке появилась бы вторая очередь между I1 и I6
```

| Стык | Свои слоты | Hatchet | River Pro | Temporal | Kueue |
|---|---|---|---|---|---|
| [I1](../architecture/components/agent-runner/integrations/I1.yaml)–[I3](../architecture/components/agent-runner/integrations/I3.yaml) очередь [ICPlan](../architecture/components/icplan/README.md) | И2: протокол описан | И1: Runner — и клиент [ICPlan](../architecture/components/icplan/README.md), и производитель Hatchet | И2 | И1 | И2 |
| Слоты / очередь движка | И2: таблица в S3 | И1: свой движок и БД | И2: таблицы в Postgres | И1: кластер | И1: объекты K8s |
| [I6](../architecture/components/agent-runner/integrations/I6.yaml) / [I23](../architecture/components/agent-runner/integrations/I23.yaml) запуск среды | И2 | И2: воркер Hatchet создаёт среду | И2 | И1: activity | И1: только Job в K8s |
| Статусы [FR-72](../architecture/components/agent-runner/prd.md) | И2: одна модель | И1: статусы Hatchet + [ICPlan](../architecture/components/icplan/README.md) | И2 | И1 | И1 |

**Изменения у соседей:**

| Кандидат | Что меняется |
|---|---|
| Свои слоты | ничего: спроектировано в [AD-14](../architecture/decisions/AD-14.yaml) |
| River Pro | лицензия River Pro в TECHNOLOGIES |
| Hatchet | спека инфраструктуры (движок, его БД), техспека, FMEA Runner (отказ движка), профиль нагрузки |
| Temporal | то же, плюс кластер из нескольких служб |
| Kueue | только на этапе 4: установка в K8s, лимит модели остаётся у нас |

**Вывод этапа.** ==Движки очередей добавляют вторую очередь между [ICPlan](../architecture/components/icplan/README.md) и средой и меняют инфраструктуру; свои слоты встают без изменений у соседей.== Kueue полезен позже — для ёмкости узлов в Kubernetes.

<span class="gate">G7</span> ✅ отсев; готовность стыков; изменения у соседей.

## Э8. Спор ролей {#e8}

Роли 🤖. Оппонент защищает Hatchet, «адвокат дьявола» атакует свои слоты.

| Роль | За | Довод | Опасение | Согласится, если |
|---|---|---|---|---|
| DevOps 🤖 | свои слоты | без новых сервисов (Э7) | — | — |
| Архитектор 🤖 | свои слоты | очередь одна — в [ICPlan](../architecture/components/icplan/README.md); статусы в одной модели | — | — |
| Владелец продукта 🤖 | свои слоты | без платной River Pro и без кластера Temporal | сроки задачи 2.7 | оценка 2.7 в пределах 3–4 дн |
| Безопасность 🤖 | нейтрально | изоляция и G1 одинаковы | — | — |
| Разработчик 🤖 (оппонент) | Hatchet | ключи CEL и стратегии готовы, меньше своего кода | гонки при захвате слотов | конкурентный тест в 2.7 |
| Тестировщик 🤖 | Hatchet | движок проверен в эксплуатации | голодание низкого приоритета | тест `aging_s` в 2.7 |

| Спор | Разрешение |
|---|---|
| Адвокат дьявола: «своя логика слотов — гонки и двойной старт» | ✅ **внесено:** подзадача 2.7.7 — конкурентный тест (3 Runner × 50 запусков, лимиты не превышены) |
| Тестировщик: «низкий приоритет голодает» | ✅ **внесено:** в 2.7.7 — проверка `aging_s`; параметр уже в [AD-18](../architecture/decisions/AD-18.yaml) |
| Разработчик: «Hatchet меньше кода» | **условие:** пересмотр, если 2.7 выйдет за 5 дн или тест гонок не удастся сделать стабильным |

**Вывод этапа.** Возражения Разработчика и Тестировщика сняты тестом в 2.7 и условием пересмотра.

<span class="gate">G8</span> ✅ у каждого спора есть разрешение.

## Э9. Выбор {#e9}

| Потребность | Свои слоты | Hatchet | River Pro | Temporal | Kueue |
|---|---|---|---|---|---|
| П1 поверх [ICPlan](../architecture/components/icplan/README.md) | закрывает | с доработкой: вторая очередь | закрывает | с доработкой | закрывает |
| П2 лимиты по ключам | закрывает | закрывает | закрывает | частично | частично: ресурсы, не модели |
| П3 последовательно / параллельно | закрывает | закрывает | закрывает | закрывает | частично |
| П4 ожидание без слота | закрывает | с доработкой | с доработкой | закрывает | не закрывает: Job занимает квоту |
| П5 общие слоты, аренда | закрывает | закрывает | закрывает | закрывает | закрывает |
| П6 изоляция и G1 | закрывает | закрывает | закрывает | закрывает | закрывает |
| П7 статусы, отмена | закрывает | частично: две модели статусов | закрывает | частично | частично |
| П8 без новой инфраструктуры | закрывает | не закрывает | частично: платная лицензия | не закрывает | не закрывает на этапе 2 |
| П9 без голодания | с доработкой: `aging_s` | закрывает | закрывает | закрывает | закрывает |

- **Утверждение.** Свой [Agent Runner](../architecture/components/agent-runner/README.md) на Go со слотами в Postgres ([AD-8](../architecture/decisions/AD-8.yaml), [AD-14](../architecture/decisions/AD-14.yaml)).
- **Основания.** Закрывает 8 из 9 потребностей без нового сервиса. Очередь остаётся одна — в [ICPlan](../architecture/components/icplan/README.md). Соседи не меняются.
- **Связка.** Движки решают задачу очереди, которую уже решает [ICPlan](../architecture/components/icplan/README.md). От них нужна только логика лимитов по ключу, а её объём меньше, чем эксплуатация нового сервиса.
- **Опровержение.** Вывод неверен, если задача 2.7 выйдет за 5 дн или тест гонок окажется нестабильным. Тогда переходим на Hatchet (или River Pro, если лицензия приемлема).

<span class="gate">G9</span> ✅ вывод следует из покрытия, встраивания и спора; есть опровержение.

## Э10. Последствия {#e10}

| Изменение | Документ | Статус |
|---|---|---|
| Конкурентный тест слотов и проверка `aging_s` | [задача 2.7](..\source\tasks\2.7-runner-scheduler.md) (подзадача 2.7.7) | ✅ внесено |
| Альтернативы в решении [AD-14](../architecture/decisions/AD-14.yaml): Hatchet, River Pro, Temporal, Kueue | [design AD-14](..\source\design\define-agent-platform\design.md) | ✅ внесено |
| Справедливая доля проектов по истории использования (Kueue) | [BACKLOG](..\source\BACKLOG.md) | ✅ внесено в бэклог |
| Kueue для ёмкости узлов на этапе 4 | [R&D Kubernetes](kubernetes-runtime.md) | ✅ учтено при переводе R&D Kubernetes |
| Решения [AD-8](../architecture/decisions/AD-8.yaml), [AD-14](../architecture/decisions/AD-14.yaml) | design | ✅ подтверждено, без изменений |
| Слоты и аренда | спека agent-runner ([FR-67](../architecture/components/agent-runner/prd.md) – [FR-71](../architecture/components/agent-runner/prd.md)) | — не требуется |
| Стыки [I1](../architecture/components/agent-runner/integrations/I1.yaml)–[I7](../architecture/components/agent-runner/integrations/I7.yaml), [I22](../architecture/integrations/I22.yaml) | спека agent-runner, [поток Runner](..\architecture\components\agent-runner\docs\how.md) | — не требуется |
| Техспека Runner | [техспека](..\architecture\components\agent-runner\docs\techspec.md) | — не требуется |

<span class="gate">G10</span> ✅ у каждого изменения есть документ и статус.

<details markdown>
<summary>Приложение A. Карточки кандидатов</summary>

GitHub API на 11.10.2026.

| Технология | Лицензия | ★ | Релиз | Активность |
|---|---|---|---|---|
| It's a Plan (протокол раннера) | AGPL-3.0 | 926 | v1.4.0 | 11.10.2026 |
| Temporal | MIT | 23 596 | v1.32.1 | 10.10.2026 |
| Hatchet | MIT | 8 099 | v0.110.5 | 10.10.2026 |
| River | MPL-2.0 (Pro — коммерческая) | 5 765 | — | 11.10.2026 |
| Kueue | Apache-2.0 | 3 051 | v0.20.1 | 09.10.2026 |
</details>

## Источники

Поиск и чтение — 11.10.2026; в скобках уровень доказательства.

- [ICPlan](../architecture/components/icplan/README.md): [протокол раннера](https://github.com/croffasia/itsaplan/blob/main/docs/runner.md) (Б); код форка — маршруты `agent-runs`, `AGENT_RUN_LEASE_SECONDS` (А)
- Hatchet: [параллельность и ключи](https://docs.hatchet.run/home/concurrency) (Б), [репозиторий](https://github.com/hatchet-dev/hatchet) (Б)
- River: [лимиты параллельности — River Pro](https://riverqueue.com/docs/pro/concurrency-limits) (Б), [обзор River](https://brandur.org/river) (В)
- Temporal: [репозиторий](https://github.com/temporalio/temporal) (Б)
- Kueue: [ClusterQueue](https://kueue.sigs.k8s.io/docs/concepts/cluster_queue) (Б), [справедливая доля](https://kueue.sigs.k8s.io/docs/concepts/fair_sharing/) (Б), [вытеснение](https://kueue.sigs.k8s.io/docs/concepts/preemption/) (Б)
- Решения: [AD-8, AD-14, AD-17, AD-18](..\source\design\define-agent-platform\design.md) (А)
