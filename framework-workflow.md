# ClaudeTask Framework - Workflow Architecture

На основе изучения AI Tasks and Goals, вот адаптированный workflow для фреймворка ClaudeTask:

## 🎯 Основные принципы работы фреймворка

### 1. КООРДИНАТОР (Claude Main Flow)
- **Анализирует задачи** из ClaudeTask UI
- **Никогда не меняет код напрямую** 
- **Создает worktree** для каждой задачи
- **Делегирует субагентам** с полным контекстом
- **Координирует merge** после проверок
- **Обновляет статусы** в UI через MCP

### 2. СУБАГЕНТЫ (Исполнители)
- **Только они меняют код**
- **Работают в изолированных worktrees**
- **Получают детальный контекст** от координатора
- **Возвращают результаты** для проверки
- **Специализированы** по областям (frontend, backend, AI, тесты)

### 3. АВТОМАТИЧЕСКАЯ ПРОВЕРКА
- **Code Review** после изменений
- **Testing** перед merge
- **Статус обновляется** автоматически в UI

## 📋 Структура задач в фреймворке

### Формат задачи (из Features/web_features_new.md)
```yaml
task:
  id: "task-123"
  title: "Краткое название"
  priority: "High|Medium|Low"
  type: "Feature|Bug"
  status: "Backlog|Analysis|Ready|In Progress|Testing|Code Review|Done"
  sub_agent: "mobile-react-expert|python-api-expert|ai-implementation-expert"
  parallelizable: true|false
  conflicts: "список потенциальных конфликтов"
  description: "Детальное описание"
  functionality: "Список функций для реализации"
  value: "Ценность для пользователя"
```

## 🌳 Worktree Structure для задач

```
/user-project/                      # main branch
/user-project/worktrees/
  ├── task-123-feature/             # Worktree для задачи #123
  ├── task-124-bugfix/              # Worktree для задачи #124
  └── task-125-feature/             # Worktree для задачи #125
```

### Принципы worktrees:
- **Каждая задача = отдельный worktree**
- **Максимум 3 задачи** разрабатываются параллельно
- **Автоматическое создание** при взятии задачи
- **Чистый merge** после завершения
- **Автоматическая очистка** после мержа

## 🔄 Task Workflow в фреймворке

### 1. Получение задачи (Backlog → Analysis)
```yaml
claude_action:
  - Получить задачу через MCP: get_next_task()
  - Проанализировать требования
  - Определить затрагиваемые файлы
  - Оценить сложность
  - Сохранить анализ: save_task_analysis()
  - Обновить статус: update_task_status("Analysis")
```

### 2. Подготовка к разработке (Analysis → Ready)
```yaml
preparation:
  - Создать worktree: git worktree add ./worktrees/task-{id}
  - Создать branch: feature/task-{id} или bugfix/task-{id}
  - Определить субагентов для делегирования
  - Подготовить контекст для субагентов
  - Обновить статус: update_task_status("Ready")
```

### 3. Делегирование субагентам (Ready → In Progress)
```yaml
delegation:
  agent: "определенный субагент"
  worktree: "./worktrees/task-{id}"
  task: "Что нужно сделать"
  context:
    - affected_files: ["список файлов"]
    - requirements: "детальные требования"
    - constraints: "ограничения"
  status: update_task_status("In Progress")
```

### 4. Выполнение задачи субагентами
Субагенты работают согласно своей специализации:

#### mobile-react-expert (Frontend)
- Область: `src/components/`, `src/pages/`, `src/hooks/`
- Технологии: React, TypeScript, Tailwind, Zustand
- Фокус: Mobile-first, доступность, производительность

#### python-api-expert (Backend)
- Область: `api/`, `models/`, `services/`
- Технологии: FastAPI, SQLAlchemy, Pydantic
- Фокус: REST API, валидация, бизнес-логика

#### ai-implementation-expert (AI/LLM)
- Область: `agents/`, `ai_services/`
- Технологии: LangChain, LangGraph, OpenAI
- Фокус: Промпты, агенты, AI workflows

### 5. Тестирование (In Progress → Testing)
```yaml
testing:
  - Субагент завершает работу
  - Запускаются автоматические тесты
  - Проверка функциональности
  - Обновить статус: update_task_status("Testing")
```

### 6. Code Review (Testing → Code Review)
```yaml
review:
  - Code review субагент проверяет изменения
  - Проверка стандартов кода
  - Проверка производительности
  - Создание PR: gh pr create
  - Обновить статус: update_task_status("Code Review")
```

### 7. Завершение (Code Review → Done)
```yaml
completion:
  - Merge в main: git merge feature/task-{id}
  - Очистка worktree: git worktree remove
  - Обновить статус: update_task_status("Done")
  - Уведомить UI о завершении
```

## 🤖 Субагенты фреймворка

### Основные субагенты (из .claude/agents/)

1. **mobile-react-expert**
   - Frontend разработка
   - React компоненты
   - UI/UX оптимизация

2. **python-api-expert**
   - Backend API
   - База данных
   - Бизнес-логика

3. **ai-implementation-expert**
   - AI агенты
   - LLM интеграции
   - Промпт-инжиниринг

4. **fullstack-code-reviewer**
   - Проверка кода
   - Стандарты качества
   - Рекомендации

5. **background-tester**
   - Автоматическое тестирование
   - E2E тесты
   - Регрессионное тестирование

## 📊 Интеграция с UI через MCP

### MCP команды для UI
```python
# Получение задач
@mcp.command("get_tasks")
async def get_tasks(status: Optional[str] = None):
    """Получить список задач по статусу"""

# Анализ задачи
@mcp.command("analyze_task")
async def analyze_task(task_id: int):
    """Запустить анализ задачи"""

# Обновление статуса
@mcp.command("update_task_status")
async def update_task_status(task_id: int, status: str):
    """Обновить статус задачи"""

# Создание worktree
@mcp.command("create_worktree")
async def create_worktree(task_id: int):
    """Создать worktree для задачи"""
```

## ✅ Checklist для Claude (Main Flow)

### Перед началом задачи:
- [ ] Получил задачу через MCP
- [ ] Проанализировал требования
- [ ] Определил затрагиваемые файлы
- [ ] Создал worktree для задачи
- [ ] Выбрал подходящих субагентов

### Во время выполнения:
- [ ] Делегировал субагентам с контекстом
- [ ] Отслеживаю прогресс через MCP
- [ ] Обновляю статусы в UI

### После выполнения:
- [ ] Запустил тестирование
- [ ] Провел code review
- [ ] Создал PR
- [ ] Выполнил merge
- [ ] Очистил worktree
- [ ] Обновил статус на Done

## 🚫 Запрещено

- ❌ Main Flow НЕ меняет код напрямую
- ❌ Субагенты НЕ работают вне worktrees
- ❌ Merge БЕЗ тестирования и review
- ❌ Работа в main branch напрямую
- ❌ Более 3-х параллельных задач
- ❌ Смешивание несвязанных изменений

## 🔑 Ключевые отличия от AI Tasks

1. **UI-driven workflow** - задачи создаются в веб-интерфейсе
2. **MCP интеграция** - все коммуникации через протокол
3. **Автоматические статусы** - обновление в реальном времени
4. **SQLite вместо файлов** - задачи хранятся в БД
5. **Docker deployment** - все компоненты в контейнерах
6. **Универсальность** - поддержка любых технологий