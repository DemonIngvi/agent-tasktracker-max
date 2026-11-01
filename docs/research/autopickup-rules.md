# R&D: Автоподхват задач агентом

← [Все R&D](README.md) · методология R&D v3.1 · компонент: **[ICPlan](../architecture/components/icplan/README.md)** · решение: [design AD-17](..\source\design\define-agent-platform\design.md) · спека: icplan-agent-autopickup · поток: процесс задачи

<div class="rnd-hero" markdown>
<div class="rnd-q">Вопрос</div>
Как задача, пришедшая в шаг процесса, сама попадает к агенту, а после его работы — в следующий шаг: без кода, однозначно и с контролем человека?

<div class="rnd-a">Ответ: процесс задаёт тип задачи. Шаг = колонка + агент + переходы при успехе и при неудаче + лимит попыток + проверка человеком. Переход делает [ICPlan](../architecture/components/icplan/README.md) по итогу запуска, агент берёт задачи из своей очереди ([AD-17](../architecture/decisions/AD-17.yaml)).</div>

<span class="rnd-badge adopt">Adopt</span> доработка форка [ICPlan](../architecture/components/icplan/README.md) (задачи 3.1, 3.6) · AGPL-3.0 · 0 $ · данные 11.10.2026
</div>

```deck
# Покрытие потребностей П1–П8
> процесс в ICPlan закрывает всё; внешний оркестратор силён, но процесс уходит из трекера
stack Процесс типа задачи в ICPlan: 8 ok, 0 part, 0 no
stack Внешний оркестратор (n8n, Temporal): 5 ok, 1 part, 2 no
stack Автоназначение + отдельный триггер: 3 ok, 3 part, 2 no
stack Ручное делегирование: 5 ok, 0 part, 3 no
# Кто переводит задачу
> переход по итогу запуска делает ICPlan — одно место решения
bar Процесс в ICPlan: 1/1 ICPlan по итогу ok
bar Оркестратор: 1/1 внешняя система part
bar Отдельный триггер: 0/1 агент сам через update_issue no
# Объём доработки
> процесс в ICPlan — 7.5–12 дн человека по задачам 3.1 и 3.6; остальные варианты отсеяны по MUST в Э7 и не оценивались
bar Процесс в ICPlan: 12/12 7.5–12 дн: 3.1 (4.5–7 дн) + 3.6 (3–5 дн) part
bar Внешний оркестратор: 0/12 не оценён: отсеян по M1 — процесс вне ICPlan mute
bar Автоназначение + триггер: 0/12 не оценён: отсеян по M3 — агент двигает задачу сам mute
bar Ручное делегирование: 0/12 доработки нет (как есть), но отсеян по M2 mute
# Позиции ролей
side Процесс в ICPlan | внешний оркестратор
pos Владелец продукта: -2 | доработка в задачах 3.1 и 3.6 этапа 3, без нового сервиса
pos Администратор: -2 | процесс настраивается в проекте ICPlan
pos Пользователь: -2 | процесс виден на доске
pos Архитектор: -1 | очередь и переход — в одном месте
pos DevOps: -1 | без новой инфраструктуры
pos Разработчик: 1 | ветвления и ожидания проще в движке
# Что меняется
> AD-17 подтверждён; зависимости задач — в бэклог
stack Документы: 3 ok, 0 part, 4 mute
- ✅ бэклог: шаг стартует, когда родительские задачи закрыты (Hermes)
- ✅ подтверждено: валидатор перехода = критерии приёмки + проверка человеком
```

**Почему процесс в [ICPlan](../architecture/components/icplan/README.md).** Три вывода:

<div class="rnd-grid" markdown>
<div markdown>
**1. Агент на переходе процесса — общий приём рынка**

Jira + Rovo ставят агента на переход workflow, Plane Agents запускают агента по изменению задачи. Мы делаем так же: шаг процесса знает своего агента. Ручное делегирование оставляет процесс человеку, и он стоит ([Э4](#e4)).
</div>
<div markdown>
**2. Переход делает трекер, а не агент**

Если агент сам двигает задачу (`update_issue`), правила процесса живут в промптах и расходятся. У нас переход делает [ICPlan](../architecture/components/icplan/README.md) по итогу запуска, по правилам шага. В движках workflow это классика: условия, валидаторы, действия после перехода ([Э5](#e5)).
</div>
<div markdown>
**3. Внешний оркестратор — вторая очередь и второй интерфейс**

n8n или Temporal умеют ветвления и ожидания, но процесс уходит из трекера, а задачи синхронизируются через вебхуки. Очередь агента уже есть в [ICPlan](../architecture/components/icplan/README.md), поэтому оркестратор продублировал бы её ([Э7](#e7)).
</div>
</div>

<div class="rnd-grid" markdown>
<div class="take" markdown>
**Берём**

- процесс по типу задачи;
- шаг: колонка, агент, переходы, лимит попыток (3), проверка человеком;
- переход по итогу запуска;
- очередь агента: [ICPlan](../architecture/components/icplan/README.md) выдаёт запуск по приоритету задачи, затем по времени постановки ([FR-198](../architecture/components/icplan/prd.md), задача 3.6); когда стартовать и в каком порядке ждать слотов (`fifo | priority`) — решает планировщик Runner ([AD-14](../architecture/decisions/AD-14.yaml));
- эффект Действия «делегировать агенту».
</div>
<div class="adapt" markdown>
**Адаптируем**

- валидатор перехода (Jira) → критерии приёмки в чек-листе [ICPlan](../architecture/components/icplan/README.md) + проверка человеком ([FR-199](../architecture/components/icplan/prd.md), контракт шага [AD-20](../architecture/decisions/AD-20.yaml));
- запуск по изменению задачи (Plane) → триггеры [ICPlan](../architecture/components/icplan/README.md) ([FR-204](../architecture/components/icplan/prd.md));
- зависимости «родитель → потомок» (Hermes) → в бэклог.
</div>
<div class="drop" markdown>
**Не берём**

- агент сам двигает задачу: [FR-197](../architecture/components/icplan/prd.md);
- внешний оркестратор: процесс уходит из трекера;
- ручное делегирование: процесс не идёт сам;
- ветвления на несколько параллельных шагов: нет историй.
</div>
</div>

<div class="rnd-grid" markdown>
<div class="no" markdown>
**Отсеяны до сравнения**

- **Jira + Rovo, Plane Agents, Hermes Kanban** — это другие трекеры, а не способ автоподхвата в [ICPlan](../architecture/components/icplan/README.md): трекер выбран в [R&D трекера](tracker-choice.md). От них взяты функции (Э5–Э6), в сравнение Э9 они не входят.
</div>
<div class="risk" markdown>
**Риски и пересмотр**

- Задача зациклилась между шагами — лимит попыток шага, затем ожидание человека.
- Пересмотр: появятся процессы с параллельными ветками и ожиданием внешних событий.
</div>
</div>

<div class="rnd-chain" markdown>
<div markdown>**Э1 Вопрос**<span class="gate">G1</span></div>
<div markdown>**Э2 Потребности**8 <span class="gate">G2</span></div>
<div markdown>**Э3 Делегирование [ICPlan](../architecture/components/icplan/README.md)**5 функций <span class="gate">G3</span></div>
<div markdown>**Э4 Альтернативы**7 <span class="gate">G4</span></div>
<div markdown>**Э5 Ценность**<span class="gate">G5</span></div>
<div markdown>**Э6 Перенос**3 MUST <span class="gate">G6</span></div>
<div markdown>**Э7 Встраивание**[I1](../architecture/components/agent-runner/integrations/I1.yaml), [I2](../architecture/components/agent-runner/integrations/I2.yaml), [I20](../architecture/components/icplan/integrations/I20.yaml) <span class="gate">G7</span></div>
<div markdown>**Э8 Спор**6 ролей <span class="gate">G8</span></div>
<div markdown>**Э9 Выбор**<span class="gate">G9</span></div>
<div markdown>**Э10 Последствия**7 <span class="gate">G10</span></div>
</div>

---

Дальше — как получен ответ, этап за этапом.

## Э1. Вопрос {#e1}

**Ситуация.** В [ICPlan](../architecture/components/icplan/README.md) агент запускается при смене поля «Делегат» или упоминании. Автоназначение на колонке ставит только исполнителя и запуск не создаёт (проверено по коду форка, `issues/service.ts`).

**Осложнение.** Командам нужен процесс «задача пришла в шаг → агент взял → по итогу дальше». Ревью 2 нашло разночтение: кто и когда переводит задачу.

**Вопрос.** Как задача сама попадает к агенту и переходит дальше?

**Решает:** владелец продукта с администратором. **Не решаем:** когда стартует запуск ([Runner](runner-and-scheduling.md)), выбор трекера ([трекер](tracker-choice.md)).

<span class="gate">G1</span> ✅ вопрос — выбор; есть владелец; связан с [AD-17](../architecture/decisions/AD-17.yaml).

## Э2. Потребности {#e2}

| # | Потребность | Откуда | Что ломается без неё |
|---|---|---|---|
| П1 | задача в шаге сама попадает в очередь агента | [US-ICP-01](../architecture/components/icplan/stories/us-icp-01.yaml), [FR-188](../architecture/components/icplan/prd.md) | процесс стоит |
| П2 | процесс настраивает пользователь в [ICPlan](../architecture/components/icplan/README.md) без кода | [FR-196](../architecture/components/icplan/prd.md), [FR-203](../architecture/components/icplan/prd.md) | процесс — код |
| П3 | переход однозначен и делается одним участником | [FR-197](../architecture/components/icplan/prd.md) | агент и человек двигают задачу по-разному |
| П4 | проверка человеком перед переходом и вердикт | [FR-199](../architecture/components/icplan/prd.md), [FR-200](../architecture/components/icplan/prd.md) | плохой результат уходит дальше |
| П5 | повтор шага с лимитом | [FR-202](../architecture/components/icplan/prd.md) | бесконечный цикл |
| П6 | остановка и возобновление процесса по задаче | [FR-201](../architecture/components/icplan/prd.md) | нельзя прервать процесс |
| П7 | нет дублей запусков | [FR-192](../architecture/components/icplan/prd.md) | два запуска на один шаг |
| П8 | без новой инфраструктуры | [AD-15](../architecture/decisions/AD-15.yaml) | ещё один сервис |

<span class="gate">G2</span> ✅ у потребностей есть требования.

## Э3. Опорное решение: делегирование в ICPlan {#e3}

| # | Функция | Что делает | Потребность |
|---|---|---|---|
| F1 | Поле «Делегат» → запуск (`enqueueDelegateRun`) | смена делегата ставит запуск | П1 частично |
| F2 | Колонки с автоназначением | ставят исполнителя, запуск не создают | — |
| F3 | Действия: условие → эффект | эффекты типизированы, новый тип без миграции | П1, П2 |
| F4 | Типы задач | разные виды задач в проекте | П2 |
| F5 | Очередь запусков агента с арендой | порядок, повторы до 3 | П7 |

**Вывод этапа.** Механизмы есть по отдельности; процесса как сущности нет.

<span class="gate">G3</span> ✅ функции проверены по коду форка (А).

## Э4. Альтернативы и их ключевые функции {#e4}

Поиск 11.10.2026: документация Jira + Rovo, Plane Agents, Hermes Agent; движки workflow.

| Кандидат | Ключевые функции | Чего нет в опорном | Уровень |
|---|---|---|---|
| **Процесс типа задачи в [ICPlan](../architecture/components/icplan/README.md)** ([AD-17](../architecture/decisions/AD-17.yaml)) | шаг = колонка + агент + переходы + лимит + проверка; переход по итогу | процесс как сущность | А |
| **Jira + Rovo** | агент на переходе workflow; условия, валидаторы, действия после перехода | валидатор перехода | Б |
| **Plane Agents** | запуск агента по назначению, упоминанию, изменению задачи, расписанию; граница и эскалация | запуск по изменению | Б |
| **Hermes Kanban** | зависимость «родитель → потомок»: потомок готов, когда родители закрыты | зависимости | Б |
| **Внешний оркестратор (n8n, Temporal)** | ветвления, ожидания, повторы во внешней системе | ветвления | Б |
| **Автоназначение + отдельный триггер** | колонка назначает, правило запускает, агент двигает сам | — | А |
| **Ручное делегирование** | человек назначает агента на каждом шаге | — | А |

**Вывод этапа.** Рынок ставит агента на переход процесса. Workflow-движки добавляют к переходу условия и валидаторы, Hermes — зависимости между задачами.

<span class="gate">G4</span> ✅ 7 кандидатов, включая «как есть»; источники трёх видов; дата есть.

## Э5. Ценность функций {#e5}

| Функция | Потребность | Почему ценна | Доказательство | Класс |
|---|---|---|---|---|
| Агент на шаге процесса | П1 | процесс идёт сам | Jira + Rovo, Plane (Б) | базовая |
| Процесс в трекере без кода | П2 | процесс меняет команда | Jira workflow (Б); [AD-17](../architecture/decisions/AD-17.yaml) (А) | базовая |
| Переход делает трекер по итогу | П3 | одно место решения | ревью 2 (А); переходы в Jira — по правилам workflow (Б) | базовая |
| Валидатор перехода | П4 | проверка до перехода | Jira (Б); у нас — критерии приёмки и проверка человеком (А) | линейная, есть |
| Лимит попыток | П5 | нет бесконечного цикла | [FR-202](../architecture/components/icplan/prd.md) (А) | базовая |
| Запуск по изменению задачи | П1 | агент реагирует на событие | Plane (Б); триггеры [ICPlan](../architecture/components/icplan/README.md) (А) | линейная, есть |
| Зависимости задач | — | порядок работ между задачами | Hermes (Б); нет историй | привлекательная |
| Ветвления и ожидания событий | — | сложные процессы | n8n, Temporal (Б); нет историй | безразличная сейчас |
| Агент сам двигает задачу | П3 | — | правила в промптах расходятся | обратная |

**Вывод этапа.** Базовые функции — агент на шаге, процесс без кода, переход по итогу трекером, лимит попыток. Зависимости задач — привлекательная функция на будущее.

<span class="gate">G5</span> ✅ у функций есть доказательство уровня Б и выше.

## Э6. Перенос и критерии {#e6}

| Функция | Решение | Как | Где |
|---|---|---|---|
| Процесс, шаг, переход, очередь, эффект Действия | брать | [AD-17](../architecture/decisions/AD-17.yaml) | [FR-188](../architecture/components/icplan/prd.md) – [FR-204](../architecture/components/icplan/prd.md), задачи 3.1, 3.6 |
| Валидатор перехода | оставить | критерии приёмки в чек-листе [ICPlan](../architecture/components/icplan/README.md) + проверка человеком | [FR-199](../architecture/components/icplan/prd.md), [AD-20](../architecture/decisions/AD-20.yaml) |
| Запуск по изменению | оставить | триггеры [ICPlan](../architecture/components/icplan/README.md) | [FR-204](../architecture/components/icplan/prd.md) |
| Зависимости задач | не брать сейчас | в бэклог | [BACKLOG](..\source\BACKLOG.md) |
| Ветвления, оркестратор, агент двигает сам | не брать | Э5 | — |

**Критерии:**

| Критерий | Цепочка | Как проверяем |
|---|---|---|
| **M1** процесс настраивается в [ICPlan](../architecture/components/icplan/README.md) без кода | П2 → базовая | где редактор |
| **M2** задача сама попадает к агенту | П1 → базовая | без ручного шага |
| **M3** переход делает один участник | П3 → базовая | кто двигает |
| **К1** новая инфраструктура | П8 | сервисы |
| **К2** проверка человеком и вердикт | П4 | есть ли |
| **К3** повтор с лимитом, остановка | П5, П6 | есть ли |

<span class="gate">G6</span> ✅ у функций есть решения; критерии с цепочкой.

## Э7. Отсев и встраивание {#e7}

### Отсев по MUST

| Кандидат | M1 в [ICPlan](../architecture/components/icplan/README.md) без кода | M2 сам к агенту | M3 один участник | Итог |
|---|---|---|---|---|
| Процесс типа задачи | да | да | да: [ICPlan](../architecture/components/icplan/README.md) | проходит |
| Автоназначение + триггер | частично: два места | да | **нет**: агент двигает сам | ✗ |
| Внешний оркестратор | **нет** | да | да: оркестратор | ✗ |
| Ручное делегирование | да | **нет** | да: человек | ✗ |

### Как встаёт в схему

```
 Администратор ──I20──▶ ICPlan: тип задачи → процесс → шаги (колонка, агент, переходы, лимит, проверка)
 задача входит в шаг ──▶ очередь агента (ICPlan) ──I1 claim──▶ Agent Runner ──▶ запуск
                                                 ◀──I2 итог─── (success / failed / canceled)
 ICPlan по итогу и правилам шага: переход при успехе / при неудаче / повтор / ждать проверки человека
```

| Стык | Процесс в [ICPlan](../architecture/components/icplan/README.md) | Внешний оркестратор |
|---|---|---|
| [I1](../architecture/components/agent-runner/integrations/I1.yaml) выдача запуска | И2: очередь агента не меняется | И1: оркестратор кладёт запуск через API [ICPlan](../architecture/components/icplan/README.md) |
| [I2](../architecture/components/agent-runner/integrations/I2.yaml) итог → переход | И2: [ICPlan](../architecture/components/icplan/README.md) применяет правила шага | И1: вебхук в оркестратор, переход через API |
| [I20](../architecture/components/icplan/integrations/I20.yaml) редактор процесса | И2: настройки проекта [ICPlan](../architecture/components/icplan/README.md) | И0: внешний редактор |

**Изменения у соседей:** процесс в [ICPlan](../architecture/components/icplan/README.md) — Runner и [Harness](../architecture/components/harness/README.md) не меняются (переход не их дело). Порядок разделён: [ICPlan](../architecture/components/icplan/README.md) выдаёт запуск из очереди агента по приоритету задачи и времени постановки ([FR-198](../architecture/components/icplan/prd.md)); взятый запуск ждёт свободных слотов в порядке `fifo | priority` планировщика Runner ([AD-14](../architecture/decisions/AD-14.yaml), [FR-67](../architecture/components/agent-runner/prd.md)). Оркестратор — новый сервис, вебхуки [ICPlan](../architecture/components/icplan/README.md), новый I-код, синхронизация статусов.

**Вывод этапа.** ==Процесс в [ICPlan](../architecture/components/icplan/README.md) не меняет ни Runner, ни [Harness](../architecture/components/harness/README.md): они видят только запуск и итог.==

<span class="gate">G7</span> ✅ отсев; готовность стыков; изменения у соседей.

## Э8. Спор ролей {#e8}

Роли 🤖. Оппонент — Разработчик за оркестратор, «адвокат дьявола» атакует процесс в [ICPlan](../architecture/components/icplan/README.md).

| Роль | За | Довод | Опасение | Согласится, если |
|---|---|---|---|---|
| Владелец продукта 🤖 | процесс в [ICPlan](../architecture/components/icplan/README.md) | доработка — 7.5–12 дн человека в задачах 3.1 и 3.6 этапа 3, без нового сервиса (П8) | линейный процесс не покроет процессы команд с ветками | пересмотр при историях с параллельными ветками |
| Администратор 🤖 | процесс в [ICPlan](../architecture/components/icplan/README.md) | процесс в настройках проекта | — | — |
| Пользователь 🤖 | процесс в [ICPlan](../architecture/components/icplan/README.md) | процесс виден на доске; проверка со мной | агент утащит задачу без меня | `require_review` на шаге |
| Архитектор 🤖 | процесс в [ICPlan](../architecture/components/icplan/README.md) | очередь и переход — в одном месте | — | — |
| DevOps 🤖 | процесс в [ICPlan](../architecture/components/icplan/README.md) | без новой инфраструктуры | — | — |
| Разработчик 🤖 (оппонент) | оркестратор | ветвления и ожидания событий проще в движке | процесс в [ICPlan](../architecture/components/icplan/README.md) упрётся в линейность | пересмотр при параллельных ветках |

| Спор | Разрешение |
|---|---|
| Разработчик: «нужны ветвления» | **условие:** пересмотр при появлении историй с параллельными ветками |
| Адвокат дьявола: «задача зациклится между шагами» | **условие:** лимит попыток шага (3), затем ожидание человека ([FR-202](../architecture/components/icplan/prd.md)) |
| Пользователь: «нужен порядок между задачами» | ✅ **внесено в бэклог:** зависимости «родитель → потомок» |

**Вывод этапа.** Возражение о ветвлениях снято условием пересмотра; новых функций спор не вскрыл, кроме зависимостей — они в бэклоге.

<span class="gate">G8</span> ✅ у каждого спора есть разрешение.

## Э9. Выбор {#e9}

| Потребность | Процесс в [ICPlan](../architecture/components/icplan/README.md) | Оркестратор | Автоназначение + триггер | Ручное |
|---|---|---|---|---|
| П1 сам к агенту | закрывает | закрывает | закрывает | не закрывает |
| П2 без кода в [ICPlan](../architecture/components/icplan/README.md) | закрывает | не закрывает | частично | закрывает |
| П3 один участник | закрывает | закрывает | не закрывает | закрывает |
| П4 проверка и вердикт | закрывает | закрывает | частично | закрывает |
| П5 повтор с лимитом | закрывает | закрывает | не закрывает | не закрывает |
| П6 остановка | закрывает | закрывает | частично | не закрывает |
| П7 без дублей | закрывает | частично | закрывает | закрывает |
| П8 без инфраструктуры | закрывает | не закрывает | закрывает | закрывает |

- **Утверждение.** Процесс типа задачи в [ICPlan](../architecture/components/icplan/README.md) ([AD-17](../architecture/decisions/AD-17.yaml)).
- **Основания.** Закрывает все 8 потребностей; Runner и [Harness](../architecture/components/harness/README.md) не меняются.
- **Связка.** Рынок ставит агента на переход процесса; переход в трекере делает правило однозначным.
- **Опровержение.** Вывод неверен, если понадобятся параллельные ветки и ожидание внешних событий. Тогда — внешний оркестратор поверх [ICPlan](../architecture/components/icplan/README.md).

<span class="gate">G9</span> ✅ вывод следует из покрытия, встраивания и спора; есть опровержение.

## Э10. Последствия {#e10}

| Изменение | Документ | Статус |
|---|---|---|
| Зависимости задач «родитель → потомок» | [BACKLOG](..\source\BACKLOG.md) | ✅ внесено в бэклог |
| Валидатор перехода = критерии приёмки + проверка человеком | [FR-199](../architecture/components/icplan/prd.md), [AD-20](../architecture/decisions/AD-20.yaml) | ✅ подтверждено, без изменений |
| Решение [AD-17](../architecture/decisions/AD-17.yaml) | design | ✅ подтверждено, без изменений |
| Требования [FR-188](../architecture/components/icplan/prd.md) – [FR-204](../architecture/components/icplan/prd.md) | спека icplan-agent-autopickup | — не требуется |
| Задачи 3.1, 3.6 | [задачи](..\source\TASKS.md) | — не требуется |
| Поток процесса | поток [ICPlan](../architecture/components/icplan/README.md) | — не требуется |
| Стыки [I1](../architecture/components/agent-runner/integrations/I1.yaml), [I2](../architecture/components/agent-runner/integrations/I2.yaml), [I20](../architecture/components/icplan/integrations/I20.yaml) | спеки | — не требуется |

<span class="gate">G10</span> ✅ у каждого изменения есть документ и статус.

## Источники

Поиск и чтение — 10–11.10.2026; в скобках уровень доказательства.

- Jira + Rovo: [агенты в Jira](https://www.atlassian.com/blog/rovo/ai-agents-in-jira) (Б), [работа с агентами в задачах](https://support.atlassian.com/jira-software-cloud/docs/collaborate-on-work-items-with-ai-agents/) (Б)
- [Plane Agents](https://plane.so/blog/agents-are-now-live-in-plane) (Б) · [Hermes Kanban](https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban) (Б)
- Наши: код форка `issues/service.ts` (А), [AD-14, AD-17, AD-20](..\source\design\define-agent-platform\design.md) (А), оценки задач [3.1](..\source\tasks\3.1-icplan-process-step-agent.md) и [3.6](..\source\tasks\3.6-icplan-process-engine.md) (А), [ревью 2](..\source\reviews\2026-10-10-spec-review-2.md) (А), [потоки аналогов](us-analogs-agent-tracker.md) (А)
