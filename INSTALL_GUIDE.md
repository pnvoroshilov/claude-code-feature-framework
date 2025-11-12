# 📦 Руководство по установке ClaudeTask Framework

## 🎯 Варианты установки

### 🚀 Вариант 1: Быстрая установка одной командой

Если репозиторий уже клонирован:

```bash
cd claude-code-feature-framework
chmod +x install.sh && ./install.sh
```

### 📥 Вариант 2: Установка с нуля из GitHub

```bash
# Клонировать и установить
git clone https://github.com/YOUR_USERNAME/claude-code-feature-framework.git
cd claude-code-feature-framework
chmod +x install.sh && ./install.sh
```

### ⚡ Вариант 3: Одна команда с автоклонированием

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/claude-code-feature-framework/main/quick-install.sh | bash
```

## 🔧 Что делает установщик

`install.sh` автоматически:

1. ✅ Проверяет системные требования (Python 3.10+, Node.js 18+, npm)
2. ✅ Устанавливает backend зависимости (FastAPI, SQLAlchemy, и др.)
3. ✅ Устанавливает MCP server зависимости
4. ✅ Устанавливает frontend зависимости (React, Material-UI)
5. ✅ Создает виртуальные окружения Python
6. ✅ Выполняет миграции базы данных
7. ✅ Создает конфигурационные файлы (.env)
8. ✅ Создает скрипты запуска (`start.sh`, `stop.sh`)
9. ✅ Создает директорию для логов

## 📋 Системные требования

### Обязательно:
- **Python** 3.10 или выше (рекомендуется 3.11)
- **Node.js** 18 или выше
- **npm** 9 или выше
- **Git**

### Установка зависимостей по платформам:

#### macOS
```bash
# Установка через Homebrew
brew install python@3.11 node git

# Проверка версий
python3 --version  # должно быть >= 3.10
node --version     # должно быть >= v18
npm --version      # должно быть >= 9
```

#### Ubuntu/Debian
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка зависимостей
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm git

# Если нужна более новая версия Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Проверка версий
python3.11 --version
node --version
npm --version
```

#### Windows (через WSL2)
```bash
# Установите WSL2
wsl --install

# В WSL терминале:
sudo apt update
sudo apt install python3.11 python3.11-venv nodejs npm git
```

## 📦 Структура установки

После установки структура будет выглядеть так:

```
claude-code-feature-framework/
├── install.sh              # Установочный скрипт ✓
├── start.sh                # Запуск всех сервисов (создается установщиком)
├── stop.sh                 # Остановка сервисов (создается установщиком)
├── logs/                   # Логи (создается установщиком)
│   ├── backend.log
│   ├── frontend.log
│   └── mcp.log
├── claudetask/
│   ├── backend/
│   │   ├── venv/           # Python virtual environment (создается)
│   │   ├── data/           # SQLite database (создается)
│   │   │   └── claudetask.db
│   │   └── .env            # Backend config (создается)
│   ├── frontend/
│   │   ├── node_modules/   # npm packages (создается)
│   │   └── .env            # Frontend config (создается)
│   └── mcp_server/
│       └── venv/           # MCP Python environment (создается)
```

## 🎯 Запуск после установки

### 1. Запустить все сервисы:
```bash
./start.sh
```

Это запустит:
- 📊 Frontend: http://localhost:3334
- 🔌 Backend: http://localhost:3333  
- 🔧 MCP Server: http://localhost:8000

### 2. Открыть в браузере:
```bash
open http://localhost:3334
# или
xdg-open http://localhost:3334  # Linux
```

### 3. Остановить все сервисы:
```bash
./stop.sh
```

## 📝 Логи

Все логи сохраняются в директории `logs/`:

```bash
# Просмотр логов в реальном времени
tail -f logs/backend.log   # Backend API
tail -f logs/frontend.log  # React frontend
tail -f logs/mcp.log       # MCP server

# Просмотр всех логов
tail -f logs/*.log
```

## 🔍 Проверка установки

### Backend API:
```bash
curl http://localhost:3333/health
# Ожидается: {"status":"healthy","service":"claudetask-backend"}
```

### Frontend:
```bash
curl http://localhost:3334
# Ожидается: HTML страница React приложения
```

### Database:
```bash
ls -lh claudetask/backend/data/claudetask.db
# Должен существовать файл базы данных
```

## ⚙️ Конфигурация

### Backend (.env)
Файл создается автоматически: `claudetask/backend/.env`

```env
DATABASE_URL=sqlite+aiosqlite:///./data/claudetask.db
SYNC_DATABASE_URL=sqlite:///./data/claudetask.db
API_HOST=0.0.0.0
API_PORT=3333
CORS_ORIGINS=http://localhost:3334,http://127.0.0.1:3334
ENVIRONMENT=development
```

### Frontend (.env)
Файл создается автоматически: `claudetask/frontend/.env`

```env
REACT_APP_API_URL=http://localhost:3333
PORT=3334
```

## 🐛 Устранение неполадок

### Проблема: Порты уже заняты

```bash
# Остановить все сервисы
./stop.sh

# Или освободить порты вручную
lsof -ti:3333 | xargs kill -9  # Backend
lsof -ti:3334 | xargs kill -9  # Frontend
lsof -ti:8000 | xargs kill -9  # MCP
```

### Проблема: Ошибки при установке Python пакетов

```bash
# Очистить и переустановить backend
cd claudetask/backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ../..
```

### Проблема: Ошибки при установке npm пакетов

```bash
# Очистить и переустановить frontend
cd claudetask/frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
cd ../..
```

### Проблема: База данных не создается

```bash
# Создать базу данных вручную
cd claudetask/backend
source venv/bin/activate
python migrations/migrate_add_custom_instructions.py
deactivate
cd ../..
```

### Проблема: MCP Server не запускается

```bash
# Переустановить MCP server
cd claudetask/mcp_server
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -e .
deactivate
cd ../..
```

## 🔄 Переустановка

Если нужно переустановить с нуля:

```bash
# Остановить сервисы
./stop.sh

# Удалить установленные компоненты
rm -rf claudetask/backend/venv
rm -rf claudetask/frontend/node_modules
rm -rf claudetask/mcp_server/venv
rm -rf logs
rm -f start.sh stop.sh

# Запустить установку заново
./install.sh
```

## 🔄 Обновление

```bash
# Получить последние изменения
git pull origin main

# Переустановить зависимости (если нужно)
./install.sh

# Запустить обновленную версию
./start.sh
```

## 📚 Дополнительные ресурсы

- [QUICK_START.md](QUICK_START.md) - Быстрый старт
- [README.md](README.md) - Полная документация
- [IMPLEMENTATION_QUICK_START.md](IMPLEMENTATION_QUICK_START.md) - Гайд разработчика
- [API Docs](http://localhost:3333/docs) - Swagger документация (после запуска)

## 💡 Советы

1. **Используйте виртуальное окружение Python** - оно создается автоматически, не удаляйте папку `venv`
2. **Логи - ваш друг** - всегда проверяйте логи при проблемах
3. **Порты** - убедитесь, что порты 3333, 3334, 8000 свободны
4. **Версии** - используйте рекомендованные версии Python 3.11 и Node.js 20

## 🤝 Поддержка

Если возникли проблемы:
1. Проверьте логи в `logs/`
2. Проверьте системные требования
3. Создайте issue на GitHub
4. Смотрите документацию в `docs/`

---

**Удачной установки! 🚀**
