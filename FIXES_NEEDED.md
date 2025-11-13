# 🔧 Исправления для Claude Code Sessions

## ✅ Уже исправлено в backend:

### 1. Названия проектов
- ✅ Fixed в `claude_sessions_reader.py:42-46`
- Теперь показывает "Start Up / Framework" вместо "Framework"

### 2. Загрузка деталей сессии
- ✅ Fixed в `claude_sessions.py:55-116`
- Использует `project_dir` вместо `project_name`
- Правильно загружает messages

## ⚠️ Нужны исправления в frontend:

### Frontend Fix #1: Хранить весь объект проекта

В `ClaudeCodeSessions.tsx` строка 114:

```typescript
// БЫЛО:
const [selectedProject, setSelectedProject] = useState<string>('');

// ДОЛЖНО БЫТЬ:
const [selectedProject, setSelectedProject] = useState<ClaudeCodeProject | null>(null);
```

### Frontend Fix #2: Выбирать весь объект проекта

Строка ~131:

```typescript
// БЫЛО:
if (response.data.projects.length > 0 && !selectedProject) {
  setSelectedProject(response.data.projects[0].name);
}

// ДОЛЖНО БЫТЬ:
if (response.data.projects.length > 0 && !selectedProject) {
  setSelectedProject(response.data.projects[0]);  // весь объект!
}
```

### Frontend Fix #3: Обновить useEffect

Строка ~200:

```typescript
// БЫЛО:
useEffect(() => {
  if (selectedProject) {
    fetchSessions(selectedProject);
    fetchStatistics(selectedProject);
  }
}, [selectedProject]);

// ДОЛЖНО БЫТЬ:
useEffect(() => {
  if (selectedProject) {
    fetchSessions(selectedProject.name);
    fetchStatistics(selectedProject.name);
  }
}, [selectedProject]);
```

### Frontend Fix #4: Передавать directory в openDetails

Строка ~186:

```typescript
// БЫЛО:
const openDetails = async (session: ClaudeCodeSession) => {
  try {
    const response = await axios.get(
      `${API_BASE}/sessions/${session.session_id}?project_name=${selectedProject}&include_messages=true`
    );
    // ...
  }
};

// ДОЛЖНО БЫТЬ:
const openDetails = async (session: ClaudeCodeSession) => {
  try {
    if (!selectedProject) return;

    const response = await axios.get(
      `${API_BASE}/sessions/${session.session_id}?project_dir=${encodeURIComponent(selectedProject.directory)}&include_messages=true`
    );
    setSelectedSession(response.data.session);
    setDetailsOpen(true);
    setTabValue(0);
  } catch (error) {
    console.error('Error fetching session details:', error);
  }
};
```

### Frontend Fix #5: Обновить Select компонент

Строка ~248:

```typescript
// БЫЛО:
<Select
  value={selectedProject}
  onChange={(e) => setSelectedProject(e.target.value)}
  label="Project"
>
  {projects.map((project) => (
    <MenuItem key={project.name} value={project.name}>

// ДОЛЖНО БЫТЬ:
<Select
  value={selectedProject?.name || ''}
  onChange={(e) => {
    const project = projects.find(p => p.name === e.target.value);
    if (project) setSelectedProject(project);
  }}
  label="Project"
>
  {projects.map((project) => (
    <MenuItem key={project.directory} value={project.name}>
```

### Frontend Fix #6: Обновить handleSearch

Строка ~170:

```typescript
// БЫЛО:
const url = selectedProject
  ? `${API_BASE}/sessions/search?query=${encodeURIComponent(searchQuery)}&project_name=${selectedProject}`
  : `${API_BASE}/sessions/search?query=${encodeURIComponent(searchQuery)}`;

// ДОЛЖНО БЫТЬ:
const url = selectedProject
  ? `${API_BASE}/sessions/search?query=${encodeURIComponent(searchQuery)}&project_name=${selectedProject.name}`
  : `${API_BASE}/sessions/search?query=${encodeURIComponent(searchQuery)}`;
```

## 3️⃣ Мониторинг активных сессий

Нужно добавить:

### Backend: Endpoint для активных сессий

Добавить в `claude_sessions.py`:

```python
@router.get("/active-sessions")
async def get_active_sessions():
    """Get currently active Claude Code sessions"""
    try:
        # Get list of running claude processes
        import subprocess
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )

        active = []
        for line in result.stdout.split('\n'):
            if 'claude' in line.lower() and 'code' in line.lower():
                # Parse process info
                parts = line.split()
                if len(parts) > 10:
                    active.append({
                        "pid": parts[1],
                        "command": ' '.join(parts[10:])
                    })

        return {
            "success": True,
            "active_sessions": active,
            "count": len(active)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{pid}/kill")
async def kill_session(pid: int):
    """Kill an active Claude Code session"""
    try:
        import os
        import signal

        os.kill(pid, signal.SIGTERM)

        return {
            "success": True,
            "message": f"Session {pid} terminated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Frontend: Показывать активные сессии

Добавить в `ClaudeCodeSessions.tsx`:

```typescript
const [activeSessions, setActiveSessions] = useState<any[]>([]);

const fetchActiveSessions = async () => {
  try {
    const response = await axios.get(`${API_BASE}/active-sessions`);
    setActiveSessions(response.data.active_sessions);
  } catch (error) {
    console.error('Error fetching active sessions:', error);
  }
};

const killSession = async (pid: number) => {
  if (!confirm(`Kill session ${pid}?`)) return;

  try {
    await axios.post(`${API_BASE}/sessions/${pid}/kill`);
    fetchActiveSessions();
    alert('Session terminated');
  } catch (error) {
    console.error('Error killing session:', error);
    alert('Failed to kill session');
  }
};

// В useEffect добавить:
useEffect(() => {
  fetchActiveSessions();

  // Refresh every 5 seconds
  const interval = setInterval(fetchActiveSessions, 5000);
  return () => clearInterval(interval);
}, []);
```

### Frontend: UI для активных сессий

Добавить перед таблицей сессий:

```tsx
{/* Active Sessions Alert */}
{activeSessions.length > 0 && (
  <Alert severity="success" sx={{ mb: 2 }}>
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <Typography>
        🟢 {activeSessions.length} active Claude Code session{activeSessions.length > 1 ? 's' : ''}
      </Typography>
      <Button
        size="small"
        onClick={() => setShowActiveDetails(!showActiveDetails)}
      >
        {showActiveDetails ? 'Hide' : 'Show'} Details
      </Button>
    </Box>

    {showActiveDetails && (
      <List sx={{ mt: 1 }}>
        {activeSessions.map((session) => (
          <ListItem key={session.pid}>
            <ListItemText
              primary={`PID: ${session.pid}`}
              secondary={session.command.substring(0, 100)}
            />
            <IconButton
              color="error"
              onClick={() => killSession(parseInt(session.pid))}
            >
              <StopIcon />
            </IconButton>
          </ListItem>
        ))}
      </List>
    )}
  </Alert>
)}
```

## 🚀 Быстрое тестирование

После исправлений протестировать:

```bash
# 1. Рестарт backend (уже запущен)
# Backend автоматически перезагрузится

# 2. Рестарт frontend
cd claudetask/frontend
npm start

# 3. Проверить:
# - Названия проектов (должны быть "Start Up / Framework")
# - Детали сессии (должны загружаться messages)
# - Активные сессии (должны показываться)
```

## 📝 Summary

**Backend:** ✅ Готов

**Frontend:** ⚠️ Нужны 6 исправлений в `ClaudeCodeSessions.tsx`

**Active Sessions:** ⚠️ Нужно добавить 2 endpoint + UI

---

**Все исправления занимают ~5-10 минут ручного редактирования, сэр!**
