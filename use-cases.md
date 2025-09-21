# ClaudeTask Framework - Детальные Use Cases

## Участники системы
- **User** - Разработчик, использующий фреймворк
- **Claude Code** - AI ассистент для разработки
- **ClaudeTask UI** - Веб-интерфейс фреймворка
- **Backend API** - Сервер фреймворка
- **MCP Server** - Сервер протокола для Claude
- **Project** - Локальная папка с кодом пользователя

---

## Use Case 1: Первичная установка и инициализация проекта

### Участники: User, ClaudeTask UI, Backend API, Project, Claude Code

### Пошаговый сценарий:

#### Этап 1: Установка фреймворка
1. **User** клонирует репозиторий ClaudeTask
2. **User** запускает `docker-compose up -d`
3. **Docker** поднимает три контейнера:
   - Frontend (port 3000)
   - Backend API (port 8000)
   - MCP Server (port 3333)
4. **User** открывает браузер на http://localhost:3000

#### Этап 2: Инициализация проекта
1. **User** в UI нажимает "Initialize New Project"
2. **ClaudeTask UI** показывает форму инициализации
3. **User** вводит путь к проекту: `/Users/john/my-app`
4. **User** вводит название: "My App"
5. **User** нажимает "Initialize"

6. **ClaudeTask UI** → **Backend API**: POST /api/project/initialize
   ```json
   {
     "project_path": "/Users/john/my-app",
     "project_name": "My App"
   }
   ```

7. **Backend API** выполняет:
   - Проверяет существование папки
   - Определяет используемые технологии в проекте
   - Создает UUID проекта: `abc-123-def`
   - Создает в БД запись о проекте

8. **Backend API** создает файлы в **Project**:
   ```
   /Users/john/my-app/
   ├── .mcp.json                        # MCP конфигурация для Claude Code
   ├── .claudetask/
   │   ├── CLAUDE.md (кастомизированный для проекта)
   │   ├── agents/
   │   │   ├── task-analyzer.md
   │   │   ├── feature-developer.md
   │   │   └── ...
   │   └── project.json
   └── worktrees/ (пустая папка)
   ```

9. **Backend API** → **ClaudeTask UI**: Возвращает результат
   ```json
   {
     "project_id": "abc-123-def",
     "mcp_config": "{ mcpServers: { claudetask: {...} } }",
     "files_created": [".claudetask/CLAUDE.md", ...]
   }
   ```

10. **ClaudeTask UI** показывает **User**:
    - ✅ Проект инициализирован
    - ✅ Файлы созданы в проекте
    - Список созданных файлов

#### Этап 3: Автоматическая настройка MCP и запуск Claude Code

1. **Backend API** автоматически создает MCP конфигурацию:
   - Создает файл `.mcp.json` в корне проекта `/Users/john/my-app/.mcp.json`
   - Записывает конфигурацию для ClaudeTask:
     ```json
     {
       "mcpServers": {
         "claudetask": {
           "command": "python",
           "args": [
             "-m",
             "claudetask_mcp_bridge",
             "--project-id", "abc-123-def",
             "--project-path", "/Users/john/my-app",
             "--server", "http://localhost:3333"
           ]
         }
       }
     }
     ```
   - Если файл `.mcp.json` уже существует - добавляет секцию claudetask с сохранением остальных настроек

2. **ClaudeTask UI** показывает **User**:
   ```
   ✅ Проект инициализирован
   ✅ MCP конфигурация создана в .mcp.json
   ⚠️  Требуется перезапустить Claude Code для применения настроек
   ```

3. **User** перезапускает Claude Code:
   ```bash
   # Закрыть текущую сессию Claude Code (если открыта)
   # Запустить заново в папке проекта
   claude-code /Users/john/my-app
   ```

4. **Claude Code** при запуске:
   - Автоматически обнаруживает `.mcp.json` в папке проекта
   - Загружает MCP конфигурацию из `.mcp.json`
   - Запускает MCP клиент для "claudetask"
   - Читает `.claudetask/CLAUDE.md` из проекта
   - Загружает агентов из `.claudetask/agents/`
   - Подключается к MCP Server через bridge
   - Готов к работе

5. **Claude Code** автоматически проверяет подключение:
   ```
   Claude: Обнаружен проект ClaudeTask.
           Подключение к фреймворку... ✅
           Проект: My App
           Задач в бэклоге: 0
           Готов к работе!
   ```

---

## Use Case 2: Создание и автоматическое выполнение Feature задачи

### Участники: User, ClaudeTask UI, Backend API, Claude Code, MCP Server, Project

### Пошаговый сценарий:

#### Этап 1: Создание задачи
1. **User** открывает http://localhost:3000
2. **User** нажимает "Create Task"
3. **User** заполняет форму:
   - Title: "Add dark mode toggle"
   - Description: "Add a toggle button in header to switch between light and dark themes"
   - Type: Feature
   - Priority: High
4. **User** нажимает "Create"

5. **ClaudeTask UI** → **Backend API**: POST /api/tasks
   ```json
   {
     "title": "Add dark mode toggle",
     "description": "Add a toggle button...",
     "type": "Feature",
     "priority": "High",
     "status": "Backlog"
   }
   ```

6. **Backend API**:
   - Создает задачу с ID: 1
   - Сохраняет в БД
   - Возвращает созданную задачу

7. **ClaudeTask UI** отображает задачу в колонке "Backlog"

#### Этап 2: Автоматический триггер для Claude

##### Вариант А: Push-уведомление через MCP
1. **Backend API** обнаруживает новую задачу с высоким приоритетом
2. **Backend API** → **MCP Server**: отправляет push-уведомление
3. **MCP Server** → **Claude Code**: триггерит команду `check_new_tasks`
4. **Claude Code** автоматически выводит:
   ```
   🔔 Новая задача с высоким приоритетом доступна!
   Задача #1: "Add dark mode toggle"
   Начать работу? (да/нет)
   ```

##### Вариант Б: Периодический polling
1. **Claude Code** через MCP каждые N минут проверяет новые задачи
2. При обнаружении задач с приоритетом High - уведомляет пользователя

##### Вариант В: Ручной запрос пользователя
1. **User** в Claude Code: "Возьми следующую задачу из бэклога"
2. **Claude Code** → **MCP Server**: вызывает `get_next_task()`

#### Этап 3: Claude берет задачу в работу

1. **User** подтверждает: "да" (или Claude автоматически берет при автоматическом режиме)

2. **Claude Code** → **MCP Server**: вызывает `get_next_task()`

3. **MCP Server** → **Backend API**: GET /api/tasks/next

4. **Backend API**:
   - Находит задачу #1 (высокий приоритет)
   - Меняет статус на "Analysis"
   - Возвращает задачу

5. **MCP Server** → **Claude Code**: возвращает задачу #1

6. **Claude Code** выводит **User**:
   ```
   Беру задачу #1 "Add dark mode toggle" с высоким приоритетом.
   Начинаю анализ требований...
   ```

#### Этап 4: Анализ задачи
1. **Claude Code** анализирует проект:
   - Читает структуру проекта
   - Находит файлы связанные с UI/header
   - Находит файлы стилей и темы
   - Определяет точки интеграции

2. **Claude Code** → **MCP Server**: вызывает `save_task_analysis()`
   ```json
   {
     "task_id": 1,
     "analysis": {
       "affected_files": [
         "components/Header",
         "contexts/ThemeContext",
         "styles/theme"
       ],
       "complexity": "Medium",
       "risks": ["Необходимо проверить совместимость с текущими стилями"],
       "implementation_plan": "1. Создать контекст для темы\n2. Добавить переключатель в header\n3..."
     }
   }
   ```

3. **MCP Server** → **Backend API**: PUT /api/tasks/1/analysis

4. **Backend API**:
   - Сохраняет анализ
   - Меняет статус на "Ready"

5. **ClaudeTask UI** автоматически обновляет доску (websocket или polling)

6. **Claude Code** выводит **User**:
   ```
   Анализ завершен. Задача готова к реализации.
   Затронутые файлы: Header, ThemeContext, theme
   Сложность: Средняя
   Начинаю разработку...
   ```

#### Этап 5: Разработка
1. **Claude Code** → **MCP Server**: `create_worktree(task_id: 1)`

2. **MCP Server** выполняет в **Project**:
   ```bash
   cd /Users/john/my-app
   git worktree add -b feature/task-1-dark-mode ./worktrees/task-1
   ```

3. **Claude Code** → **MCP Server**: `update_task_status(1, "In Progress")`

4. **Backend API** обновляет статус → **ClaudeTask UI** показывает в колонке "In Progress"

5. **Claude Code** работает в worktree:
   ```bash
   cd /Users/john/my-app/worktrees/task-1
   ```

6. **Claude Code** создает/обновляет файлы:
   - Создает контекст для управления темой
   - Добавляет состояние темы (светлая/темная)
   - Обновляет компонент header с кнопкой переключения
   - Добавляет логику переключения темы
   - Обновляет стили для поддержки обеих тем

7. **Claude Code** коммитит изменения:
   ```bash
   git add .
   git commit -m "feat: implement dark mode toggle (task #1)"
   ```

#### Этап 6: Тестирование
1. **Claude Code** → **MCP Server**: `update_task_status(1, "Testing")`

2. **Claude Code** запускает тесты проекта (определяет команду автоматически)

3. **Claude Code** добавляет/обновляет тесты:
   - Тест для переключения темы
   - Тест для сохранения состояния
   - Тест для корректного отображения

4. Тесты проходят успешно

5. **Claude Code** выводит **User**:
   ```
   ✅ Все тесты прошли успешно
   Переходу к код-ревью...
   ```

#### Этап 7: Code Review и Merge
1. **Claude Code** → **MCP Server**: `update_task_status(1, "Code Review")`

2. **Claude Code** создает PR:
   ```bash
   gh pr create --title "feat: Add dark mode toggle (#1)" \
                --body "Implements dark mode toggle in header"
   ```

3. **Claude Code** проводит self-review:
   - Проверяет код на соответствие стандартам
   - Проверяет покрытие тестами
   - Проверяет отсутствие console.log

4. **Claude Code** мержит PR:
   ```bash
   git checkout main
   git merge feature/task-1-dark-mode
   git push origin main
   ```

5. **Claude Code** очищает worktree:
   ```bash
   git worktree remove ./worktrees/task-1
   ```

6. **Claude Code** → **MCP Server**: `update_task_status(1, "Done")`

7. **ClaudeTask UI** перемещает задачу в "Done"

8. **Claude Code** выводит **User**:
   ```
   ✅ Задача #1 "Add dark mode toggle" успешно завершена!
   - Создан контекст для управления темой
   - Добавлена кнопка переключения в header
   - Написаны тесты
   - Код смержен в main
   ```

---

## Use Case 3: Исправление бага с высоким приоритетом

### Участники: User, ClaudeTask UI, Claude Code, MCP Server

### Пошаговый сценарий:

#### Этап 1: Создание баг-репорта
1. **User** в UI создает задачу:
   - Title: "Fix login button not working"
   - Description: "Login button doesn't respond to clicks"
   - Type: Bug
   - Priority: High

2. Задача создается со статусом "Backlog"

#### Этап 2: Claude автоматически берет баг
1. **User**: "Проверь, есть ли критичные баги"

2. **Claude Code** → **MCP Server**: `get_next_task(type="Bug", priority="High")`

3. **Claude Code** получает задачу #2 и начинает анализ

4. **Claude Code** находит проблему:
   - Анализирует код кнопки входа
   - Обнаруживает ошибку в обработчике события
   - Определяет корректное решение

5. **Claude Code** создает bugfix ветку:
   ```bash
   git worktree add -b bugfix/task-2-login ./worktrees/task-2
   ```

6. **Claude Code** исправляет баг и добавляет регрессионный тест для проверки что кнопка работает корректно

7. **Claude Code** коммитит, тестирует, создает PR и мержит

8. **Claude Code** выводит **User**:
   ```
   🐛 Баг #2 исправлен!
   Проблема: ошибка в обработчике события кнопки
   Решение: исправлен обработчик
   Добавлен регрессионный тест
   ```

---

## Use Case 4: Пакетный анализ задач

### Участники: User, Claude Code, MCP Server, Backend API

### Пошаговый сценарий:

1. **User** создает в UI несколько задач в Backlog

2. **User** в Claude: "Проанализируй все задачи в бэклоге"

3. **Claude Code** → **MCP Server**: `get_backlog_tasks()`

4. **Claude Code** получает список из 5 задач

5. **Claude Code** для каждой задачи:
   - Анализирует требования
   - Определяет затрагиваемые файлы
   - Оценивает сложность
   - Сохраняет анализ через MCP

6. **Claude Code** выводит сводку:
   ```
   Проанализировано 5 задач:
   - #3 "Add user profile page" - Сложность: High, 8 файлов
   - #4 "Fix typo in footer" - Сложность: Low, 1 файл
   - #5 "Add API caching" - Сложность: Medium, 4 файла
   - #6 "Update dependencies" - Сложность: Low, 2 файла
   - #7 "Add unit tests" - Сложность: Medium, 10 файлов
   
   Все задачи готовы к разработке (статус: Ready)
   ```

7. **ClaudeTask UI** показывает все задачи в колонке "Ready" с анализом

---

## Use Case 5: Переключение между проектами

### Участники: User, ClaudeTask UI, Backend API, Claude Code

### Пошаговый сценарий:

1. **User** имеет два инициализированных проекта:
   - Project A: /Users/john/project-a
   - Project B: /Users/john/project-b

2. **User** в UI выбирает "Switch Project" → "Project B"

3. **ClaudeTask UI** → **Backend API**: PUT /api/project/switch
   ```json
   { "project_id": "project-b-uuid" }
   ```

4. **Backend API**:
   - Устанавливает Project B как активный
   - Возвращает конфигурацию Project B

5. **ClaudeTask UI** обновляет:
   - Показывает задачи Project B
   - Обновляет настройки

6. **User** перезапускает Claude Code:
   ```bash
   claude-code /Users/john/project-b
   ```

7. **Claude Code**:
   - Читает `/Users/john/project-b/.claudetask/CLAUDE.md`
   - Подключается к MCP с контекстом Project B
   - Готов работать с задачами Project B

8. **User**: "Что в бэклоге?"

9. **Claude Code** → **MCP Server**: `get_backlog_tasks()`

10. **Claude Code** выводит:
    ```
    Текущий проект: Project B
    Задачи в бэклоге:
    - #10 "Setup CI/CD pipeline" (High)
    - #11 "Add logging system" (Medium)
    ```

---

## Use Case 6: Ручное управление статусами

### Участники: User, ClaudeTask UI, Backend API, Claude Code

### Пошаговый сценарий:

1. **User** видит задачу #8 в статусе "Testing"

2. **User** считает, что нужно вернуть на доработку

3. **User** перетаскивает задачу в колонку "In Progress"

4. **ClaudeTask UI** → **Backend API**: PUT /api/tasks/8/status
   ```json
   { "status": "In Progress" }
   ```

5. **Backend API** обновляет статус

6. При следующем запросе **Claude Code** видит обновленный статус:
   ```
   User: "Какой статус у задачи 8?"
   Claude: "Задача #8 находится в статусе 'In Progress'. 
           Похоже, она была возвращена на доработку из Testing."
   ```

---

## Use Case 7: Работа без активного Claude

### Участники: User, ClaudeTask UI, Backend API

### Пошаговый сценарий:

1. **User** работает только через UI (Claude Code не запущен)

2. **User** создает задачи, организует бэклог

3. **User** вручную перемещает задачи между статусами

4. **User** может:
   - Просматривать анализ от Claude (если был сделан ранее)
   - Редактировать описания задач
   - Устанавливать приоритеты
   - Просматривать историю

5. Позже **User** запускает Claude Code

6. **Claude Code** сразу видит актуальное состояние:
   ```
   User: "Что нужно сделать?"
   Claude: "В бэклоге 3 новые задачи без анализа. 
           2 задачи в Ready ждут реализации.
           Начать с анализа новых задач?"
   ```

---

## Use Case 8: Автоматический режим работы

### Участники: User, ClaudeTask UI, Backend API, Claude Code, MCP Server

### Пошаговый сценарий:

#### Этап 1: Включение автоматического режима
1. **User** в Claude: "Включи автоматический режим для критических задач"

2. **Claude Code** → **MCP Server**: `enable_auto_mode(priority="High")`

3. **MCP Server** сохраняет настройки и начинает мониторинг

4. **Claude Code** выводит:
   ```
   ✅ Автоматический режим активирован
   Буду автоматически выполнять задачи с приоритетом High
   Проверка новых задач каждые 5 минут
   ```

#### Этап 2: Автоматическая обработка новой задачи
1. **User** создает в UI критический баг:
   - Title: "Payment system is down"
   - Type: Bug
   - Priority: High

2. **Backend API** сохраняет задачу и триггерит уведомление

3. **Backend API** → **MCP Server**: push-уведомление
   ```json
   {
     "type": "new_high_priority_task",
     "task_id": 15,
     "title": "Payment system is down",
     "auto_start": true
   }
   ```

4. **MCP Server** → **Claude Code**: триггер автоматического старта

5. **Claude Code** автоматически (без запроса пользователя):
   ```
   🔴 КРИТИЧЕСКАЯ ЗАДАЧА ОБНАРУЖЕНА
   Автоматически беру в работу: #15 "Payment system is down"
   
   [10:30] Начинаю анализ...
   [10:31] Проблема найдена в payment_processor
   [10:32] Создаю worktree bugfix/task-15
   [10:35] Исправление применено
   [10:36] Запускаю тесты...
   [10:38] ✅ Тесты прошли
   [10:39] Создаю PR для срочного мержа
   [10:40] ✅ Задача #15 завершена за 10 минут
   ```

#### Этап 3: Пакетная обработка в автоматическом режиме
1. **Claude Code** в автоматическом режиме проверяет очередь

2. **Claude Code** → **MCP Server**: `get_task_queue()`

3. **MCP Server** возвращает список из 3 задач

4. **Claude Code** последовательно обрабатывает:
   ```
   📋 Очередь задач: 3
   
   [11:00] Задача #16 - Начата
   [11:20] Задача #16 - Завершена ✅
   
   [11:21] Задача #17 - Начата
   [11:45] Задача #17 - Завершена ✅
   
   [11:46] Задача #18 - Начата
   [12:10] Задача #18 - Требуется ручное вмешательство ⚠️
           Причина: Неоднозначные требования
   
   Автоматический режим приостановлен.
   Обработано задач: 2/3
   ```

#### Этап 4: Остановка при проблеме
1. **Claude Code** сталкивается с проблемой при выполнении задачи #19

2. **Claude Code** обнаруживает что тесты не проходят после 3 попыток

3. **Claude Code** → **MCP Server**: `pause_auto_mode("test_failure")`

4. **Claude Code** выводит **User**:
   ```
   ⚠️ Автоматический режим приостановлен
   
   Причина: Тесты не проходят для задачи #19
   Ошибка: payment_test.py::test_refund FAILED
   
   Требуется ваше вмешательство.
   Варианты:
   1. Исследовать проблему вручную
   2. Пропустить задачу
   3. Откатить изменения и продолжить
   ```

5. **User**: "Пропусти эту задачу и продолжай"

6. **Claude Code**:
   - Откатывает изменения задачи #19
   - Меняет статус задачи на "Blocked"
   - Продолжает автоматический режим с следующей задачи

---

## Use Case 9: Конфликт при мерже

### Участники: Claude Code, MCP Server, User

### Пошаговый сценарий:

1. **Claude Code** завершает задачу #9 и пытается смержить

2. Git показывает конфликт:
   ```
   CONFLICT (content): Merge conflict in main application file
   ```

3. **Claude Code** → **MCP Server**: `report_merge_conflict(task_id: 9)`

4. **Claude Code** выводит **User**:
   ```
   ⚠️ Обнаружен конфликт при мерже задачи #9
   Файл с конфликтом: main application file
   
   Варианты действий:
   1. Я могу попытаться разрешить конфликт автоматически
   2. Вы можете разрешить конфликт вручную
   3. Отложить мерж и продолжить с другой задачей
   
   Что выбираете?
   ```

5. **User**: "Попробуй разрешить автоматически"

6. **Claude Code**:
   - Анализирует конфликт
   - Определяет правильное решение
   - Разрешает конфликт
   - Создает коммит
   - Завершает мерж

7. **Claude Code** → **MCP Server**: `update_task_status(9, "Done")`

---

## Диаграмма взаимодействия компонентов

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    User     │────▶│ ClaudeTask  │────▶│  Backend    │
│             │     │     UI      │     │    API      │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                         │
       │                                         │
       ▼                                         ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│Claude Code  │────▶│ MCP Server  │────▶│  Database   │
│             │     │             │     │  (SQLite)   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                         
       │                                         
       ▼                                         
┌─────────────┐                                 
│   Project   │                                 
│   Folder    │                                 
└─────────────┘                                 
```

## Ключевые принципы взаимодействия

1. **UI-driven**: Пользователь управляет задачами через веб-интерфейс
2. **Claude-automated**: Claude автоматизирует выполнение задач
3. **MCP-connected**: Вся коммуникация Claude с фреймворком через MCP
4. **Git-isolated**: Каждая задача разрабатывается в изолированном worktree
5. **Status-tracked**: Статусы задач обновляются в реальном времени
6. **Project-scoped**: Все операции ограничены текущим проектом