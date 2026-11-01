# Интеграции: Memory API

← компонент · Deploy · методология

<div class="api-head">
<div><span class="about-label">Базовый адрес</span> `http://memory-api:8085`</div>
<div><span class="about-label">Аутентификация</span> токен запуска (Harness), сервисный токен (администрирование)</div>
</div>

## Память

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-get">GET</span> | `/context?issueId=&agentId=` | <span class="st st-new">🆕 новое</span> | контекст запуска: M1, M2, M3 по профилю; M1 и M2 старше `retention` профиля не отдаются (AD-25) | Harness · токен запуска | US-MEM-01, US-MEM-02, US-MEM-06 | FR-40, FR-39, FR-43 | I11 |
| <span class="m m-put">PUT</span> | `/m3/:issueId` | <span class="st st-new">🆕 новое</span> | записать состояние задачи (проверки до записи) | Harness (тул памяти) · токен запуска | US-MEM-01 | FR-39, FR-44 | I11 |
| <span class="m m-del">DELETE</span> | `/records/:level/:id` | <span class="st st-new">🆕 новое</span> | удалить запись | Администратор · сервисный токен | US-MEM-03 | FR-42 | I11 |
| <span class="m m-post">POST</span> | `/retention/run` | <span class="st st-new">🆕 новое</span> | очистка по срокам своих уровней: M3, позже M4; M1 и M2 в таблицах форка не удаляет — только фильтр чтения, строки удаляет ICPlan (AD-25) (CronJob) | Kubernetes CronJob · сервисный токен | US-MEM-10 | FR-43 | — |
