# Интеграции: Инфраструктура

← компонент · Deploy · методология

<div class="api-head">
<div><span class="about-label">Базовый адрес</span> ingress Traefik</div>
<div><span class="about-label">Аутентификация</span> TLS</div>
</div>

## Входные точки

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-get">GET</span> | `https://<домен>/` | <span class="st st-ok">✅ есть</span> | web ICPlan | Пользователи · сессия | US-INF-02 | FR-161 | I21 |
| <span class="m m-get">GET</span> | `https://<домен>/api/*` · `/mcp` | <span class="st st-ok">✅ есть</span> | api и MCP ICPlan | Пользователи, внешние агенты · сессия / ключ | US-INF-02 | FR-161 | I21 |
