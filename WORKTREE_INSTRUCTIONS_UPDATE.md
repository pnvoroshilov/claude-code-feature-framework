# Worktree-Aware CLAUDE.md Generation

## Что было сделано

Добавлена логика в `claude_config_generator.py` для **автоматической адаптации инструкций** в `CLAUDE.md` в зависимости от настройки `worktree_enabled`.

## Как это работает

### 1. Когда `worktree_enabled = True` (по умолчанию)

В сгенерированный `CLAUDE.md` добавляется секция:

```markdown
## ✅ GIT WORKTREES ENABLED

**This project uses Git worktrees for task isolation.**

### How worktrees work:
- ✅ Each task gets isolated workspace
- ✅ Parallel development
- ✅ Clean separation
- ✅ Automatic cleanup

### Worktree workflow:
1. Create worktree: `mcp:create_worktree <task_id>`
2. Work in: `worktrees/task-{id}/`
3. After merge: automatic cleanup

### Important worktree rules:
- ⚠️ NEVER delete worktrees manually
- ⚠️ ONLY delete when explicitly requested
- ⚠️ Maximum 3 parallel worktrees
```

### 2. Когда `worktree_enabled = False`

В сгенерированный `CLAUDE.md`:

**Добавляется предупреждение:**
```markdown
## ⚠️ GIT WORKTREES DISABLED

**This project has Git worktrees DISABLED.**

### What this means:
- ❌ DO NOT use `git worktree` commands
- ❌ DO NOT create worktrees for tasks
- ❌ DO NOT use `mcp:create_worktree` command
- ✅ Work directly in main branch
- ✅ Use standard git branching instead

### When working on tasks:
1. Work in the main branch for simple changes
2. For complex features: `git checkout -b feature/task-{id}`
3. Do NOT attempt to create worktrees

**IMPORTANT**: If you see instructions about worktrees elsewhere, IGNORE them.
```

**Удаляется секция:**
- Секция "⛔ NEVER DELETE WORKTREES WITHOUT EXPLICIT USER REQUEST" полностью удаляется из шаблона

## Где применяется

Эта логика работает в файле: `claudetask/backend/app/services/claude_config_generator.py`

Функция: `generate_claude_md()`

Параметры:
- `project_mode`: "simple" или "development"
- `worktree_enabled`: `True` или `False`

## Когда регенерируется CLAUDE.md

`CLAUDE.md` регенерируется в следующих случаях:
1. При создании нового проекта через `initialize_project()`
2. При явном вызове API: `POST /api/projects/{project_id}/instructions/regenerate`
3. Через веб-интерфейс: кнопка "Regenerate CLAUDE.md"

## Как использовать

### Для пользователя:

1. Откройте веб-интерфейс ClaudeTask
2. Перейдите в настройки проекта
3. Измените параметр `worktree_enabled`
4. Нажмите "Regenerate CLAUDE.md"
5. Файл `CLAUDE.md` будет обновлен с правильными инструкциями

### Для разработчика:

```python
# Регенерировать CLAUDE.md программно
await ProjectService.regenerate_claude_md(db, project_id)

# Параметр worktree_enabled берется из:
# ProjectSettings.worktree_enabled для проекта
```

## Преимущества

✅ **Автоматическая адаптация** - Claude получает правильные инструкции для режима работы
✅ **Предотвращение ошибок** - Claude не пытается создавать worktrees когда они отключены
✅ **Ясные указания** - Явные инструкции что делать в каждом режиме
✅ **Удаление конфликтующих секций** - Противоречивые инструкции удаляются

## Пример использования

### Проект с worktrees (microservices):
```
project_mode = "development"
worktree_enabled = True
→ Claude создает worktrees для параллельной работы
```

### Проект без worktrees (simple app):
```
project_mode = "development"
worktree_enabled = False
→ Claude работает в main branch или feature branches
```

## Изменения в коде

**Файл**: `claudetask/backend/app/services/claude_config_generator.py`

**Строки**: 193-293

**Ключевая логика**:
1. Проверяет `project_mode == "development"`
2. Если `worktree_enabled=True`: добавляет инструкции про worktrees
3. Если `worktree_enabled=False`: добавляет предупреждение + удаляет worktree-секции из шаблона
