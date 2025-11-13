# 🎨 Claude Code Sessions - Frontend Integration

## ✅ Готово

### Созданные компоненты:

1. **`ClaudeCodeSessions.tsx`** - Новая страница для отображения сессий из `~/.claude/projects/`
   - Выбор проекта
   - Список сессий с фильтрацией и поиском
   - Детальная информация о сессии
   - Статистика использования

2. **Обновленные файлы**:
   - ✅ `App.tsx` - Добавлен роут `/claude-code-sessions`
   - ✅ `Sidebar.tsx` - Добавлен пункт меню "Claude Code Sessions"

## 🚀 Запуск

### 1. Backend (уже запущен)
```bash
cd claudetask/backend
python -m uvicorn app.main:app --reload --port 3333
```

### 2. Frontend
```bash
cd claudetask/frontend
npm start
```

Откроется на http://localhost:3000

### 3. Перейти к Claude Code Sessions
- В боковом меню нажмите **"Claude Code Sessions"** 📜
- Или откройте напрямую: http://localhost:3000/claude-code-sessions

## 📋 Функционал

### Главная страница
- 📊 **Статистика**: Общее количество сессий, сообщений, файлов, ошибок
- 📂 **Выбор проекта**: Dropdown с выбором проекта из `~/.claude/projects/`
- 🔍 **Поиск**: Поиск по содержимому сессий
- 📈 **Tool Usage**: Статистика использования инструментов (Accordion)

### Таблица сессий
Показывает для каждой сессии:
- **Session ID** - Первые 12 символов UUID
- **Branch** - Git ветка
- **Messages** - Количество сообщений (↑user ↓assistant)
- **Tools** - Количество использованных инструментов
- **Files** - Количество измененных файлов
- **Errors** - Количество ошибок (если есть)
- **Created** - Дата создания
- **Actions** - Кнопка "View Details"

### Детали сессии (Dialog)

**4 вкладки:**

1. **Overview** 📋
   - Working Directory
   - Git Branch
   - Claude Version
   - File Size
   - Commands Used
   - Modified Files

2. **Messages** 💬
   - История всех сообщений (user ↔ assistant)
   - Временные метки
   - Превью содержимого

3. **Tools** 🔧
   - Список всех использованных инструментов
   - Количество вызовов каждого

4. **Timeline** ⏱️
   - Список ошибок с временными метками
   - Полное содержимое ошибок

## 🎨 UI Features

### Responsive Design
- ✅ Адаптивная сетка (Grid)
- ✅ Мобильная версия
- ✅ Pagination для больших списков

### Material-UI Components
- Cards для статистики
- Chips для статусов и меток
- Accordions для Tool Usage
- Dialog для деталей
- TablePagination

### Цветовая схема
- Primary: Инструменты, чипы
- Error: Ошибки
- Success: Успешные операции

## 📊 API Endpoints используемые

```typescript
// Все проекты
GET /api/claude-sessions/projects

// Сессии проекта
GET /api/claude-sessions/projects/{name}/sessions

// Детали сессии
GET /api/claude-sessions/sessions/{id}
  ?project_name=Framework
  &include_messages=true

// Поиск
GET /api/claude-sessions/sessions/search
  ?query=error
  &project_name=Framework

// Статистика
GET /api/claude-sessions/statistics
  ?project_name=Framework
```

## 🔄 Отличия от ClaudeSessions.tsx

| Feature | ClaudeSessions (старый) | ClaudeCodeSessions (новый) |
|---------|-------------------------|----------------------------|
| **Источник данных** | База данных ClaudeTask | `~/.claude/projects/` JSONL |
| **Управление** | Start/Pause/Resume/Stop | Read-only просмотр |
| **Real-time** | WebSocket обновления | Refresh по запросу |
| **История** | Только активные сессии | Вся история сессий |
| **Поиск** | Нет | Полнотекстовый поиск |
| **Статистика** | Базовая | Детальная с tool usage |

## 🎯 Use Cases

### 1. Анализ продуктивности
- Сколько сессий работало над проектом
- Сколько сообщений было отправлено
- Какие инструменты чаще всего используются

### 2. Поиск решений
- Найти сессии с похожими ошибками
- Посмотреть, как решалась похожая задача
- Изучить историю изменений файлов

### 3. Отладка
- Просмотр ошибок в прошлых сессиях
- Анализ паттернов ошибок
- Поиск проблемных мест

### 4. Learning
- Изучить, какие команды использовались
- Посмотреть эффективные workflow
- Найти best practices

## 📸 Скриншоты (будут в UI)

### Main View
```
┌────────────────────────────────────────────────┐
│ Claude Code Sessions               [Refresh]   │
├────────────────────────────────────────────────┤
│ 📂 Reading from ~/.claude/projects/            │
├────────────────────────────────────────────────┤
│ Project: [Framework ▼]    [Search: _______]   │
├────────────────────────────────────────────────┤
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐          │
│ │  59  │ │10662 │ │  0   │ │  24  │          │
│ │Total │ │Msgs  │ │Files │ │Errors│          │
│ └──────┘ └──────┘ └──────┘ └──────┘          │
├────────────────────────────────────────────────┤
│ [▼] Tool Usage Statistics                      │
├────────────────────────────────────────────────┤
│ Session ID   Branch  Messages  Tools  Errors  │
│ cb6e8208...  main    55        5      0       │
│ 0d18e9a8...  main    1043      8      3       │
└────────────────────────────────────────────────┘
```

## 🐛 Troubleshooting

### "No sessions available"
- Проверьте, что существует `~/.claude/projects/`
- Убедитесь, что есть JSONL файлы в директориях проектов

### Backend errors
- Проверьте, что backend запущен на порту 3333
- Проверьте логи: `/tmp/claudetask_backend.log`

### CORS errors
- Backend должен быть на localhost:3333
- Frontend на localhost:3000
- CORS уже настроен в `main.py`

## ✅ Checklist

- [x] Backend API работает
- [x] Frontend компонент создан
- [x] Роут добавлен
- [x] Sidebar обновлен
- [x] Тестирование API
- [ ] Запустить frontend
- [ ] Проверить UI
- [ ] Протестировать все функции

## 🎉 Готово к использованию!

Теперь можно:
1. Запустить frontend: `cd claudetask/frontend && npm start`
2. Открыть http://localhost:3000/claude-code-sessions
3. Выбрать проект из dropdown
4. Просмотреть все сессии Claude Code!

---

**Created:** 2025-11-13
**Status:** ✅ Ready for Testing
