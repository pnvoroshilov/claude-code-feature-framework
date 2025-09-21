# Процесс инициализации проекта в ClaudeTask

## Детальное описание процесса

### 1. Backend API - Инициализация

#### Endpoint: POST /api/project/initialize
```python
async def initialize_project(request: InitProjectRequest):
    """
    Request:
    {
        "project_path": "/Users/username/my-project",
        "project_name": "My Awesome Project", 
        "github_repo": "username/my-project" (optional)
    }
    """
    
    # 1. Валидация пути
    if not os.path.exists(project_path):
        raise HTTPException(400, "Project path does not exist")
    
    if not os.path.isdir(project_path):
        raise HTTPException(400, "Path must be a directory")
    
    # 2. Проверка git
    is_git_repo = os.path.exists(os.path.join(project_path, '.git'))
    
    # 3. Определение технологий
    tech_stack = detect_technologies(project_path)
    # Ищет: package.json, requirements.txt, pom.xml, go.mod etc.
    
    # 4. Создание структуры .claudetask
    create_claudetask_structure(project_path, project_name, tech_stack)
    
    # 5. Сохранение в БД
    project = Project(
        id=generate_uuid(),
        path=project_path,
        name=project_name,
        github_repo=github_repo,
        tech_stack=tech_stack,
        created_at=datetime.now()
    )
    db.save(project)
    
    # 6. Автоматическая настройка MCP в Claude
    mcp_configured = configure_claude_mcp(project)
    
    return {
        "project_id": project.id,
        "mcp_configured": mcp_configured,
        "files_created": [
            ".claudetask/CLAUDE.md",
            ".claudetask/agents/",
            ".claudetask/mcp-config.json",
            ".claudetask/project.json"
        ],
        "claude_restart_required": True
    }
```

### 2. Создание файловой структуры

#### Функция create_claudetask_structure
```python
def create_claudetask_structure(project_path, project_name, tech_stack):
    """Создает все необходимые файлы в проекте пользователя."""
    
    claudetask_dir = os.path.join(project_path, '.claudetask')
    
    # 1. Создание директорий
    os.makedirs(claudetask_dir, exist_ok=True)
    os.makedirs(os.path.join(claudetask_dir, 'agents'), exist_ok=True)
    os.makedirs(os.path.join(claudetask_dir, 'templates'), exist_ok=True)
    os.makedirs(os.path.join(project_path, 'worktrees'), exist_ok=True)
    
    # 2. Генерация CLAUDE.md
    claude_md = generate_claude_md(project_name, project_path, tech_stack)
    with open(os.path.join(claudetask_dir, 'CLAUDE.md'), 'w') as f:
        f.write(claude_md)
    
    # 3. Копирование агентов
    copy_agents(claudetask_dir)
    
    # 4. Создание project.json
    project_meta = {
        "name": project_name,
        "path": project_path,
        "tech_stack": tech_stack,
        "initialized_at": datetime.now().isoformat()
    }
    with open(os.path.join(claudetask_dir, 'project.json'), 'w') as f:
        json.dump(project_meta, f, indent=2)
```

### 3. Генерация CLAUDE.md

```python
def generate_claude_md(project_name, project_path, tech_stack):
    """Генерирует кастомизированный CLAUDE.md для проекта."""
    
    template = """# Project: {project_name}

## ClaudeTask Integration ✅
You are working with ClaudeTask framework. This project is managed through the ClaudeTask system.

## MCP Commands
Always use these commands to work with tasks:
- `mcp:get_next_task` - Get the highest priority task from backlog
- `mcp:analyze_task <id>` - Analyze a specific task
- `mcp:update_status <id> <status>` - Update task status
- `mcp:create_worktree <id>` - Create isolated workspace for task
- `mcp:verify_connection` - Check ClaudeTask connection

## Project Configuration
- **Path**: {project_path}
- **Technologies**: {technologies}
- **Test Command**: {test_command}
- **Build Command**: {build_command}
- **Lint Command**: {lint_command}

## Workflow Rules
1. ⚠️ ALWAYS work through ClaudeTask tasks
2. ⚠️ NEVER make changes directly in main branch
3. ⚠️ ALWAYS use git worktrees for development
4. ⚠️ UPDATE task status in real-time
5. ⚠️ COMPLETE the full workflow for each task

## Task Workflow
1. **Get Task** → Retrieve from backlog via MCP
2. **Analyze** → Understand requirements and plan
3. **Develop** → Implement in isolated worktree
4. **Test** → Run tests and verify
5. **Review** → Self-review and create PR
6. **Complete** → Merge and cleanup

## Project Structure
{project_structure}

## Available Agents
- task-analyzer - For analyzing tasks
- feature-developer - For implementing features
- bug-fixer - For fixing bugs
- test-runner - For running tests
- code-reviewer - For code review

## Important Notes
- This project uses ClaudeTask for task management
- Check http://localhost:3000 for task board
- All tasks must go through the complete workflow
- Commit messages should reference task IDs
"""
    
    # Определение команд на основе tech_stack
    commands = detect_commands(tech_stack)
    
    # Генерация структуры проекта
    structure = generate_project_structure(project_path)
    
    return template.format(
        project_name=project_name,
        project_path=project_path,
        technologies=", ".join(tech_stack),
        test_command=commands.get('test', 'npm test'),
        build_command=commands.get('build', 'npm run build'),
        lint_command=commands.get('lint', 'npm run lint'),
        project_structure=structure
    )
```

### 4. Frontend - UI инициализации

```typescript
// InitializeProject.tsx
const InitializeProject: React.FC = () => {
  const [projectPath, setProjectPath] = useState('');
  const [projectName, setProjectName] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  
  const handleInitialize = async () => {
    setLoading(true);
    try {
      const response = await api.initializeProject({
        project_path: projectPath,
        project_name: projectName
      });
      
      setResult(response);
      // Показать инструкции для настройки MCP
    } catch (error) {
      console.error('Initialization failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Container>
      <Typography variant="h4">Initialize New Project</Typography>
      
      <TextField
        label="Project Path"
        value={projectPath}
        onChange={(e) => setProjectPath(e.target.value)}
        placeholder="/Users/username/my-project"
        fullWidth
      />
      
      <TextField
        label="Project Name"
        value={projectName}
        onChange={(e) => setProjectName(e.target.value)}
        placeholder="My Awesome Project"
        fullWidth
      />
      
      <Button 
        onClick={handleInitialize}
        variant="contained"
        disabled={loading || !projectPath || !projectName}
      >
        Initialize Project
      </Button>
      
      {result && (
        <Paper>
          <Typography variant="h6">✅ Project Initialized!</Typography>
          <Typography>Files created:</Typography>
          <List>
            {result.files_created.map(file => (
              <ListItem key={file}>{file}</ListItem>
            ))}
          </List>
          
          <Typography variant="h6">Next Steps:</Typography>
          <ol>
            <li>Add this to your claude_desktop_config.json:</li>
            <CodeBlock>{result.mcp_config}</CodeBlock>
            <li>Restart Claude Code in project directory</li>
            <li>Start creating tasks!</li>
          </ol>
        </Paper>
      )}
    </Container>
  );
};
```

### 5. Автоматическая конфигурация MCP

```python
def configure_claude_mcp(project):
    """Создает .mcp.json в корне проекта для Claude Code."""
    
    # Путь к .mcp.json в корне проекта
    mcp_config_path = os.path.join(project.path, ".mcp.json")
    
    # Чтение существующей конфигурации если есть
    if os.path.exists(mcp_config_path):
        try:
            with open(mcp_config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            # Если файл поврежден, создаем новый
            config = {}
    else:
        config = {}
    
    # Убедиться что есть секция mcpServers
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Добавление/обновление конфигурации ClaudeTask
    config["mcpServers"]["claudetask"] = {
        "command": "python",
        "args": [
            "-m",
            "claudetask_mcp_bridge",
            "--project-id", project.id,
            "--project-path", project.path,
            "--server", "http://localhost:3333"
        ]
    }
    
    # Сохранение конфигурации в проект
    try:
        with open(mcp_config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Created .mcp.json for project {project.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to create .mcp.json: {e}")
        return False
```

### 5.1 Слияние с существующими MCP серверами

```python
def merge_mcp_configs(project):
    """Сохраняет существующие MCP серверы при добавлении ClaudeTask."""
    
    mcp_config_path = os.path.join(project.path, ".mcp.json")
    
    # Чтение существующей конфигурации
    existing_config = {}
    if os.path.exists(mcp_config_path):
        try:
            with open(mcp_config_path, 'r') as f:
                existing_config = json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Invalid .mcp.json found, will overwrite")
    
    # Сохранение существующих серверов (кроме старых claudetask)
    preserved_servers = {}
    if "mcpServers" in existing_config:
        for server_name, server_config in existing_config["mcpServers"].items():
            # Сохраняем все серверы кроме claudetask
            if not server_name.startswith("claudetask"):
                preserved_servers[server_name] = server_config
    
    # Создание новой конфигурации
    new_config = {
        "mcpServers": {
            **preserved_servers,  # Сначала существующие серверы
            "claudetask": {       # Потом наш сервер
                "command": "python",
                "args": [
                    "-m",
                    "claudetask_mcp_bridge",
                    "--project-id", project.id,
                    "--project-path", project.path,
                    "--server", "http://localhost:3333"
                ]
            }
        }
    }
    
    # Сохранение
    with open(mcp_config_path, 'w') as f:
        json.dump(new_config, f, indent=2)
    
    logger.info(f"MCP config merged: {len(preserved_servers)} existing servers preserved")
    return True
```

### 6. Автоопределение технологий

```python
def detect_technologies(project_path):
    """Определяет используемые технологии в проекте."""
    
    technologies = []
    
    # JavaScript/TypeScript
    if os.path.exists(os.path.join(project_path, 'package.json')):
        with open(os.path.join(project_path, 'package.json')) as f:
            pkg = json.load(f)
            if 'react' in pkg.get('dependencies', {}):
                technologies.append('React')
            if 'vue' in pkg.get('dependencies', {}):
                technologies.append('Vue')
            if 'typescript' in pkg.get('devDependencies', {}):
                technologies.append('TypeScript')
            else:
                technologies.append('JavaScript')
    
    # Python
    if os.path.exists(os.path.join(project_path, 'requirements.txt')):
        technologies.append('Python')
        with open(os.path.join(project_path, 'requirements.txt')) as f:
            content = f.read()
            if 'django' in content:
                technologies.append('Django')
            if 'fastapi' in content:
                technologies.append('FastAPI')
            if 'flask' in content:
                technologies.append('Flask')
    
    # Java
    if os.path.exists(os.path.join(project_path, 'pom.xml')):
        technologies.append('Java')
        technologies.append('Maven')
    
    # Go
    if os.path.exists(os.path.join(project_path, 'go.mod')):
        technologies.append('Go')
    
    # Rust
    if os.path.exists(os.path.join(project_path, 'Cargo.toml')):
        technologies.append('Rust')
    
    return technologies
```

### 7. Проверка подключения Claude

После инициализации и перезапуска Claude Code, можно проверить подключение:

```python
# MCP endpoint: /connection/verify
async def verify_connection(project_id: str):
    """Проверяет, что Claude подключен к проекту."""
    
    project = db.get_project(project_id)
    if not project:
        return {"connected": False, "error": "Project not found"}
    
    # Проверка, что путь к проекту существует
    if not os.path.exists(project.path):
        return {"connected": False, "error": "Project path not found"}
    
    # Проверка наличия .claudetask
    claudetask_path = os.path.join(project.path, '.claudetask')
    if not os.path.exists(claudetask_path):
        return {"connected": False, "error": "Project not initialized"}
    
    return {
        "connected": True,
        "project_name": project.name,
        "project_path": project.path,
        "tasks_count": db.count_tasks(project_id),
        "active_task": db.get_active_task(project_id)
    }
```