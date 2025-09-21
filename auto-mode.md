# Механизм автоматического запуска Claude через MCP

## Концепция триггеров

### 1. Push-уведомления от Backend

Фреймворк может активно уведомлять Claude о новых задачах через MCP протокол.

#### Реализация на стороне Backend:
```python
class TaskNotificationService:
    def notify_claude_about_task(self, task):
        """Отправляет уведомление Claude через MCP."""
        if task.priority == "High":
            # Немедленное уведомление для высокого приоритета
            mcp_client.send_notification(
                "new_high_priority_task",
                {
                    "task_id": task.id,
                    "title": task.title,
                    "auto_start": True  # Автоматически начать работу
                }
            )
        else:
            # Добавление в очередь для обычных задач
            mcp_client.send_notification(
                "task_added_to_queue",
                {
                    "task_id": task.id,
                    "priority": task.priority
                }
            )
```

#### Обработка в Claude через MCP:
```python
# MCP Server handler
@mcp.notification_handler("new_high_priority_task")
async def handle_high_priority_task(notification):
    """Claude автоматически реагирует на задачи с высоким приоритетом."""
    task_id = notification["task_id"]
    
    # Триггер для Claude
    await claude_context.trigger_command(
        "start_task",
        {
            "task_id": task_id,
            "auto_mode": notification.get("auto_start", False)
        }
    )
```

### 2. Периодическая проверка (Polling)

Claude может периодически проверять наличие новых задач.

#### Конфигурация в CLAUDE.md:
```markdown
## Автоматический режим работы
- Проверять новые задачи каждые 5 минут
- Автоматически брать задачи с приоритетом High
- Запрашивать подтверждение для Medium приоритета
- Игнорировать Low приоритет в автоматическом режиме
```

#### MCP команда для проверки:
```python
@mcp.scheduled_task(interval_minutes=5)
async def check_pending_tasks():
    """Периодическая проверка новых задач."""
    tasks = await get_pending_tasks()
    
    high_priority = [t for t in tasks if t.priority == "High"]
    if high_priority:
        return {
            "action": "auto_start",
            "task": high_priority[0],
            "message": f"🔴 Обнаружена критическая задача: {high_priority[0].title}"
        }
    
    medium_priority = [t for t in tasks if t.priority == "Medium"]
    if medium_priority:
        return {
            "action": "request_confirmation",
            "task": medium_priority[0],
            "message": f"🟡 Доступна задача: {medium_priority[0].title}"
        }
    
    return {"action": "none", "message": "Нет новых задач"}
```

### 3. Event-Driven режим

Система может работать по событиям, когда определенные действия автоматически триггерят Claude.

#### События-триггеры:
1. **Создание задачи с критическим багом** → Немедленный анализ и исправление
2. **Завершение блокирующей задачи** → Автоматический старт зависимых задач
3. **Провал тестов в CI/CD** → Создание и выполнение задачи на исправление
4. **PR review request** → Автоматический код-ревью

#### Пример обработки события:
```python
@mcp.event_handler("critical_bug_created")
async def handle_critical_bug(event):
    """Немедленная реакция на критический баг."""
    bug_task = event["task"]
    
    # Останавливаем текущую работу
    await pause_current_work()
    
    # Переключаемся на критический баг
    await switch_to_task(bug_task.id)
    
    # Автоматически начинаем работу
    return {
        "action": "immediate_start",
        "reason": "Critical bug requires immediate attention",
        "expected_time": estimate_fix_time(bug_task)
    }
```

## Режимы работы Claude

### 1. Полностью автоматический режим
```python
class AutoMode:
    """Claude работает автономно без запросов пользователя."""
    
    settings = {
        "auto_take_tasks": True,
        "auto_analyze": True,
        "auto_implement": True,
        "auto_test": True,
        "auto_merge": True,
        "require_confirmation": False,
        "priority_threshold": "Low"  # Берет все задачи
    }
```

### 2. Полуавтоматический режим
```python
class SemiAutoMode:
    """Claude запрашивает подтверждение на ключевых этапах."""
    
    settings = {
        "auto_take_tasks": True,
        "auto_analyze": True,
        "auto_implement": False,  # Запрос перед началом разработки
        "auto_test": True,
        "auto_merge": False,      # Запрос перед мержем
        "require_confirmation": True,
        "priority_threshold": "Medium"
    }
```

### 3. Ручной режим (по умолчанию)
```python
class ManualMode:
    """Claude работает только по явным командам пользователя."""
    
    settings = {
        "auto_take_tasks": False,
        "auto_analyze": False,
        "auto_implement": False,
        "auto_test": False,
        "auto_merge": False,
        "require_confirmation": True,
        "priority_threshold": None
    }
```

## Команды управления режимом

### Включение автоматического режима:
```
User: "Включи автоматический режим для критических задач"
Claude: Автоматический режим активирован.
        Буду автоматически брать и выполнять задачи с приоритетом High.
        Текущих задач в очереди: 0
```

### Настройка режима:
```
User: "Работай в автоматическом режиме, но спрашивай перед мержем"
Claude: Настроен полуавтоматический режим:
        ✅ Автоматический анализ и разработка
        ⚠️  Запрос подтверждения перед мержем
```

### Остановка автоматического режима:
```
User: "Стоп, переключись в ручной режим"
Claude: Автоматический режим остановлен.
        Текущая задача #5 приостановлена.
        Жду ваших команд.
```

## Безопасность и ограничения

### Защитные механизмы:
1. **Лимит автоматических действий** - не более N задач подряд без подтверждения
2. **Проверка критических изменений** - запрос при удалении файлов, изменении конфигураций
3. **Откат при ошибках** - автоматический revert при провале тестов
4. **Логирование всех действий** - полная история автоматических операций

### Конфигурация ограничений:
```json
{
  "auto_mode_limits": {
    "max_consecutive_tasks": 5,
    "max_files_changed": 50,
    "require_confirmation_for": [
      "delete_files",
      "modify_config",
      "force_push",
      "database_migrations"
    ],
    "pause_on_test_failure": true,
    "rollback_on_error": true
  }
}
```

## Интеграция с UI

### Индикатор режима в UI:
```
┌─────────────────────────────────┐
│ Claude Status: 🟢 AUTO MODE     │
│ Current: Task #3 (In Progress)   │
│ Queue: 2 tasks pending           │
│ [Pause] [Switch to Manual]       │
└─────────────────────────────────┘
```

### Лог автоматических действий:
```
[10:15] 🤖 Auto-mode started
[10:16] 📋 Took task #3 "Fix login bug"
[10:17] 🔍 Analysis completed
[10:20] 💻 Implementation done
[10:22] ✅ Tests passed
[10:23] 🔀 PR created
[10:24] ⏸️  Waiting for review (manual step required)
```