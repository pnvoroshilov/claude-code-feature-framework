# 🚀 Quick Start: ClaudeTask MCP Setup

## Для использования в новом проекте

### 1. Запустите ClaudeTask сервисы

```bash
# Backend
cd "Claude Code Feature Framework/claudetask/backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 3333

# Frontend (новое окно терминала)
cd "Claude Code Feature Framework/claudetask/frontend"
REACT_APP_API_URL=http://localhost:3333/api PORT=3334 npm start
```

### 2. Инициализируйте MCP в вашем проекте

Откройте веб-интерфейс ClaudeTask:
```bash
# Откройте в браузере
http://localhost:3334
```

1. Перейдите в раздел "Project Setup"
2. Введите путь к вашему проекту
3. Нажмите "Initialize Project"
4. MCP конфигурация будет автоматически создана

### 3. Перезапустите Claude Code

После создания `.mcp.json` перезапустите Claude Code в вашем проекте.

### 4. Проверьте подключение

В Claude Code выполните:
```bash
mcp:get_task_queue
```

Если видите данные о задачах - всё работает! ✅

## Основные команды MCP

```bash
# Просмотр задач
mcp:get_task_queue
mcp:get_next_task
mcp:get_task 4

# Работа с задачами
mcp:analyze_task 4
mcp:update_status 4 "In Progress"
mcp:delegate_to_agent 4 "frontend-developer" "Implement feature"
```

## Что делать если не работает

### Проблема: "Capabilities: none"
✅ **Решение:** Убедитесь, что используете `native_stdio_server.py`, а не `stdio_server.py`

### Проблема: MCP не подключается
✅ **Решение:** 
1. Проверьте, что backend запущен на порту 3333
2. Убедитесь в правильности путей в `.mcp.json`
3. Перезапустите Claude Code

### Проблема: "Connection failed"
✅ **Решение:** Запустите backend сервер:
```bash
cd "Claude Code Feature Framework/claudetask/backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 3333
```

## Управление задачами

1. **Веб-интерфейс:** http://localhost:3334
2. **MCP команды в Claude Code**
3. **REST API:** http://localhost:3333

Готово! Теперь вы можете управлять задачами через Claude Code! 🎉