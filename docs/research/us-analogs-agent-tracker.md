# R&D: Потоки аналогов «трекер + ИИ-агенты»

← [Все R&D](README.md) · методология · методика User Stories · компонент: **[ICPlan](../architecture/components/icplan/README.md)** (и связанные) · статус: **Adopt — истории написаны**

## Итог

| | |
|---|---|
| **Вопрос** | Какие пользовательские потоки и точки входа нужны интеграции [ICPlan](../architecture/components/icplan/README.md) с платформой агентов, чтобы покрыть всех пользователей и сценарии |
| **Вид R&D** | потоки пользователей (METHOD.md), не выбор технологии |
| **Аналоги** | Linear Agents, GitHub Copilot coding agent, Jira + Rovo agents, Devin (интеграция с Jira / Slack) |
| **Результат** | 29 историй [ICPlan](../architecture/components/icplan/README.md) по персонам: пользователь, администратор, агент-исполнитель и эксплуатация ([персона Э](..\source\personas.md): [US-ICP-06](../architecture/components/icplan/stories/us-icp-06.yaml) — видеть, в сети ли платформа агентов); истории остальных компонентов. Открытые вопросы по путям без требований закрыты решениями [AD-17](..\source\design\define-agent-platform\design.md) (вердикт, проверка со мной, остановка процесса, повтор шага, версии процесса, указания во время работы, выключение агента, тестовый запуск, сводка) и [AD-18](..\source\design\define-agent-platform\design.md); в историях [ICPlan](../architecture/components/icplan/README.md) открытых вопросов нет |
| **Важность потоков** | все потоки матрицы, кроме журнала изменений настроек ([US-PM-07](../architecture/components/platform-module/stories/us-pm-07.yaml), этап 4), — в MVP: их истории в этапах 1–3 (сводка историй, колонка «Этап · задачи») |
| **Главные находки** | у всех аналогов есть: состояния сессии агента (ждёт ввода, ошибка, готово), остановка пользователем, указания во время работы, итерация через комментарии, учёт стоимости на сессию, агент на переходе workflow, админ решает, где и кому доступны агенты |

## Идея и работы (JTBD)

Идея интеграции: **[ICPlan](../architecture/components/icplan/README.md) — рабочее место людей, где агенты получают работу и куда возвращают результат; процесс задачи идёт сам, а человек управляет им и видит результат и стоимость.**

| Актор | Когда… | хочу… | чтобы… |
|---|---|---|---|
| Пользователь | есть работа, которую может сделать агент | поручить её из того места, где я работаю (задача, комментарий, чат, бот) | не переключаться в другой инструмент |
| Пользователь | агент работает | видеть ход, отвечать на вопросы, поправлять, останавливать | вовремя вмешаться |
| Пользователь | агент закончил | принять или вернуть с заметкой | дальше шёл только годный результат |
| Пользователь | у меня много задач с агентами | видеть сводку: в работе, в очереди, время, закрыто/открыто, токены и $ | понимать загрузку и стоимость |
| Администратор | нужен новый исполнитель | создать, настроить, проверить, выключить, удалить агента | агенты были управляемыми |
| Администратор | меняется процесс команды | создать и менять процесс, подключать агентов к шагам | процесс работал без кода |
| Администратор | агенты работают давно | видеть статистику и затраты по агентам | улучшать агентов |
| Агент | получил задачу | иметь весь контекст и очередь | продолжать, а не начинать заново |
| Эксплуатация | задачи не берутся агентами | видеть, в сети ли платформа агентов ([US-ICP-06](../architecture/components/icplan/stories/us-icp-06.yaml)) | понимать, почему задачи не берутся |

## Матрица потоков

| Поток | Linear | GitHub Copilot | Jira + Rovo | Devin | У нас | Решение | Важность |
|---|---|---|---|---|---|---|---|
| Поручить задачу агенту полем | делегат (человек остаётся исполнителем) | назначить issue на Copilot | исполнитель — агент | метка `devin` | поле «делегат» | [US-ICP-08](../architecture/components/icplan/stories/us-icp-08.yaml) | MVP · этап 2 |
| Упоминание в комментарии | упоминание создаёт сессию | — | — | — | `@агент` | [US-ICP-09](../architecture/components/icplan/stories/us-icp-09.yaml) | MVP · этап 2 |
| Агент на переходе процесса | — | — | агент на переходе workflow | — | шаг процесса | [US-ICP-01](../architecture/components/icplan/stories/us-icp-01.yaml), [US-ICP-05](../architecture/components/icplan/stories/us-icp-05.yaml) | MVP · этап 3 |
| Состояния работы агента | pending / active / awaitingInput / error / complete | сессия, журнал | — | сессия | статусы запуска + «ждёт ответа» | [US-ICP-02](../architecture/components/icplan/stories/us-icp-02.yaml), [US-ICP-11](../architecture/components/icplan/stories/us-icp-11.yaml), [US-ICP-12](../architecture/components/icplan/stories/us-icp-12.yaml) | MVP · этапы 1–3 |
| Журнал работы вживую | активности (мысли, тулы, ответ) | «View session», живой журнал | история задачи | — | таймлайн | [US-ICP-02](../architecture/components/icplan/stories/us-icp-02.yaml), [US-OBS-01](../architecture/components/observability/stories/us-obs-01.yaml) | MVP · этапы 2–3 |
| Вопрос агента пользователю | prompt for clarification | — | — | план + «Start session?» | вопрос → ответ | [US-ICP-11](../architecture/components/icplan/stories/us-icp-11.yaml), [US-HAR-07](../architecture/components/harness/stories/us-har-07.yaml) | MVP · этап 1 |
| Указание во время работы | — | комментарий-руление в PR | — | чат сессии | чат задачи | [US-ICP-10](../architecture/components/icplan/stories/us-icp-10.yaml), [US-HAR-06](../architecture/components/harness/stories/us-har-06.yaml) | MVP · этапы 2–3 |
| Остановка пользователем | «Send stop request» | «Stop session» | — | — | отмена запуска, остановка процесса | [US-ICP-04](../architecture/components/icplan/stories/us-icp-04.yaml), [US-ICP-14](../architecture/components/icplan/stories/us-icp-14.yaml) | MVP · этап 2 |
| Итерация по результату | — | комментарии к PR | одобрить → передать | — | «не выполнено» с заметкой | [US-ICP-13](../architecture/components/icplan/stories/us-icp-13.yaml) | MVP · этап 3 |
| Человек одобряет до продолжения | — | PR на ревью | ревью и одобрение агентного результата | «Start session?», карточки двигает человек | проверка со мной на задаче | [US-ICP-15](../architecture/components/icplan/stories/us-icp-15.yaml) | MVP · этап 3 |
| Агент не двигает доску сам | — | — | — | да (двигает человек) | переход делает [ICPlan](../architecture/components/icplan/README.md) по процессу | [FR-197](../architecture/components/icplan/prd.md) | MVP · этап 3 (задача 3.6) |
| Стоимость сессии | — | premium request на сессию и руление | — | ACU | токены и $ по задаче, сводка | [US-ICP-12](../architecture/components/icplan/stories/us-icp-12.yaml), [US-LLM-03](../architecture/components/llm-gateway/stories/us-llm-03.yaml) | MVP · этап 3 |
| Админ: где и кому доступны агенты | guidance на уровнях рабочее пространство / команда | планы и политики | админ сайта включает агентов, «что такое готово» | интеграции команды | агент → проекты, доступы | [US-ICP-20](../architecture/components/icplan/stories/us-icp-20.yaml), [US-SBX-06](../architecture/components/sandbox/stories/us-sbx-06.yaml) | MVP · этапы 1–2 |
| Права и аудит | — | — | агенты соблюдают права и аудит | — | журнал изменений, журнал guardrails | [US-PM-07](../architecture/components/platform-module/stories/us-pm-07.yaml), [US-GRD-05](../architecture/components/guardrails/stories/us-grd-05.yaml) | журнал guardrails — MVP · этап 3 ([US-GRD-05](../architecture/components/guardrails/stories/us-grd-05.yaml)); журнал изменений — после MVP · этап 4 ([US-PM-07](../architecture/components/platform-module/stories/us-pm-07.yaml)) |
| Регулярная работа | — | — | — | — | расписание агента (есть в [ICPlan](../architecture/components/icplan/README.md)) | [US-ICP-19](../architecture/components/icplan/stories/us-icp-19.yaml) | MVP · этап 2 |
| Тест агента до включения | — | — | — | — | тестовый запуск | [US-ICP-24](../architecture/components/icplan/stories/us-icp-24.yaml) | MVP · этап 1 |
| Статистика агентов | — | — | — | — | запуски, успех, возвраты, $ | [US-ICP-28](../architecture/components/icplan/stories/us-icp-28.yaml) | MVP · этап 3 |

«—» — в найденных источниках не подтверждено; функции аналогов не додумывались. **Важность:** MVP — истории потока в этапах 1–3, после MVP — только этап 4 (этап — из колонки «Этап · задачи» сводки историй и сводок историй компонентов).

## Отброшено фильтром необходимости

| Путь | Почему нет |
|---|---|
| Агент сам двигает задачу по доске | заменено переходом по итогу ([FR-197](../architecture/components/icplan/prd.md)): однозначность процесса |
| Отдельное приложение для работы с агентами | противоречит идее: работа — в [ICPlan](../architecture/components/icplan/README.md) |
| Подписки и тарифы как у SaaS | платформа своя; вместо тарифов — бюджеты ([US-PM-06](../architecture/components/platform-module/stories/us-pm-06.yaml)) |
| Пользователь видит и правит память агента | путь не вытекает из идеи [Memory](../architecture/components/memory/README.md) (память — для агента); удаление памяти — администратором ([US-MEM-03](../architecture/components/memory/stories/us-mem-03.yaml)). Если нужно — вопрос пользователю |

## Источники

Дата поиска и чтения не зафиксирована. В скобках — уровень доказательства по методологии.

- Linear: [Agent Interaction](https://linear.app/developers/agent-interaction) (Б), [Getting started](https://linear.app/developers/agents) (Б), [Agent Interaction SDK](https://linear.app/blog/our-approach-to-building-the-agent-interaction-sdk) (Б, блог производителя)
- GitHub Copilot coding agent: [работа над issue](https://docs.github.com/en/copilot/using-github-copilot/coding-agent/using-copilot-to-work-on-an-issue) (Б), [отслеживание сессий](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/track-copilot-sessions) (Б)
- Jira + Rovo: [работа с ИИ-агентами в задачах](https://support.atlassian.com/jira-software-cloud/docs/collaborate-on-work-items-with-ai-agents/) (Б), [агенты в Jira](https://www.atlassian.com/blog/rovo/ai-agents-in-jira) (Б, блог производителя)
- Devin: [интеграции и тестирование (DataCamp)](https://www.datacamp.com/tutorial/devin-ai-integrations-testing) (В, статья практиков — не первичный источник)
- Истории: [ICPlan](../architecture/components/icplan/README.md), покрытие (наши документы)
