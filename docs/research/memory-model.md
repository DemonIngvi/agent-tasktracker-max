# R&D: Модель памяти агентов

← [Все R&D](README.md) · методология R&D v3.1 · компонент: **[Memory](../architecture/components/memory/README.md)** · решение: [design AD-4](..\source\design\define-agent-platform\design.md) · спека: agent-memory · потоки: [память](..\architecture\components\memory\docs\how.md)

<div class="rnd-hero" markdown>
<div class="rnd-q">Вопрос</div>
Как устроить память, чтобы агент следующего шага процесса продолжал работу, а не начинал заново, контекст не раздувался, а проекты не видели чужого?

<div class="rnd-a">Ответ: уровни M0–M6 по видам знания, область видимости — атрибут записи. Своя тонкая [Memory](../architecture/components/memory/README.md) API в Postgres [ICPlan](../architecture/components/icplan/README.md). Готовые слои памяти (Mem0, LangMem) — кандидаты для M4 после MVP.</div>

<span class="rnd-badge adopt">Adopt</span> M0–M3, M5, M6 · <span class="rnd-badge assess">Assess</span> M4 (Mem0, LangMem, Graphiti) · Postgres [ICPlan](../architecture/components/icplan/README.md) · 0 $ · данные 11.10.2026
</div>

```deck
# Покрытие потребностей П1–П8
> M0–M6 закрывает всё без нового сервиса; готовые слои сильны в фактах (M4), но тянут свой цикл или свою БД
stack M0–M6 + своя Memory API: 7 ok, 1 part, 0 no
stack Mem0: 4 ok, 2 part, 2 no
stack LangMem: 4 ok, 3 part, 1 no
stack Letta: 4 ok, 1 part, 3 no
stack Graphiti (Zep): 3 ok, 2 part, 3 no
stack Только история чата: 2 ok, 1 part, 5 no
# Что уже есть в ICPlan
> 5 из 7 уровней пишет и хранит ICPlan; своё — только M3 и (позже) M4
bar Уже в ICPlan: 5/7 M0, M1, M2, M5, M6 ok
bar Своё: 2/7 M3 сейчас, M4 после MVP info
# Объём доработки
> своя часть — M3 и Memory API, задача 2.5: 39 ч по подзадачам; M4 — после MVP
bar 2.5.1–2.5.2 хранилище M3 и тул записи: 10/39 ч ok
bar 2.5.3 подача M3 и M2 в контекст: 6/39 ч ok
bar 2.5.4, 2.5.7 права, область и проверки записи: 8/39 ч ok
bar 2.5.8–2.5.9 передача шага и срок хранения: 5/39 ч ok
bar 2.5.5 тесты преемственности: 4/39 ч ok
bar 2.5.6 конфигурация, хранилища, интерфейсы, отказы: 6/39 ч ok
# Позиции ролей
side M0–M6 | готовый слой (Mem0)
pos Архитектор: -2 | без нового сервиса и второго цикла агента
pos Безопасность: -1 | область и маскирование под нашим контролем
pos DevOps: -1 | одна БД
pos Пользователь: 0 | важно, чтобы агент помнил
pos Разработчик: 1 | извлечение фактов готово
# Что меняется
> модель подтверждена; функции Mem0, Graphiti, Letta — в требования M4 после MVP
stack Документы: 4 ok, 0 part, 4 mute
- ✅ бэклог M4: кандидаты и функции · ✅ TECHNOLOGIES: Mem0, LangMem, Graphiti — Assess
- ✅ FR-41: противоречия, срок действия, маскирование
```

**Почему M0–M6.** Три вывода:

<div class="rnd-grid" markdown>
<div markdown>
**1. Преемственность даёт состояние задачи, а не вся история**

Следующему агенту нужно знать, что сделано, что дальше и что мешает. Это M3 — короткая запись (`m3_max_kb` 16) — плюс итоги последних запусков M2. История чата целиком раздувает контекст и не говорит, что дальше ([Э5](#e5)).
</div>
<div markdown>
**2. Пять уровней уже живут в [ICPlan](../architecture/components/icplan/README.md)**

Переписку (M1), итоги запусков (M2), инструкции (M5) и документы (M6) пишет [ICPlan](../architecture/components/icplan/README.md), рабочий контекст (M0) — [Harness](../architecture/components/harness/README.md). Своё хранилище нужно только для M3. Готовые слои памяти пришлось бы синхронизировать с [ICPlan](../architecture/components/icplan/README.md) ([Э7](#e7)).
</div>
<div markdown>
**3. Лучшие функции готовых слоёв — для фактов M4**

Mem0 разрешает противоречия: новый факт обновляет или удаляет старый. Graphiti хранит срок действия факта. Это ценно для M4, а не для состояния задачи. Поэтому функции переносим в требования M4 после MVP ([Э6](#e6)).
</div>
</div>

<div class="rnd-grid" markdown>
<div class="take" markdown>
**Берём**

- виды знания CoALA: рабочая, эпизодическая, семантическая, процедурная память;
- состояние задачи M3: сделано, дальше, блокировки;
- область как атрибут записи (задача, агент, проект, команда);
- автоматическую запись M1 и M2.
</div>
<div class="adapt" markdown>
**Адаптируем (M4 после MVP)**

- извлечение фактов с разрешением противоречий (Mem0) → сценарии [FR-41](../architecture/components/memory/prd.md);
- срок действия факта (Graphiti) → поля «действует с / по»;
- ключи области `user` / `agent` / `run` (Mem0) → уже есть атрибут `scope`.
</div>
<div class="drop" markdown>
**Не берём**

- Letta-сервер: свой цикл агента — второй [Harness](../architecture/components/harness/README.md);
- агент сам переписывает свою инструкцию (LangMem): M5 меняет только администратор (версии Registry); *уточнено 14.10.2026 ([AD-27](..\source\design\define-agent-platform\design.md), [FR-45](../architecture/components/memory/prd.md)): агент может ПРЕДЛАГАТЬ изменение навыков и плейбука, применяет администратор новой версией после регрессионного набора и утверждения человеком*;
- графовую БД (Neo4j) для Graphiti: новая БД.
</div>
</div>

<div class="rnd-grid" markdown>
<div class="no" markdown>
**Отсеяны до сравнения**

- **Только история чата** — нет состояния задачи, следующий агент начинает заново.
</div>
<div class="risk" markdown>
**Риски и пересмотр**

- Агент не пишет M3 — проверки записи [FR-44](../architecture/components/memory/prd.md), напоминание перед завершением.
- Пересмотр: для M4 — выбор между Mem0 и LangMem на прототипе после MVP.
</div>
</div>

<div class="rnd-chain" markdown>
<div markdown>**Э1 Вопрос**<span class="gate">G1</span></div>
<div markdown>**Э2 Потребности**8 <span class="gate">G2</span></div>
<div markdown>**Э3 M0–M6**7 функций <span class="gate">G3</span></div>
<div markdown>**Э4 Альтернативы**8 <span class="gate">G4</span></div>
<div markdown>**Э5 Ценность**<span class="gate">G5</span></div>
<div markdown>**Э6 Перенос**3 MUST <span class="gate">G6</span></div>
<div markdown>**Э7 Встраивание**[I2](../architecture/components/agent-runner/integrations/I2.yaml), [I11](../architecture/components/harness/integrations/I11.yaml), [I22](../architecture/integrations/I22.yaml) <span class="gate">G7</span></div>
<div markdown>**Э8 Спор**6 ролей <span class="gate">G8</span></div>
<div markdown>**Э9 Выбор**<span class="gate">G9</span></div>
<div markdown>**Э10 Последствия**8 <span class="gate">G10</span></div>
</div>

---

Дальше — как получен ответ, этап за этапом.

## Э1. Вопрос {#e1}

**Ситуация.** Задача проходит шаги процесса, на каждом — свой агент ([AD-17](../architecture/decisions/AD-17.yaml)). Запуски короткие, между ними задача ждёт людей.

**Осложнение.** Без памяти следующий агент начинает с нуля. С полной историей контекст раздувается и дорожает. Готовые слои памяти (Letta, Mem0, Zep) решают это по-своему, но приносят свои сервисы.

**Вопрос.** Какая модель памяти и где она хранится?

**Решает:** владелец продукта с архитектором. **Не решаем:** поиск по документам и коду ([RAG](rag.md)), хранилища в целом ([хранилища](data-stores.md)).

<span class="gate">G1</span> ✅ вопрос — выбор; есть владелец; связан с [AD-4](../architecture/decisions/AD-4.yaml) и требованиями agent-memory.

## Э2. Потребности {#e2}

| # | Потребность | Откуда | Что ломается без неё |
|---|---|---|---|
| П1 | следующий агент продолжает работу по задаче | [FR-39](../architecture/components/memory/prd.md), [FR-40](../architecture/components/memory/prd.md), [AD-17](../architecture/decisions/AD-17.yaml) | шаг процесса повторяет сделанное |
| П2 | в контекст попадает только нужное | [FR-36](../architecture/components/memory/prd.md), `read` | токены и деньги на лишнее |
| П3 | проекты и задачи не видят чужое | [FR-37](../architecture/components/memory/prd.md) | утечка между проектами |
| П4 | переписка и итоги пишутся автоматически | [FR-38](../architecture/components/memory/prd.md) | память зависит от того, вспомнит ли агент |
| П5 | срок хранения и удаление | [FR-43](../architecture/components/memory/prd.md), [FR-42](../architecture/components/memory/prd.md) | память растёт без предела, нельзя удалить |
| П6 | проверки записи: что, когда и куда агент пишет | [FR-44](../architecture/components/memory/prd.md) | мусор и секреты в памяти |
| П7 | без нового сервиса и новой БД на MVP | [AD-4](../architecture/decisions/AD-4.yaml), [AD-15](../architecture/decisions/AD-15.yaml) | ещё одна система в эксплуатации |
| П8 | факты и знания проекта (M4) после MVP | [FR-41](../architecture/components/memory/prd.md) | агент не накапливает знания проекта |

<span class="gate">G2</span> ✅ у потребностей есть требования и решения.

## Э3. Опорное решение: M0–M6 {#e3}

Опорное решение — модель проекта AI-агент на основе CoALA, принятая в [AD-4](../architecture/decisions/AD-4.yaml).

| # | Уровень | Что хранит | Кто пишет | Потребность |
|---|---|---|---|---|
| F1 | M0 рабочий | контекст запуска | [Harness](../architecture/components/harness/README.md), каждый шаг | П2 |
| F2 | M1 переписка | чат и комментарии задачи | [ICPlan](../architecture/components/icplan/README.md) | П4 |
| F3 | M2 итоги | итог, статус, токены, вердикт запуска (`agent_run`) | Runner → [ICPlan](../architecture/components/icplan/README.md) | П1, П4 |
| F4 | M3 состояние задачи | [`M3Record`](../architecture/data/model-M3Record.yaml): сделано, дальше, блокировки | агент через тул памяти | П1 |
| F5 | M4 факты | факты с источником | после MVP | П8 |
| F6 | M5 процедуры | инструкция и навыки агента | администратор через Registry | — |
| F7 | M6 документы | документы проекта | люди в [ICPlan](../architecture/components/icplan/README.md) | — |

Область видимости (`scope`) — атрибут записи, сроки — параметр `retention`.

**Вывод этапа.** M0–M6 закрывает П1–П7; M4 отложена.

<span class="gate">G3</span> ✅ уровни связаны с потребностями; [потоки памяти](..\architecture\components\memory\docs\how.md) описывают запись и чтение каждого (А).

## Э4. Альтернативы и их ключевые функции {#e4}

Поиск 11.10.2026: GitHub (agent memory, long-term memory), документация, обзоры памяти агентов.

| Кандидат | Ключевые функции | Чего нет у M0–M6 | Уровень |
|---|---|---|---|
| **Mem0** (Apache-2.0, 66 967★) | модель извлекает факты из диалога; новый факт добавляет, обновляет или удаляет старый; векторное хранилище (в том числе pgvector) и граф; ключи `user_id` / `agent_id` / `run_id` | разрешение противоречий | Б |
| **Letta** (MemGPT, Apache-2.0, 25 098★, 0.16.8) | блоки памяти всегда в контексте, агент правит их тулами; архивная и диалоговая память; фоновые агенты перестраивают память; сервер со своим циклом агента | фоновая перестройка памяти | Б |
| **Graphiti** (Zep, Apache-2.0, 31 633★, v0.30.2) | временной граф знаний: у факта срок действия; инкрементальные обновления; гибридный поиск; Neo4j или FalkorDB | срок действия факта | Б |
| **LangMem** (MIT, 1 700★) | тулы памяти для LangGraph; фоновое извлечение воспоминаний; процедурная память — улучшение промпта; хранилище LangGraph (Postgres + pgvector) | улучшение промпта агентом | Б |
| **Cognee** (Apache-2.0, 31 989★, v1.6.3) | граф знаний из документов (конвейеры) | — (ближе к RAG) | Б |
| **L1–L4 по области** | уровни по охвату: запуск, задача, проект, команда | — | А |
| **Только история чата** | контекст = переписка | — | — |
| **Файлы памяти в репозитории** (как CLAUDE.md) | процедурная память файлами рядом с кодом | — | Б |

**Вывод этапа.** Готовые слои сильны в **фактах** (M4): извлечение, противоречия, срок действия. Состояние задачи (M3) и автоматическая запись итогов у нас проще и уже связаны с [ICPlan](../architecture/components/icplan/README.md).

<span class="gate">G4</span> ✅ 8 кандидатов, включая «как есть»; источники трёх видов; дата есть.

## Э5. Ценность функций {#e5}

| Функция | Потребность | Почему ценна | Доказательство | Класс |
|---|---|---|---|---|
| Короткое состояние задачи | П1 | следующий агент видит «что дальше» за сотни токенов | блоки памяти Letta (Б); M3 (А) | базовая |
| Итоги прошлых запусков в контексте | П1 | видны попытки и причины возврата | [FR-40](../architecture/components/memory/prd.md) (А); история сессий у аналогов (Б) | базовая |
| Область видимости | П3 | проект не видит чужое | ключи Mem0 (Б); [FR-37](../architecture/components/memory/prd.md) (А) | базовая |
| Автоматическая запись | П4 | не зависит от модели | M1, M2 пишет [ICPlan](../architecture/components/icplan/README.md) (А) | базовая |
| Разрешение противоречий фактов | П8 | старый факт не спорит с новым в контексте | Mem0 (Б) | линейная (M4) |
| Срок действия факта | П8 | агент знает, что факт устарел | Graphiti (Б) | привлекательная (M4) |
| Фоновая перестройка памяти | П2 | меньше шума | Letta (Б) | привлекательная |
| Агент улучшает свою инструкцию | — | — | M5 меняет администратор с версией (R-REG); агент только предлагает ([FR-45](../architecture/components/memory/prd.md), [AD-27](../architecture/decisions/AD-27.yaml)) | обратная |
| Свой цикл агента в сервисе памяти | — | — | дублирует [Harness](../architecture/components/harness/README.md) | обратная |
| Вся история в контексте | П2 | — | раздувание контекста | обратная |

**Вывод этапа.** Базовые функции у M0–M6 уже есть. Функции готовых слоёв ценны для M4 — переносим их в требования M4.

<span class="gate">G5</span> ✅ у функций есть доказательство уровня Б и выше.

## Э6. Перенос и критерии {#e6}

| Функция | Решение | Как | Где |
|---|---|---|---|
| M0–M6, `scope`, `retention`, автоматическая запись | оставить | как в [AD-4](../architecture/decisions/AD-4.yaml) | [FR-36](../architecture/components/memory/prd.md) – [FR-43](../architecture/components/memory/prd.md) |
| Разрешение противоречий (Mem0) | адаптировать | сценарий M4: новый факт обновляет или помечает устаревшим противоречащий | [FR-41](../architecture/components/memory/prd.md) |
| Срок действия факта (Graphiti) | адаптировать | поля «действует с / по» у факта M4 | [FR-41](../architecture/components/memory/prd.md) |
| Выбор движка M4 | не брать сейчас | прототип Mem0 (pgvector) и LangMem после MVP | [BACKLOG](..\source\BACKLOG.md) |
| Фоновая перестройка (Letta) | не брать сейчас | M2 даёт итоги, шум мал | — |
| Улучшение инструкции агентом | не брать как самозапись | M5 — через администратора; агент предлагает ([FR-45](../architecture/components/memory/prd.md), [AD-27](../architecture/decisions/AD-27.yaml)) | — |
| Letta-сервер, графовая БД | не брать | П7 | — |

**Критерии:**

| Критерий | Цепочка | Как проверяем |
|---|---|---|
| **M1** состояние задачи для следующего агента | П1 → базовая | есть запись «что дальше» |
| **M2** область видимости | П3 → базовая | изоляция проектов |
| **M3** своё размещение | [AD-15](../architecture/decisions/AD-15.yaml) | без облака |
| **К1** без нового сервиса и БД | П7 | что ставить |
| **К2** связь с данными [ICPlan](../architecture/components/icplan/README.md) | П4 | M1, M2 без синхронизации |
| **К3** экономия контекста | П2 | что попадает в запрос |
| **К4** готовность к M4 | П8 | факты, противоречия, срок |

<span class="gate">G6</span> ✅ у функций есть решения; критерии с цепочкой.

## Э7. Отсев и встраивание {#e7}

### Отсев по MUST

| Кандидат | M1 состояние задачи | M2 область | M3 у нас | Итог |
|---|---|---|---|---|
| M0–M6 + своя [Memory](../architecture/components/memory/README.md) API | да | да | да | проходит |
| Mem0 | частично: факты, не состояние | да | да | проходит |
| LangMem | частично | да: пространства имён | да | проходит |
| Letta | да: блоки | частично | да | проходит |
| Graphiti | частично | частично: группы | да | проходит |
| Только история чата | **нет** | **нет** | да | ✗ |

### Как встаёт в схему

```
 ICPlan (S1: чат M1, agent_run M2, документы M6, определения M5)
      ▲ I2 итог запуска → M2                         │ чтение M1, M2
 Agent Runner                                         ▼
      └─I7─▶ Harness ──I11 (M3: запись, чтение)──▶ Memory API ──I22──▶ Postgres S4 (memory_m3; позже M4*)
                └ M0 в контексте запуска
  * — M4: Mem0 или LangMem поверх pgvector в той же БД, без новой службы БД
```

| Стык | M0–M6 | Mem0 | LangMem | Letta | Graphiti |
|---|---|---|---|---|---|
| [I11](../architecture/components/harness/integrations/I11.yaml) [Harness](../architecture/components/harness/README.md) → память | И2: REST, токен запуска | И2: Mem0 за [Memory](../architecture/components/memory/README.md) API | И1: хранилище LangGraph в sandbox — нет доступа к БД ([AD-18](../architecture/decisions/AD-18.yaml)), только через [Memory](../architecture/components/memory/README.md) API | И1: свой API и свой агент | И1 |
| [I22](../architecture/integrations/I22.yaml) хранение | И2: S4 в Postgres [ICPlan](../architecture/components/icplan/README.md) | И2: pgvector | И2: Postgres store | И1: своя БД сервера | И0: Neo4j / FalkorDB |
| Связь с M1, M2 в [ICPlan](../architecture/components/icplan/README.md) | И4: уже в [ICPlan](../architecture/components/icplan/README.md) | И1: синхронизация | И1 | И1 | И1 |
| Модель для извлечения | — | И2: через LiteLLM ([I8](../architecture/components/harness/integrations/I8.yaml)) | И2 | И2 | И2 |

**Изменения у соседей:**

| Кандидат | Что меняется |
|---|---|
| M0–M6 | ничего |
| Mem0, LangMem (для M4) | [Memory](../architecture/components/memory/README.md) API вызывает модель через LiteLLM — новый поток Т1 (данные промпта) через [Memory](../architecture/components/memory/README.md) |
| Letta | [Harness](../architecture/components/harness/README.md): цикл в Letta; Runner: второй исполнитель |
| Graphiti | инфраструктура: графовая БД; бэкапы; FMEA |

**Вывод этапа.** ==Своя [Memory](../architecture/components/memory/README.md) API встаёт без изменений у соседей; для M4 Mem0 и LangMem ложатся на pgvector в той же БД, но добавляют вызов модели из [Memory](../architecture/components/memory/README.md).== Letta и Graphiti меняют чужие компоненты.

<span class="gate">G7</span> ✅ отсев; готовность стыков; изменения у соседей.

## Э8. Спор ролей {#e8}

Роли 🤖. Оппонент защищает Mem0, «адвокат дьявола» атакует M3.

| Роль | За | Довод | Опасение | Согласится, если |
|---|---|---|---|---|
| Архитектор 🤖 | M0–M6 | без нового сервиса, 5 уровней в [ICPlan](../architecture/components/icplan/README.md) (Э7) | — | — |
| Безопасность 🤖 | M0–M6 | маскирование и область под нашим контролем | факты M4 с секретами | маскирование при записи M4 |
| DevOps 🤖 | M0–M6 | одна БД, один бэкап | — | — |
| Пользователь 🤖 | нейтрально | агент должен помнить, что сделано | агент «забывает» записать | проверки записи [FR-44](../architecture/components/memory/prd.md) |
| Аналитик историй 🤖 | M0–M6 | истории про продолжение шага закрыты M3 + M2 | — | — |
| Разработчик 🤖 (оппонент) | Mem0 | извлечение фактов и противоречия готовы | M4 писать самим долго | M4 — на Mem0 или LangMem, не своё |

| Спор | Разрешение |
|---|---|
| Адвокат дьявола: «агент может не записать M3» | **условие:** проверки записи [FR-44](../architecture/components/memory/prd.md) и напоминание перед завершением (уже в спеке) |
| Разработчик: «M4 своё — долго» | ✅ **внесено в бэклог:** M4 на Mem0 или LangMem, выбор прототипом |
| Безопасность: «факты M4 с секретами» | ✅ **внесено:** сценарий маскирования в [FR-41](../architecture/components/memory/prd.md) |

**Вывод этапа.** Спор о M3 снят существующими проверками. Спор о M4 — переносом функций в требования M4 и выбором движка прототипом.

<span class="gate">G8</span> ✅ у каждого спора есть разрешение.

## Э9. Выбор {#e9}

| Потребность | M0–M6 | Mem0 | LangMem | Letta | Graphiti |
|---|---|---|---|---|---|
| П1 продолжение | закрывает | частично: факты, не «что дальше» | частично | закрывает | частично |
| П2 только нужное | закрывает | закрывает | закрывает | закрывает | закрывает |
| П3 область | закрывает | закрывает | закрывает | частично | частично |
| П4 автоматическая запись | закрывает | с доработкой: синхронизация с [ICPlan](../architecture/components/icplan/README.md) | с доработкой | не закрывает: своя история | не закрывает |
| П5 сроки и удаление | закрывает | закрывает | частично | закрывает | закрывает |
| П6 проверки записи | закрывает | частично | частично | частично | частично |
| П7 без нового сервиса | закрывает | закрывает: библиотека | закрывает: библиотека | не закрывает | не закрывает |
| П8 факты M4 | с доработкой: после MVP | закрывает | закрывает | частично | закрывает |

- **Утверждение.** M0–M6 со своей [Memory](../architecture/components/memory/README.md) API ([AD-4](../architecture/decisions/AD-4.yaml)); M4 — после MVP на Mem0 или LangMem.
- **Основания.** Закрывает 7 из 8 потребностей, 5 уровней уже в [ICPlan](../architecture/components/icplan/README.md), соседи не меняются.
- **Связка.** Преемственности шагов нужно состояние задачи, а не база фактов. Готовые слои дают факты и будут нужны для M4.
- **Опровержение.** Вывод неверен, если агенты начнут ссылаться на знания проекта чаще, чем на состояние задачи. Тогда M4 переходит в MVP.

<span class="gate">G9</span> ✅ вывод следует из покрытия, встраивания и спора; есть опровержение.

## Э10. Последствия {#e10}

| Изменение | Документ | Статус |
|---|---|---|
| M4: кандидаты Mem0 и LangMem, функции противоречий и срока действия | [BACKLOG](..\source\BACKLOG.md) | ✅ внесено в бэклог |
| Mem0, LangMem, Graphiti — Assess | [TECHNOLOGIES](..\source\TECHNOLOGIES.md) | ✅ внесено |
| Сценарии M4: противоречащий факт, срок действия, маскирование при записи | [FR-41](../architecture/components/memory/prd.md) | ✅ внесено: три сценария в [FR-41](../architecture/components/memory/prd.md) |
| M4 вызывает модель из [Memory](../architecture/components/memory/README.md) — новый поток данных промпта | [типы данных](..\source\data-types.md) | — не требуется сейчас: интерфейс [Memory](../architecture/components/memory/README.md) → LiteLLM войдёт в матрицу при переносе M4 в работу |
| Модель M0–M6, [AD-4](../architecture/decisions/AD-4.yaml) | design | ✅ подтверждено, без изменений |
| Стыки [I11](../architecture/components/harness/integrations/I11.yaml), [I22](../architecture/integrations/I22.yaml), S4 | спека agent-memory | — не требуется |
| Потоки памяти | [потоки](..\architecture\components\memory\docs\how.md) | — не требуется |
| Техспека [Memory](../architecture/components/memory/README.md) | [техспека](..\architecture\components\memory\docs\techspec.md) | — не требуется |

<span class="gate">G10</span> ✅ у каждого изменения есть документ и статус.

<details markdown>
<summary>Приложение A. Карточки кандидатов</summary>

GitHub API на 11.10.2026.

| Технология | Лицензия | ★ | Релиз | Активность |
|---|---|---|---|---|
| Mem0 | Apache-2.0 | 66 967 | ts-v3.3.1 | 09.10.2026 |
| Cognee | Apache-2.0 | 31 989 | v1.6.3 | 09.10.2026 |
| Graphiti | Apache-2.0 | 31 633 | v0.30.2 | 10.10.2026 |
| Letta | Apache-2.0 | 25 098 | 0.16.8 | 10.09.2026 |
| LangMem | MIT | 1 700 | — | 02.10.2026 |

CoALA (Sumers и др., 2023) — деление на рабочую, эпизодическую, семантическую и процедурную память.
</details>

## Источники

Поиск и чтение — 11.10.2026; в скобках уровень доказательства.

- [CoALA — Cognitive Architectures for Language Agents](https://arxiv.org/abs/2309.02427) (Б)
- [Mem0](https://github.com/mem0ai/mem0) (Б) · [Letta](https://github.com/letta-ai/letta) (Б) · [Graphiti](https://github.com/getzep/graphiti) (Б) · [LangMem](https://github.com/langchain-ai/langmem) (Б) · [Cognee](https://github.com/topoteretes/cognee) (Б)
- Наши: [AD-4](..\source\design\define-agent-platform\design.md), [потоки памяти](..\architecture\components\memory\docs\how.md), спека agent-memory (А)
