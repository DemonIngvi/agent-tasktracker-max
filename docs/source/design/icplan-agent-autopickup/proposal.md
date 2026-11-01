# Proposal

← README · схема: [architecture.md](..\..\..\architecture\components\icplan\docs\icplan-agent-autopickup-architecture.md) · задачи: [tasks.md](tasks.md)

## Why

В [ICPlan](../../../architecture/components/icplan/README.md) агент запускается только при смене поля «Делегат» или упоминании. Автоназначение на статус заполняет только «Исполнителя» и запуск не создаёт (проверено: `issues/service.ts`, `enqueueDelegateRun`). Поэтому процесс «задача пришла в статус / создана с типом → агент сам подхватил» не работает. Процесс (статусы, типы, порядок) пользователь настраивает в [ICPlan](../../../architecture/components/icplan/README.md) сам; [ICPlan](../../../architecture/components/icplan/README.md) должен уметь автоматически отдавать задачу указанному агенту.

## What Changes

- Тип задачи задаёт процесс; шаг процесса = колонка + агент + переход при успехе и при неудаче + лимит запусков + проверка человеком ([AD-17](../../../architecture/decisions/AD-17.yaml)).
- Переход между шагами делает [ICPlan](../../../architecture/components/icplan/README.md) по итогу запуска, а не агент ([FR-197](../../../architecture/components/icplan/prd.md)); у агента — своя очередь ([FR-198](../../../architecture/components/icplan/prd.md)).
- Эффект Действия «делегировать агенту».
- Защита от дублей запуска и понятный приоритет правил.
- Передача между этапами: следующий агент получает ссылки на результаты предыдущего.
- Видимость автоподхвата в истории задачи.

Изменения только в [ICPlan](../../../architecture/components/icplan/README.md). Сроки — при планировании.

## Capabilities

### New Capabilities
- `icplan-agent-autopickup`: процесс задачи по типу: шаги с агентами, переходы по итогу запуска, эффект Действия

### Modified Capabilities
<!-- нет -->

## Impact

- Форк `itsaplan`: модули `columns`, `issue-types`, `actions`, `issues`, `agents/core`; UI редактора процессов и Действий.
- Не затрагивает процесс пользователя: какие шаги, агенты и переходы — решает пользователь.
