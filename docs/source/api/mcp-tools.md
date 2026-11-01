# Интеграции: MCP / Tools

← компонент · Deploy · методология

<div class="api-head">
<div><span class="about-label">Базовый адрес</span> MCP-серверы по протоколу MCP (streamable HTTP)</div>
<div><span class="about-label">Аутентификация</span> ключ агента / секрет сервера</div>
</div>

## Протокол MCP

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-post">POST</span> | `tools/list` | <span class="st st-ok">✅ есть</span> | тулы сервера (фильтр по allowlist агента) | Harness · ключ | US-MCP-02 | FR-177 | I9 |
| <span class="m m-post">POST</span> | `tools/call` | <span class="st st-ok">✅ есть</span> | вызов тула | Harness · ключ | US-MCP-02, US-HAR-01 | FR-178, FR-182 | I9 |
