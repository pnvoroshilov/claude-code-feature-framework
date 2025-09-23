# ClaudeTask MCP Server

## Описание

MCP (Model Context Protocol) сервер для интеграции ClaudeTask с Claude Code. Предоставляет инструменты для управления задачами через MCP протокол.

## Доступные серверы

### 1. HTTP Server (порт 3335)
Веб-сервер для доступа к MCP tools через HTTP API.

**Запуск:**
```bash
cd claudetask/mcp_server
python http_server.py
```

### 2. Native STDIO Server  
Нативный MCP сервер для интеграции с Claude Code через STDIO протокол.

**Запуск:**
```bash
python3 /path/to/claudetask/mcp_server/native_stdio_server.py
```

## Настройка в другом проекте

### Шаг 1: Создайте файл `.mcp.json` в корне вашего проекта:

```json
{
  "mcpServers": {
    "claudetask": {
      "command": "python3",
      "args": [
        "/Users/pavelvorosilov/Desktop/Work/Start Up/Claude Code Feature Framework/claudetask/mcp_server/native_stdio_server.py"
      ],
      "env": {
        "CLAUDETASK_PROJECT_ID": "ff9cc152-3f38-49ab-bec0-0e7cbf84594a",
        "CLAUDETASK_PROJECT_PATH": "/path/to/your/project",
        "CLAUDETASK_BACKEND_URL": "http://localhost:3333"
      }
    }
  }
}
```

### Шаг 2: Убедитесь, что запущены необходимые сервисы:

1. **ClaudeTask Backend** (порт 3333):
```bash
cd claudetask/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 3333
```

2. **ClaudeTask Frontend** (порт 3334):
```bash
cd claudetask/frontend
REACT_APP_API_URL=http://localhost:3333/api PORT=3334 npm start
```

3. **MCP HTTP Server** (порт 3335) - опционально:
```bash
cd claudetask/mcp_server
python http_server.py
```

### Шаг 3: Перезапустите Claude Code

После создания `.mcp.json` файла, перезапустите Claude Code в вашем проекте. MCP сервер должен автоматически подключиться.

## Доступные MCP Tools

- `get_task_queue` - Просмотр очереди задач
- `get_next_task` - Получить следующую задачу с высшим приоритетом
- `get_task <task_id>` - Получить детали конкретной задачи
- `analyze_task <task_id>` - Анализировать задачу
- `update_task_analysis <task_id> "<analysis>"` - Сохранить анализ задачи
- `update_status <task_id> <status>` - Обновить статус задачи
- `create_worktree <task_id>` - Создать git worktree для задачи
- `delegate_to_agent <task_id> <agent> "<instructions>"` - Делегировать задачу агенту
- `complete_task <task_id>` - Завершить задачу и слить ветку
- `start_claude_session <task_id>` - Запустить Claude сессию для задачи
- `get_session_status <task_id>` - Получить статус Claude сессии

## Использование в Claude Code

После настройки MCP сервера, вы можете использовать команды в Claude Code:

```bash
# Получить очередь задач
mcp:get_task_queue

# Получить следующую задачу
mcp:get_next_task

# Получить конкретную задачу
mcp:get_task 4

# Обновить статус задачи
mcp:update_status 4 "In Progress"
```

## Устранение проблем

### Проблема: "Capabilities: none" в статусе MCP
**Решение:** Используйте `native_stdio_server.py` вместо `stdio_server.py`

### Проблема: MCP сервер не подключается
**Решение:** 
1. Проверьте, что backend запущен на порту 3333
2. Проверьте правильность путей в `.mcp.json`
3. Перезапустите Claude Code

### Проблема: Tools не отображаются
**Решение:**
1. Убедитесь, что используете правильный сервер (native_stdio_server.py)
2. Проверьте логи сервера в stderr
3. Проверьте доступность backend API

## Разработка

Для добавления новых MCP tools:

1. Добавьте определение tool в `claudetask_mcp_bridge.py` в методе `handle_list_tools()`
2. Добавьте обработчик в методе `handle_call_tool()`
3. Реализуйте логику в соответствующем методе `_your_tool_name()`
4. Обновите HTTP сервер, если необходимо