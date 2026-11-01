# Интеграции: Sandbox

← компонент · Deploy · методология

<div class="api-head">
<div><span class="about-label">Базовый адрес</span> своего API нет: среду создаёт Runner</div>
<div><span class="about-label">Аутентификация</span> —</div>
</div>

## Вызовы Runner к среде исполнения

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-post">POST</span> | `Docker API `/containers/create` · `/start`` | <span class="st st-ok">✅ есть</span> | создать и запустить контейнер по профилю | Agent Runner · сокет rootless Docker | US-SBX-01 | FR-82, FR-86, FR-89 | I6 |
| <span class="m m-del">DELETE</span> | `Docker API `/containers/:id`` | <span class="st st-ok">✅ есть</span> | уничтожить среду после запуска | Agent Runner · сокет | US-SBX-01 | FR-75 | I6 |
| <span class="m m-post">POST</span> | `Kubernetes `/api/v1/namespaces/itsaplan-agents/pods` (этап 4)` | <span class="st st-ok">✅ есть</span> | под запуска | Agent Runner · ServiceAccount | US-SBX-01 | FR-82 | I23 |
