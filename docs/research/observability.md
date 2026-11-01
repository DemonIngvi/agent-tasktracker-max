# R&D: Наблюдаемость агентов

← [Все R&D](README.md) · методология R&D v3.1 · компонент: **[Observability](../architecture/components/observability/README.md)** · решение: [design AD-12](..\source\design\define-agent-platform\design.md) · спека: observability

<div class="rnd-hero" markdown>
<div class="rnd-q">Вопрос</div>
Как пользователь видит шаги агента в задаче, администратор — затраты и статистику, а разработчик — разбор запуска, не добавляя на MVP новых сервисов?

<div class="rnd-a">Ответ: таблица событий запуска в Postgres [ICPlan](../architecture/components/icplan/README.md) и таймлайн в задаче; затраты — из журнала LiteLLM. Имена событий сопоставлены с OpenTelemetry GenAI, чтобы после MVP выгрузить их в Langfuse или Phoenix без переделки.</div>

<span class="rnd-badge adopt">Adopt</span> таблица `run_event` · <span class="rnd-badge assess">Assess</span> Langfuse, Phoenix, Opik · <span class="rnd-badge hold">Hold</span> метрики Prometheus · данные 11.10.2026
</div>

```deck
# Покрытие потребностей П1–П8
> таблица закрывает то, что видит пользователь; LLM-платформы сильнее в разборе, но вне задачи и с новыми сервисами
stack Таблица событий в ICPlan: 6 ok, 2 part, 0 no
stack Langfuse: 5 ok, 1 part, 2 no
stack Phoenix: 5 ok, 1 part, 2 no
stack Opik: 5 ok, 1 part, 2 no
stack Prometheus / Grafana / Loki: 2 ok, 1 part, 5 no
# Объём доработки
> выбранный вариант «таблица событий» — задачи 3.3, 3.5, 3.9, 94 ч по подзадачам; у остальных кандидатов оценок задач нет
bar 3.3 события запуска, чат в задаче, срок хранения: 43/94 ч, 9 подзадач ok
bar 3.5 затраты задачи, действия по типу: 28/94 ч, 5 подзадач ok
bar 3.9 сводка и статистика агентов: 23/94 ч, 5 подзадач ok
# Новые сервисы на MVP
> Langfuse v3 тянет ClickHouse, Redis и S3
bar Таблица событий: 0/4 сервисов ok
bar Phoenix: 1/4 сервис + Postgres part
bar Langfuse: 4/4 сервис, ClickHouse, Redis, S3 no
# Позиции ролей
side Таблица | Langfuse
pos Пользователь: -2 | шаги видны в задаче
pos DevOps: -2 | без ClickHouse на MVP
pos Безопасность: -1 | маскирование до записи под нашим контролем
pos Администратор: 0 | затраты и статистика — у обоих
pos Разработчик: 2 | разбор промптов и evals
# Что меняется
> AD-12 подтверждён; RunEvent сопоставлен с OTel GenAI
stack Документы: 4 ok, 0 part, 4 mute
- ✅ каталог API: RunEvent → OTel GenAI · ✅ TECHNOLOGIES: Phoenix, Opik — Assess
- — экспорт в OTel: после MVP, в бэклоге
```

**Почему таблица событий.** Три вывода:

<div class="rnd-grid" markdown>
<div markdown>
**1. Главный зритель — пользователь задачи**

Пользователь смотрит на шаги агента **в задаче [ICPlan](../architecture/components/icplan/README.md)**, а не в отдельном интерфейсе. Таблица событий в той же БД даёт таймлайн без интеграции. LLM-платформы показывают трассу в своём интерфейсе ([Э9](#e9)).
</div>
<div markdown>
**2. Разбор промптов — после MVP, но без переделки**

Langfuse и Phoenix сильнее в разборе промптов и evals. Наши типы событий сопоставлены с OpenTelemetry GenAI (`invoke_agent`, `chat`, `execute_tool`), поэтому после MVP события выгружаются экспортом, а не переписыванием ([Э6](#e6)).
</div>
<div markdown>
**3. Затраты — из одного источника**

Токены и $ считает LiteLLM (журнал затрат в S6). Сводка по задаче, агенту и модели читает его, а не пересчитывает. Если LiteLLM недоступен, сводка показывается без затрат с пометкой ([FR-152](../architecture/components/observability/prd.md)) ([Э7](#e7)).
</div>
</div>

<div class="rnd-grid" markdown>
<div class="take" markdown>
**Берём**

- события запуска в `run_event` (S3);
- таймлайн в задаче;
- маскирование до записи;
- затраты из журнала LiteLLM;
- срок хранения 90 дней.
</div>
<div class="adapt" markdown>
**Адаптируем**

- имена спанов и атрибутов OTel GenAI → соответствие типов [`RunEvent`](../architecture/data/model-RunEvent.yaml);
- оценка запуска (scores, Langfuse) → вердикт пользователя «принято / не выполнено» уже есть в M2;
- датасеты для evals (Phoenix, Opik) → эталонные задачи прототипа 1.3.9.
</div>
<div class="drop" markdown>
**Не берём на MVP**

- Langfuse self-host: ClickHouse, Redis, S3;
- метрики и журналы инфраструктуры (Prometheus, Loki) — в бэклоге;
- LangSmith: облако или платный self-host.
</div>
</div>

<div class="rnd-grid" markdown>
<div class="no" markdown>
**Отсеяны до сравнения**

- **LangSmith** — облако, self-host только платно.
</div>
<div class="risk" markdown>
**Риски и пересмотр**

- Объём событий при `events.level: всё` (решение владельца) — ~250 МБ/день; маскирование до записи, срок 90 дней.
- Соглашения OTel GenAI в статусе Development — версию фиксируем при экспорте.
- Пересмотр: разработчикам нужен разбор промптов на каждом запуске → Langfuse или Phoenix.
</div>
</div>

<div class="rnd-chain" markdown>
<div markdown>**Э1 Вопрос**<span class="gate">G1</span></div>
<div markdown>**Э2 Потребности**8 <span class="gate">G2</span></div>
<div markdown>**Э3 Таблица**6 функций <span class="gate">G3</span></div>
<div markdown>**Э4 Альтернативы**9 <span class="gate">G4</span></div>
<div markdown>**Э5 Ценность**<span class="gate">G5</span></div>
<div markdown>**Э6 Перенос**3 MUST <span class="gate">G6</span></div>
<div markdown>**Э7 Встраивание**[I2](../architecture/components/agent-runner/integrations/I2.yaml), [I14](../architecture/components/llm-gateway/integrations/I14.yaml), [I20](../architecture/components/icplan/integrations/I20.yaml) <span class="gate">G7</span></div>
<div markdown>**Э8 Спор**6 ролей <span class="gate">G8</span></div>
<div markdown>**Э9 Выбор**<span class="gate">G9</span></div>
<div markdown>**Э10 Последствия**8 <span class="gate">G10</span></div>
</div>

---

Дальше — как получен ответ, этап за этапом.

## Э1. Вопрос {#e1}

**Ситуация.** Runner получает от [Harness](../architecture/components/harness/README.md) поток событий ([I7](../architecture/components/agent-runner/integrations/I7.yaml)) и передаёт их в [ICPlan](../architecture/components/icplan/README.md) ([I2](../architecture/components/agent-runner/integrations/I2.yaml)). Пользователю нужен таймлайн в задаче, администратору — затраты и статистика, разработчику — разбор запуска.

**Осложнение.** Готовые LLM-платформы (Langfuse, Phoenix, Opik) удобны для разбора, но показывают трассу в своём интерфейсе и требуют своих хранилищ.

**Вопрос.** Где хранить и показывать события запусков на MVP и как не закрыть путь к LLM-платформе?

**Решает:** владелец продукта. **Не решаем:** метрики инфраструктуры (бэклог).

<span class="gate">G1</span> ✅ вопрос — выбор; есть владелец; связан с [AD-12](../architecture/decisions/AD-12.yaml).

## Э2. Потребности {#e2}

| # | Потребность | Откуда | Что ломается без неё |
|---|---|---|---|
| П1 | шаги агента в задаче по мере работы | [FR-147](../architecture/components/observability/prd.md), [US-ICP-02](../architecture/components/icplan/stories/us-icp-02.yaml) | пользователь не видит, что делает агент |
| П2 | события каждого запуска с трассировкой к задаче и версии агента | [FR-146](../architecture/components/observability/prd.md), [FR-148](../architecture/components/observability/prd.md) | нельзя разобрать запуск |
| П3 | маскирование секретов и персональных данных до записи | [FR-149](../architecture/components/observability/prd.md) | секреты в журнале |
| П4 | затраты по запуску, задаче, агенту, модели | [FR-150](../architecture/components/observability/prd.md) | нет контроля расходов |
| П5 | сводка и статистика агентов | [FR-152](../architecture/components/observability/prd.md), [US-ICP-12](../architecture/components/icplan/stories/us-icp-12.yaml), [US-ICP-28](../architecture/components/icplan/stories/us-icp-28.yaml) | нельзя оценить агентов |
| П6 | срок хранения | [FR-151](../architecture/components/observability/prd.md) | таблица растёт без предела |
| П7 | без новых сервисов на MVP | [AD-12](../architecture/decisions/AD-12.yaml), [AD-15](../architecture/decisions/AD-15.yaml) | ClickHouse и Redis в эксплуатации |
| П8 | разбор промптов и evals после MVP | [AD-12](../architecture/decisions/AD-12.yaml), прототип 1.3.9 | нельзя улучшать агентов по данным |

<span class="gate">G2</span> ✅ у потребностей есть требования и решения.

## Э3. Опорное решение: таблица событий в ICPlan {#e3}

| # | Функция | Что делает | Потребность |
|---|---|---|---|
| F1 | `run_event` в схеме `platform` | событие: запуск, `seq`, тип, время, данные | П2 |
| F2 | Типы событий | `run_started`, `llm_call`, `tool_call`, `tool_result`, `needs_approval`, `question`, `memory_write`, `guardrail_decision`, `run_finished` | П1, П2 |
| F3 | Таймлайн в задаче | API [ICPlan](../architecture/components/icplan/README.md) отдаёт события UI ([I20](../architecture/components/icplan/integrations/I20.yaml)) | П1 |
| F4 | Маскирование перед записью | поля секретов и шаблоны | П3 |
| F5 | Затраты из журнала LiteLLM | `metadata.run_id` → запуск, задача, агент | П4, П5 |
| F6 | `retention_days` 90, `events.level` | срок и детализация | П6 |

**Вывод этапа.** Таблица закрывает всё, что видит пользователь и администратор. Разбор промптов (П8) — частично: только по `events.level`.

<span class="gate">G3</span> ✅ функции из спеки и [потока observability](..\architecture\components\observability\docs\how.md) (А).

## Э4. Альтернативы и их ключевые функции {#e4}

Поиск 11.10.2026: GitHub (llm observability, agent tracing), OpenTelemetry, обзоры трассировки агентов 2026.

| Кандидат | Ключевые функции | Чего нет у таблицы | Уровень |
|---|---|---|---|
| **Langfuse** (35 636★, v4.56.0; MIT + коммерческая часть) | трассы, промпты с версиями, оценки (scores), датасеты, evals; self-host v3: Postgres, ClickHouse, Redis, S3 | промпты, оценки, датасеты | Б |
| **Phoenix** (Arize, 11 784★; лицензия по API не определена, по README — Elastic License 2.0) | трассы OpenInference / OTel, evals, датасеты; Postgres или SQLite | evals на трассах | Б |
| **Opik** (Comet, Apache-2.0, 22 499★, 2.2.96) | трассы, evals, оптимизация промптов | оптимизация промптов | Б |
| **OpenLLMetry** (Traceloop, Apache-2.0, 7 481★) | инструментирование OTel для LLM-фреймворков | автоинструментирование | Б |
| **OpenLIT** (Apache-2.0, 2 837★) | OTel-инструментирование и интерфейс | — | Б |
| **OpenTelemetry GenAI** (semconv v1.44.0, статус Development) | спаны `invoke_agent`, `chat`, `execute_tool`; атрибуты провайдера, модели, токенов, в том числе размышлений | стандарт имён | Б / В |
| **Prometheus / Grafana / Loki** | метрики и журналы инфраструктуры | — | Б |
| **LangSmith** | трассы и evals LangChain; облако, self-host платно | — | Б |

**Вывод этапа.** LLM-платформы сильнее в **разборе и оценке** (промпты, evals, датасеты). OpenTelemetry GenAI задаёт общий язык событий, через который к ним можно прийти позже.

<span class="gate">G4</span> ✅ 9 кандидатов (с таблицей); источники трёх видов; дата есть.

## Э5. Ценность функций {#e5}

| Функция | Потребность | Почему ценна | Доказательство | Класс |
|---|---|---|---|---|
| Таймлайн в задаче | П1 | пользователь не уходит из [ICPlan](../architecture/components/icplan/README.md) | истории [ICPlan](../architecture/components/icplan/README.md); журнал сессии у Copilot, Linear ([потоки аналогов](us-analogs-agent-tracker.md), Б) | базовая |
| События с трассировкой | П2 | разбор запуска | у всех платформ (Б) | базовая |
| Маскирование до записи | П3 | секрет не попадает в журнал | [FR-149](../architecture/components/observability/prd.md) (А); маскирование в Langfuse (Б) | базовая |
| Затраты по запуску | П4 | контроль расходов | LiteLLM spend logs (Б) | базовая |
| Без новых сервисов | П7 | одна эксплуатация | [AD-12](../architecture/decisions/AD-12.yaml) (А) | базовая на MVP |
| Стандарт имён OTel GenAI | П8 | переход на платформу без переписывания | semconv (Б); статус Development (В) | линейная |
| Промпты с версиями, evals, датасеты | П8 | улучшение агентов по данным | Langfuse, Phoenix, Opik (Б) | линейная (после MVP) |
| Оценка запуска (score) | П5 | качество агента | Langfuse scores (Б); у нас — вердикт пользователя (А) | линейная, уже есть |
| Метрики инфраструктуры | — | — | для эксплуатации кластера; бэклог | безразличная на MVP |

**Вывод этапа.** Базовые функции у таблицы есть. Стандарт имён — дешёвая страховка для перехода на платформу после MVP.

<span class="gate">G5</span> ✅ у функций есть доказательство уровня Б и выше.

## Э6. Перенос и критерии {#e6}

| Функция | Решение | Как | Где |
|---|---|---|---|
| Таблица, таймлайн, маскирование, затраты, срок | оставить | [AD-12](../architecture/decisions/AD-12.yaml) | [FR-146](../architecture/components/observability/prd.md) – [FR-151](../architecture/components/observability/prd.md) |
| Имена OTel GenAI | адаптировать | соответствие типов [`RunEvent`](../architecture/data/model-RunEvent.yaml) спанам и атрибутам | каталог API |
| Вердикт пользователя как оценка | оставить | M2: «принято / не выполнено» | [FR-200](../architecture/components/icplan/prd.md) |
| Датасеты и evals | адаптировать | эталонные задачи прототипа 1.3.9 — первый датасет | [задача 1.3](..\source\tasks\1.3-harness-core.md) |
| Экспорт в Langfuse или Phoenix | не брать сейчас | после MVP — прототип выбора платформы | [BACKLOG](..\source\BACKLOG.md) |
| Метрики, LangSmith | не брать | Э5 | — |

**Критерии:**

| Критерий | Цепочка | Как проверяем |
|---|---|---|
| **M1** своё размещение | [AD-15](../architecture/decisions/AD-15.yaml) | без облака |
| **M2** таймлайн в задаче [ICPlan](../architecture/components/icplan/README.md) | П1 → базовая | события доступны API [ICPlan](../architecture/components/icplan/README.md) |
| **M3** маскирование до записи | П3 → базовая | где маскируется |
| **К1** новые сервисы | П7 | что ставить |
| **К2** разбор и evals | П8 | промпты, оценки, датасеты |
| **К3** стандарт событий | П8 | OTel GenAI |

<span class="gate">G6</span> ✅ у функций есть решения; критерии с цепочкой.

## Э7. Отсев и встраивание {#e7}

### Отсев по MUST

| Кандидат | M1 у нас | M2 таймлайн в [ICPlan](../architecture/components/icplan/README.md) | M3 маскирование | Итог |
|---|---|---|---|---|
| Таблица событий | да | да | да | проходит |
| Langfuse | да | частично: через API Langfuse | да | проходит |
| Phoenix | да | частично | частично | проходит |
| Opik | да | частично | частично | проходит |
| Prometheus / Grafana / Loki | да | **нет** | частично | ✗ |
| LangSmith | **нет**: облако или платно | частично | да | ✗ |

### Как встаёт в схему

```
 Harness ──I7 RunEvent──▶ Agent Runner ──I2 события (seq)──▶ ICPlan api ──I22──▶ run_event (S3)
                                                                │ I20 таймлайн ──▶ UI задачи
 LiteLLM ──I14──▶ журнал затрат (S6) ──── чтение ──────────────┘ сводка затрат
                     (после MVP: экспорт OTel GenAI* ──▶ Langfuse / Phoenix)
  * — соответствие типов RunEvent спанам OTel — в каталоге API
```

| Стык | Таблица | Langfuse | Phoenix |
|---|---|---|---|
| [I2](../architecture/components/agent-runner/integrations/I2.yaml) события → [ICPlan](../architecture/components/icplan/README.md) | И2: описан, `seq` | И1: второй получатель или экспорт | И1 |
| [I20](../architecture/components/icplan/integrations/I20.yaml) таймлайн в UI | И2 | И1: данные в Langfuse | И1 |
| [I14](../architecture/components/llm-gateway/integrations/I14.yaml) затраты LiteLLM | И2: чтение S6 | И2: callback LiteLLM → Langfuse | И1 |
| Хранилище | И2: S3 в Postgres [ICPlan](../architecture/components/icplan/README.md) | И1: ClickHouse, Redis, S3 | И1: Postgres |

**Изменения у соседей:**

| Кандидат | Что меняется |
|---|---|
| Таблица | ничего |
| Langfuse | инфраструктура (ClickHouse, Redis, S3), техспека, бэкапы; [ICPlan](../architecture/components/icplan/README.md) — таймлайн из Langfuse или дублирование событий |
| Phoenix | инфраструктура (сервис), [ICPlan](../architecture/components/icplan/README.md) — то же |

**Вывод этапа.** ==Таблица встаёт без изменений у соседей; LLM-платформа на MVP — это новые хранилища и второй источник событий для таймлайна.==

<span class="gate">G7</span> ✅ отсев; готовность стыков; изменения у соседей.

## Э8. Спор ролей {#e8}

Роли 🤖. Оппонент — Разработчик за Langfuse, «адвокат дьявола» атакует таблицу.

| Роль | За | Довод | Опасение | Согласится, если |
|---|---|---|---|---|
| Пользователь 🤖 | таблица | шаги видны в задаче | — | — |
| DevOps 🤖 | таблица | без ClickHouse и Redis на MVP | — | — |
| Безопасность 🤖 | таблица | маскирование до записи под нашим контролем | — | — |
| Администратор 🤖 | нейтрально | затраты и статистика есть в обоих | — | сводка [FR-152](../architecture/components/observability/prd.md) |
| Тестировщик 🤖 | таблица | события проверяются тестами Runner | — | — |
| Разработчик 🤖 (оппонент) | Langfuse | разбор промптов, версии, evals | после MVP переделывать формат | соответствие OTel GenAI сейчас |

| Спор | Разрешение |
|---|---|
| Разработчик: «потом переписывать события» | ✅ **внесено:** соответствие [`RunEvent`](../architecture/data/model-RunEvent.yaml) → OTel GenAI в каталоге API |
| Адвокат дьявола: «без evals не понять, что агент стал хуже» | **условие:** вердикты пользователя (M2) и эталонные задачи 1.3.9; платформа — после MVP |
| DevOps: «а таблица событий не разрастётся?» | **условие:** срок 90 дней и очистка по сроку; при `events.level: всё` (решение владельца) ~250 МБ/день ≈ 22 ГБ — помещается; при нехватке диска — снижать до «тулы + итоги» |

**Вывод этапа.** Возражение Разработчика снято соответствием OTel GenAI: переход на платформу после MVP — экспортом.

<span class="gate">G8</span> ✅ у каждого спора есть разрешение.

## Э9. Выбор {#e9}

| Потребность | Таблица | Langfuse | Phoenix | Opik |
|---|---|---|---|---|
| П1 таймлайн в задаче | закрывает | с доработкой | с доработкой | с доработкой |
| П2 события и трассировка | закрывает | закрывает | закрывает | закрывает |
| П3 маскирование | закрывает | закрывает | частично | частично |
| П4 затраты | закрывает | закрывает | закрывает | закрывает |
| П5 сводка и статистика | закрывает | закрывает | закрывает | закрывает |
| П6 срок хранения | закрывает | закрывает | закрывает | закрывает |
| П7 без новых сервисов | закрывает | не закрывает | не закрывает | не закрывает |
| П8 разбор и evals | частично: по уровню событий | закрывает | закрывает | закрывает |

- **Утверждение.** Таблица событий в [ICPlan](../architecture/components/icplan/README.md) ([AD-12](../architecture/decisions/AD-12.yaml)); LLM-платформа — после MVP через экспорт OTel GenAI.
- **Основания.** Закрывает всё, что видят пользователь и администратор, без новых сервисов; разбор промптов закрыт частично.
- **Связка.** Главный зритель событий — пользователь в задаче; платформа разбора нужна разработчикам, и её можно подключить позже, если имена событий совпадают со стандартом.
- **Опровержение.** Вывод неверен, если разбор промптов понадобится на каждом запуске до конца MVP. Тогда — Phoenix на Postgres как более лёгкий вариант.

<span class="gate">G9</span> ✅ вывод следует из покрытия, встраивания и спора; есть опровержение.

## Э10. Последствия {#e10}

| Изменение | Документ | Статус |
|---|---|---|
| Соответствие типов [`RunEvent`](../architecture/data/model-RunEvent.yaml) спанам OTel GenAI | каталог API | ✅ внесено |
| Phoenix, Opik — Assess | [TECHNOLOGIES](..\source\TECHNOLOGIES.md) | ✅ внесено |
| Эталонные задачи 1.3.9 — первый датасет evals | [задача 1.3](..\source\tasks\1.3-harness-core.md) | ✅ учтено (подзадача 1.3.9 из R&D фреймворка) |
| Экспорт событий в OTel и выбор платформы после MVP | [BACKLOG](..\source\BACKLOG.md) (строка Langfuse) | ✅ внесено в бэклог |
| Требование экспорта в OTel | [FR-146](../architecture/components/observability/prd.md) | — не требуется до MVP: соответствие — в каталоге API, экспорт — в бэклоге |
| Решение [AD-12](../architecture/decisions/AD-12.yaml) | design | ✅ подтверждено, без изменений |
| `events.level` по умолчанию «всё» — решение владельца продукта вместо рекомендованного «тулы + итоги» | [interfaces observability](..\architecture\components\observability\docs\observability-interfaces.md), [AD-18](../architecture/decisions/AD-18.yaml), [типы данных](..\source\data-types.md), [профиль нагрузки](load-profile.md) | ✅ внесено: умолчание, объём ~250 МБ/день, сценарий маскирования промптов в [FR-149](../architecture/components/observability/prd.md) |
| Стыки [I2](../architecture/components/agent-runner/integrations/I2.yaml), [I14](../architecture/components/llm-gateway/integrations/I14.yaml), [I20](../architecture/components/icplan/integrations/I20.yaml) | спека observability | — не требуется |
| Поток observability | [поток](..\architecture\components\observability\docs\how.md) | — не требуется |

<span class="gate">G10</span> ✅ у каждого изменения есть документ и статус.

<details markdown>
<summary>Приложение A. Карточки кандидатов</summary>

GitHub API на 11.10.2026.

| Технология | Лицензия | ★ | Релиз | Активность |
|---|---|---|---|---|
| Langfuse | MIT + коммерческая часть | 35 636 | v4.56.0 | 11.10.2026 |
| Opik | Apache-2.0 | 22 499 | 2.2.96 | 10.10.2026 |
| Phoenix | Elastic License 2.0 (по README) | 11 784 | — | 11.10.2026 |
| OpenLLMetry | Apache-2.0 | 7 481 | 0.62.4 | 11.10.2026 |
| OpenLIT | Apache-2.0 | 2 837 | openlit-2.1.0 | 09.10.2026 |
| OTel semantic conventions | Apache-2.0 | 667 | v1.44.0 | 11.10.2026 |
</details>

## Источники

Поиск и чтение — 11.10.2026; в скобках уровень доказательства.

- [Langfuse](https://github.com/langfuse/langfuse) (Б) · [Phoenix](https://github.com/Arize-ai/phoenix) (Б) · [Opik](https://github.com/comet-ml/opik) (Б) · [OpenLLMetry](https://github.com/traceloop/openllmetry) (Б) · [OpenLIT](https://github.com/openlit/openlit) (Б)
- OTel GenAI: [semantic-conventions](https://github.com/open-telemetry/semantic-conventions) (Б), [Dash0 — разбор соглашений](https://www.dash0.com/knowledge/opentelemetry-genai-semantic-conventions-explained) (В), [Greptime, 05.2026](https://greptime.com/blogs/2026-05-09-opentelemetry-genai-semantic-conventions) (В), [трассировка агентов 2026](https://www.morphllm.com/agent-tracing) (В)
- Наши: [AD-12](..\source\design\define-agent-platform\design.md), [поток observability](..\architecture\components\observability\docs\how.md), [типы событий Harness](..\architecture\components\harness\docs\how.md) (А)
