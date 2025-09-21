# ClaudeTask Framework - User Workflow

## Полный сценарий использования

### 1. Начальная установка фреймворка (один раз)

```bash
# Клонирование и запуск ClaudeTask
git clone https://github.com/user/claudetask.git
cd claudetask
docker-compose up -d
```

Фреймворк запускается на:
- **UI**: http://localhost:3000
- **API**: http://localhost:8000  
- **MCP Server**: http://localhost:3333

### 2. Инициализация нового проекта

#### Шаг 1: Подготовка проекта пользователя
```bash
# У пользователя есть проект
cd ~/my-awesome-project

# Запуск Claude Code на этой папке
claude-code .
```

#### Шаг 2: Подключение проекта к фреймворку
1. Открыть UI фреймворка: http://localhost:3000
2. Нажать "Initialize New Project"
3. Указать путь к проекту: `/Users/username/my-awesome-project`
4. Фреймворк автоматически создаст структуру:

```
my-awesome-project/
├── .mcp.json                       # MCP конфигурация для Claude Code
├── .claudetask/                    # Служебная папка фреймворка
│   ├── CLAUDE.md                   # Главные инструкции для Claude
│   ├── agents/                     # Субагенты для проекта
│   │   ├── task-analyzer.md
│   │   ├── feature-developer.md
│   │   ├── bug-fixer.md
│   │   ├── test-runner.md
│   │   └── code-reviewer.md
│   └── project.json                # Настройки проекта
├── worktrees/                      # Папка для git worktrees
└── [существующие файлы проекта]
```

#### Шаг 3: Автоматическая настройка MCP
Фреймворк автоматически создал `.mcp.json` в корне проекта с конфигурацией:

```json
{
  "mcpServers": {
    "claudetask": {
      "command": "python",
      "args": [
        "-m",
        "claudetask_mcp_bridge",
        "--project", "/Users/username/my-awesome-project",
        "--server", "http://localhost:3333"
      ]
    }
  }
}
```

#### Шаг 4: Перезапуск Claude Code
```bash
# Остановить текущую сессию Claude Code (Ctrl+C)
# Запустить заново
claude-code ~/my-awesome-project
```

### 3. Проверка интеграции

После перезапуска Claude Code автоматически:
1. Прочитает `.claudetask/CLAUDE.md`
2. Загрузит субагентов
3. Подключится к MCP серверу
4. Будет готов к работе с задачами

Проверочная команда в Claude:
```
"Проверь подключение к ClaudeTask"
```

Ожидаемый ответ:
```
✅ ClaudeTask подключен
- MCP сервер: активен
- Проект: /Users/username/my-awesome-project
- Задач в backlog: 0
```

### 4. Работа с задачами

#### Создание задач через UI
1. Открыть http://localhost:3000
2. Нажать "Create Task"
3. Заполнить:
   - Title: "Add user authentication"
   - Description: "Implement JWT authentication..."
   - Type: Feature
   - Priority: High
4. Задача появляется в колонке "Backlog"

#### Автоматическая работа Claude
```
User: "Возьми следующую задачу из бэклога"

Claude: Беру задачу #1 "Add user authentication" с высоким приоритетом.
        Начинаю анализ...
        
        [Автоматически через MCP]:
        - Получает задачу
        - Анализирует кодовую базу
        - Создает план реализации
        - Обновляет статус на "Analysis"
        - Сохраняет анализ в задаче
        - Переводит в "Ready"
        
Claude: Анализ завершен. Задача готова к реализации.
        Начинаю разработку?

User: "Да, начинай"

Claude: [Автоматически]:
        - Создает git worktree
        - Создает feature branch
        - Реализует функционал
        - Пишет тесты
        - Коммитит изменения
        - Обновляет статус на "Testing"
        - Запускает тесты
        - При успехе → "Code Review"
        - Создает PR
        - Проводит self-review
        - Мержит в main
        - Обновляет статус на "Done"
```

### 5. Структура CLAUDE.md в проекте

```markdown
# Project: My Awesome Project

## ClaudeTask Integration
You are working with ClaudeTask framework. Tasks are managed through MCP protocol.

## Available Commands
- `mcp:get_next_task` - Get highest priority task
- `mcp:analyze_task <id>` - Analyze task
- `mcp:update_status <id> <status>` - Update task status
- `mcp:create_worktree <id>` - Create worktree for task

## Project Specific Configuration
- Language: Python/JavaScript
- Testing: pytest/jest
- Build: make build
- Deploy: Not configured

## Workflow
1. Always check for tasks in ClaudeTask first
2. Work in git worktrees, never in main
3. Follow the task workflow strictly
4. Update status in real-time

## Project Context
[Auto-generated project information]
- Main technologies: React, FastAPI
- Database: PostgreSQL
- Key directories: src/, api/, tests/
```

### 6. Типичные команды пользователя

```
"Что есть в бэклоге?" → Claude через MCP получает список задач
"Возьми задачу #5" → Claude начинает работу с конкретной задачей  
"Какой статус у задачи #3?" → Claude проверяет через MCP
"Проанализируй все задачи в бэклоге" → Claude последовательно анализирует
"Покажи мой прогресс" → Claude показывает статистику по задачам
```

### 7. Файловая структура после инициализации

```
my-awesome-project/
├── .mcp.json                      # MCP конфигурация для Claude Code
├── .claudetask/
│   ├── CLAUDE.md                   # Главный файл инструкций
│   ├── agents/                     # Копии агентов из фреймворка
│   ├── project.json               # {"path": "/path/to/project", "name": "My Project"}
│   └── templates/                  # Шаблоны для задач
│       ├── feature.md
│       └── bug.md
├── .git/
├── worktrees/                      # Создается автоматически
│   └── task-1-auth/               # Worktree для задачи #1
├── src/                           # Код проекта
└── README.md
```

### 8. Переключение между проектами

Если у пользователя несколько проектов:

1. В UI фреймворка выбрать другой проект
2. Фреймворк обновит MCP конфигурацию
3. Перезапустить Claude Code в папке нового проекта
4. Claude автоматически подхватит контекст нового проекта

### 9. Обновление конфигурации

Через UI можно:
- Редактировать CLAUDE.md
- Добавлять кастомных субагентов
- Настраивать git workflow
- Изменять статусы задач
- Настраивать автоматизацию

Изменения применяются сразу, но для полного эффекта нужен перезапуск Claude Code.

### 10. Деинициализация проекта

Если нужно отключить фреймворк от проекта:
1. В UI выбрать "Disconnect Project"
2. Фреймворк удалит `.claudetask/` папку
3. Очистит worktrees
4. Сохранит историю задач в архив