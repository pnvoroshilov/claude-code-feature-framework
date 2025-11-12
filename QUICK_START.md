# 🚀 ClaudeTask Framework - Quick Start

Фреймворк для управления задачами с интеграцией Claude Code.

## ⚡ Быстрая установка

### Вариант 1: Одна команда (если уже клонирован репозиторий)

```bash
chmod +x install.sh && ./install.sh
```

### Вариант 2: Установка из GitHub

```bash
# Клонировать репозиторий
git clone https://github.com/pnvoroshilov/claude-code-feature-framework.git
cd claude-code-feature-framework

# Запустить установку
chmod +x install.sh && ./install.sh
```

## 📋 Системные требования

- **Python** 3.10+ (рекомендуется 3.11)
- **Node.js** 18+
- **npm** 9+
- **Git**

### Установка зависимостей

**macOS:**
```bash
brew install python@3.11 node git
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv nodejs npm git
```

**Windows:**
```bash
# Используйте WSL2 и следуйте инструкциям для Ubuntu
```

## 🎯 Использование

### Запуск всех сервисов

```bash
./start.sh
```

Это запустит:
- 📊 **Frontend**: http://localhost:3334
- 🔌 **Backend API**: http://localhost:3333
- 🔧 **MCP Server**: http://localhost:8000

### Остановка всех сервисов

```bash
./stop.sh
```

### Просмотр логов

```bash
# Backend
tail -f logs/backend.log

# Frontend
tail -f logs/frontend.log

# MCP Server
tail -f logs/mcp.log
```

## 📁 Структура проекта

```
claude-code-feature-framework/
├── install.sh           # Установочный скрипт
├── start.sh             # Запуск всех сервисов
├── stop.sh              # Остановка всех сервисов
├── logs/                # Логи всех сервисов
├── claudetask/
│   ├── backend/         # FastAPI backend
│   │   ├── app/         # Приложение
│   │   ├── data/        # SQLite база данных
│   │   └── venv/        # Python virtual environment
│   ├── frontend/        # React frontend
│   │   └── src/         # Исходный код
│   └── mcp_server/      # MCP сервер
└── docs/                # Документация
```

## 🎨 Возможности

### ✨ Основные функции

- **📋 Task Board** - Канбан-доска для управления задачами
- **🔧 Skills Management** - Управление навыками Claude
- **🔌 MCP Configs** - Конфигурация MCP серверов
- **🤖 Subagents** - Управление подагентами
- **📝 Project Instructions** - Кастомные инструкции для проектов
- **💻 Claude Sessions** - Отслеживание сессий Claude

### 🔥 Новые возможности

- **Custom Instructions** - Добавление проектных инструкций для Claude
- **MCP Search** - Поиск MCP серверов на mcp.so
- **Auto CLAUDE.md** - Автоматическая генерация конфигурации

## 🛠️ Конфигурация

### Backend (.env)

```env
DATABASE_URL=sqlite+aiosqlite:///./data/claudetask.db
API_PORT=3333
CORS_ORIGINS=http://localhost:3334
```

### Frontend (.env)

```env
REACT_APP_API_URL=http://localhost:3333
PORT=3334
```

## 📖 Документация

- [README.md](README.md) - Полная документация
- [IMPLEMENTATION_QUICK_START.md](IMPLEMENTATION_QUICK_START.md) - Гайд по имплементации
- [SKILLS_AND_MCP_ARCHITECTURE.md](SKILLS_AND_MCP_ARCHITECTURE.md) - Архитектура
- [API Documentation](http://localhost:3333/docs) - Swagger API docs (после запуска)

## 🐛 Устранение неполадок

### Порты уже заняты

```bash
# Освободить порты
./stop.sh

# Или вручную
lsof -ti:3333 | xargs kill -9  # Backend
lsof -ti:3334 | xargs kill -9  # Frontend
lsof -ti:8000 | xargs kill -9  # MCP
```

### Ошибки установки Python пакетов

```bash
cd claudetask/backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Ошибки установки npm пакетов

```bash
cd claudetask/frontend
rm -rf node_modules package-lock.json
npm install
```

### База данных не создается

```bash
cd claudetask/backend
source venv/bin/activate
python migrations/migrate_add_custom_instructions.py
```

## 🔄 Обновление

```bash
git pull origin main
./install.sh  # Переустановит зависимости
./start.sh    # Запустит обновленную версию
```

## 🤝 Поддержка

- **GitHub Issues**: Создайте issue для багов и предложений
- **Документация**: Смотрите полную документацию в `/docs`
- **Примеры**: Изучайте примеры в репозитории

## 📝 Лицензия

MIT License

---

**Разработано с ❤️ для упрощения работы с Claude Code**
