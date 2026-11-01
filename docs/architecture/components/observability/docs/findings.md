# Замечания: Observability

← компонент · подтверждения документов · правило

## Проверка ролями (пачка, 13.10.2026)

Пакетная проверка по карточкам (агент doc-batch-reviewer, Sonnet): все роли страниц компонента за проход; механику до ролей закрыл lint.

| № | Документ | Роли | Отклонение | Как закрыть | Где | Методология | Статус |
|---|---|---|---|---|---|---|---|
| Z-OBS-1 | components/observability/agregaty-zatrat/index.md | А | retention_days=90 в params агрегатов, но [FR-151](../prd.md) требует сохранять агрегаты после удаления событий → уточнить, к чему относится срок и откуда агрегаты берут историю | правка | см. отклонение | нет — проверка ролью | ✅ retention_days убран из params агрегатов, в does: история из журнала LiteLLM, не из run_event; удаление событий агрегаты не затрагивает ([FR-151](../prd.md)) |
| Z-OBS-2 | data-by-component/observability/index.md | Р | Нет ни одной операции: чем запрашиваются затраты ([FR-150](../prd.md)), сводка ([FR-152](../prd.md)), события запуска — эндпоинтов и форматов нет → описать операции и входы/выходы | правка | см. отклонение | нет — проверка ролью | ✅ отклонено: своего API у [Observability](../README.md) нет по решению — затраты, сводка и статистика отдаются API [ICPlan](../../icplan/README.md) ([I20](../../icplan/integrations/I20.yaml): GET /issues/:issueId/costs, /me/agent-summary, analytics/agent-run-stats), операции уже в ops блока agregaty-zatrat; в docs/api/observability.md добавлено явное 'Своего API нет' |
| Z-OBS-3 | docs/api/observability.md | А | На странице нет ни таблиц (run_event), ни связей: 11 требований ([FR-150](../prd.md), [FR-152](../prd.md), [FR-136](../../llm-gateway/prd.md)) без данных, из которых считаются затраты и сводка → определить данные и связи | правка | см. отклонение | нет — проверка ролью | ✅ отклонено: таблицу run_event и agent_run ведёт [ICPlan](../../icplan/README.md) (data/tables, владелец [ICPlan](../../icplan/README.md)), у [Observability](../README.md) своих таблиц нет; затраты читаются из LiteLLM_SpendLogs (блок data); страница API пояснена |
| Z-OBS-4 | docs/api/observability.md | Р | Нет ни одной операции или эндпоинта, хотя [FR-150](../prd.md) и [FR-152](../prd.md) требуют запросов затрат и сводки; нельзя начать реализацию → добавить операции с входом/выходом | правка | см. отклонение | нет — проверка ролью | ✅ отклонено: эндпоинты есть в [ICPlan](../../icplan/README.md) ([I20](../../icplan/integrations/I20.yaml)), у [Observability](../README.md) собственных операций нет по решению; на странице docs/api/observability.md добавлено явное пояснение |
