# Claude Sessions API - Usage Examples

## Quick Start

### 1. Start Backend Server

```bash
cd claudetask/backend
python -m uvicorn app.main:app --reload --port 3333
```

### 2. Test Endpoints

```bash
# Get all projects
curl http://localhost:3333/api/claude-sessions/projects

# Get sessions for a project
curl http://localhost:3333/api/claude-sessions/projects/Framework/sessions

# Get session details
curl "http://localhost:3333/api/claude-sessions/sessions/SESSION_ID?project_name=Framework"

# Search sessions
curl "http://localhost:3333/api/claude-sessions/sessions/search?query=error&project_name=Framework"

# Get statistics
curl http://localhost:3333/api/claude-sessions/statistics
```

## Frontend Integration Examples

### React Component Example

```typescript
import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface ClaudeSession {
  session_id: string;
  cwd: string;
  git_branch: string;
  message_count: number;
  tool_calls: Record<string, number>;
  created_at: string;
}

const ClaudeSessionsView: React.FC = () => {
  const [projects, setProjects] = useState([]);
  const [sessions, setSessions] = useState<ClaudeSession[]>([]);
  const [selectedProject, setSelectedProject] = useState<string>('');

  useEffect(() => {
    // Load projects
    axios.get('http://localhost:3333/api/claude-sessions/projects')
      .then(res => {
        setProjects(res.data.projects);
        if (res.data.projects.length > 0) {
          setSelectedProject(res.data.projects[0].name);
        }
      });
  }, []);

  useEffect(() => {
    if (selectedProject) {
      // Load sessions for selected project
      axios.get(`http://localhost:3333/api/claude-sessions/projects/${selectedProject}/sessions`)
        .then(res => setSessions(res.data.sessions));
    }
  }, [selectedProject]);

  return (
    <div>
      <h2>Claude Code Sessions</h2>

      <select
        value={selectedProject}
        onChange={(e) => setSelectedProject(e.target.value)}
      >
        {projects.map((p: any) => (
          <option key={p.name} value={p.name}>
            {p.name} ({p.sessions_count} sessions)
          </option>
        ))}
      </select>

      <div className="sessions-list">
        {sessions.map(session => (
          <div key={session.session_id} className="session-card">
            <h3>Session {session.session_id.substring(0, 8)}</h3>
            <p>Branch: {session.git_branch}</p>
            <p>Messages: {session.message_count}</p>
            <p>Tools: {Object.keys(session.tool_calls).join(', ')}</p>
            <p>Created: {new Date(session.created_at).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ClaudeSessionsView;
```

### Session Analytics Dashboard

```typescript
const SessionAnalytics: React.FC = () => {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    axios.get('http://localhost:3333/api/claude-sessions/statistics')
      .then(res => setStats(res.data.statistics));
  }, []);

  if (!stats) return <div>Loading...</div>;

  return (
    <div className="analytics-dashboard">
      <h2>Claude Sessions Analytics</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Sessions</h3>
          <p className="stat-value">{stats.total_sessions}</p>
        </div>

        <div className="stat-card">
          <h3>Total Messages</h3>
          <p className="stat-value">{stats.total_messages}</p>
        </div>

        <div className="stat-card">
          <h3>Files Modified</h3>
          <p className="stat-value">{stats.total_files_modified}</p>
        </div>

        <div className="stat-card">
          <h3>Total Errors</h3>
          <p className="stat-value">{stats.total_errors}</p>
        </div>
      </div>

      <div className="tool-usage">
        <h3>Most Used Tools</h3>
        {Object.entries(stats.total_tool_calls)
          .sort(([, a], [, b]) => (b as number) - (a as number))
          .slice(0, 10)
          .map(([tool, count]) => (
            <div key={tool} className="tool-bar">
              <span>{tool}</span>
              <span>{count} calls</span>
              <div
                className="usage-bar"
                style={{
                  width: `${(count as number / Math.max(...Object.values(stats.total_tool_calls))) * 100}%`
                }}
              />
            </div>
          ))
        }
      </div>

      <div className="recent-sessions">
        <h3>Recent Sessions</h3>
        {stats.recent_sessions.slice(0, 5).map((session: any) => (
          <div key={session.session_id} className="session-item">
            <span>{session.session_id.substring(0, 12)}...</span>
            <span>{session.message_count} messages</span>
            <span>{new Date(session.last_timestamp).toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
```

### Session Search Component

```typescript
const SessionSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<ClaudeSession[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        `http://localhost:3333/api/claude-sessions/sessions/search?query=${encodeURIComponent(query)}`
      );
      setResults(response.data.results);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="session-search">
      <h2>Search Sessions</h2>

      <div className="search-input">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for keywords, file names, errors..."
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button onClick={handleSearch} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      <div className="search-results">
        <p>{results.length} sessions found</p>
        {results.map(session => (
          <div key={session.session_id} className="result-card">
            <h4>Session {session.session_id.substring(0, 12)}...</h4>
            <p>Messages: {session.message_count}</p>
            <p>Branch: {session.git_branch}</p>
            <p>Created: {new Date(session.created_at).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
```

## Python Integration Examples

### Session Monitor Script

```python
#!/usr/bin/env python3
"""Monitor Claude Code sessions and generate reports"""

import time
from datetime import datetime, timedelta
from app.services.claude_sessions_reader import ClaudeSessionsReader

def monitor_sessions(project_name: str, interval: int = 60):
    """Monitor sessions and report new activity"""
    reader = ClaudeSessionsReader()
    last_check = datetime.now()

    while True:
        print(f"\n[{datetime.now()}] Checking for new sessions...")

        sessions = reader.get_project_sessions(project_name)
        new_sessions = [
            s for s in sessions
            if datetime.fromisoformat(s['last_timestamp']) > last_check
        ]

        if new_sessions:
            print(f"Found {len(new_sessions)} new/updated sessions:")
            for session in new_sessions:
                print(f"  - {session['session_id'][:12]}... ({session['message_count']} messages)")

        last_check = datetime.now()
        time.sleep(interval)

if __name__ == "__main__":
    monitor_sessions("Framework", interval=300)  # Check every 5 minutes
```

### Daily Report Generator

```python
#!/usr/bin/env python3
"""Generate daily activity reports"""

from datetime import datetime, timedelta
from app.services.claude_sessions_reader import ClaudeSessionsReader

def generate_daily_report(project_name: str):
    """Generate a daily activity report"""
    reader = ClaudeSessionsReader()
    sessions = reader.get_project_sessions(project_name)

    # Filter today's sessions
    today = datetime.now().date()
    today_sessions = [
        s for s in sessions
        if datetime.fromisoformat(s['last_timestamp']).date() == today
    ]

    if not today_sessions:
        print("No activity today.")
        return

    print(f"=== Daily Report for {project_name} - {today} ===\n")

    total_messages = sum(s['message_count'] for s in today_sessions)
    total_tools = {}
    total_files = set()

    for session in today_sessions:
        for tool, count in session['tool_calls'].items():
            total_tools[tool] = total_tools.get(tool, 0) + count
        total_files.update(session['files_modified'])

    print(f"Sessions: {len(today_sessions)}")
    print(f"Total Messages: {total_messages}")
    print(f"Files Modified: {len(total_files)}")
    print(f"\nMost Used Tools:")
    for tool, count in sorted(total_tools.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {tool}: {count} times")

    print(f"\nTop Sessions:")
    top_sessions = sorted(today_sessions, key=lambda x: x['message_count'], reverse=True)[:3]
    for i, session in enumerate(top_sessions, 1):
        print(f"  {i}. {session['session_id'][:12]}... - {session['message_count']} messages")

if __name__ == "__main__":
    generate_daily_report("Framework")
```

### Error Analyzer

```python
#!/usr/bin/env python3
"""Analyze errors across sessions"""

from collections import defaultdict
from app.services.claude_sessions_reader import ClaudeSessionsReader

def analyze_errors(project_name: str):
    """Analyze common errors and patterns"""
    reader = ClaudeSessionsReader()
    sessions = reader.get_project_sessions(project_name)

    error_sessions = [s for s in sessions if s['errors']]

    if not error_sessions:
        print("No errors found in sessions.")
        return

    print(f"=== Error Analysis for {project_name} ===\n")
    print(f"Sessions with errors: {len(error_sessions)} / {len(sessions)}")
    print(f"Total errors: {sum(len(s['errors']) for s in error_sessions)}\n")

    # Analyze error patterns
    error_keywords = defaultdict(int)

    for session in error_sessions:
        for error in session['errors']:
            content = error['content'].lower()
            # Extract common error keywords
            for keyword in ['permission', 'not found', 'timeout', 'failed', 'invalid']:
                if keyword in content:
                    error_keywords[keyword] += 1

    print("Common Error Types:")
    for keyword, count in sorted(error_keywords.items(), key=lambda x: x[1], reverse=True):
        print(f"  {keyword}: {count} occurrences")

    print(f"\nSessions with Most Errors:")
    error_sessions.sort(key=lambda x: len(x['errors']), reverse=True)
    for session in error_sessions[:5]:
        print(f"  {session['session_id'][:12]}... - {len(session['errors'])} errors")

if __name__ == "__main__":
    analyze_errors("Framework")
```

## Advanced Use Cases

### 1. Productivity Tracker

```python
def track_productivity(project_name: str, days: int = 7):
    """Track productivity metrics over time"""
    reader = ClaudeSessionsReader()
    sessions = reader.get_project_sessions(project_name)

    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(days=days)

    recent_sessions = [
        s for s in sessions
        if datetime.fromisoformat(s['last_timestamp']) > cutoff
    ]

    # Calculate metrics
    avg_messages = sum(s['message_count'] for s in recent_sessions) / len(recent_sessions)
    avg_tools = sum(len(s['tool_calls']) for s in recent_sessions) / len(recent_sessions)

    print(f"Productivity Report (Last {days} days)")
    print(f"Sessions: {len(recent_sessions)}")
    print(f"Avg Messages/Session: {avg_messages:.1f}")
    print(f"Avg Tools/Session: {avg_tools:.1f}")
```

### 2. Tool Usage Optimizer

```python
def suggest_tool_optimizations(project_name: str):
    """Suggest tool usage optimizations"""
    reader = ClaudeSessionsReader()
    stats = reader.get_session_statistics(project_name)

    # Analyze tool patterns
    read_count = stats['total_tool_calls'].get('Read', 0)
    write_count = stats['total_tool_calls'].get('Write', 0)
    edit_count = stats['total_tool_calls'].get('Edit', 0)

    print("Tool Usage Recommendations:")

    if write_count > edit_count * 2:
        print("  ⚠️ Consider using Edit instead of Write for file modifications")

    if read_count > 1000:
        print("  ✅ High Read usage - consider caching frequently accessed files")
```

### 3. Session Comparison

```python
def compare_sessions(project_name: str, session_id_1: str, session_id_2: str):
    """Compare two sessions"""
    reader = ClaudeSessionsReader()

    s1 = reader.get_session_details(project_name, session_id_1)
    s2 = reader.get_session_details(project_name, session_id_2)

    print(f"Comparison: {session_id_1[:12]} vs {session_id_2[:12]}\n")
    print(f"Messages: {s1['message_count']} vs {s2['message_count']}")
    print(f"Tools: {len(s1['tool_calls'])} vs {len(s2['tool_calls'])}")
    print(f"Files: {len(s1['files_modified'])} vs {len(s2['files_modified'])}")
```

## API Response Caching

For better performance with large projects:

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedSessionsReader:
    def __init__(self):
        self.reader = ClaudeSessionsReader()
        self._cache_timestamp = {}

    @lru_cache(maxsize=32)
    def get_projects_cached(self, cache_key: str):
        """Cached version of get_all_projects"""
        return self.reader.get_all_projects()

    def get_projects(self, cache_ttl: int = 300):
        """Get projects with caching (TTL in seconds)"""
        now = datetime.now()
        cache_key = f"projects_{now.timestamp() // cache_ttl}"
        return self.get_projects_cached(cache_key)
```

## Best Practices

1. **Rate Limiting**: Don't poll too frequently (minimum 30 seconds)
2. **Caching**: Cache results for static data (project list)
3. **Pagination**: Limit number of sessions returned (use slicing)
4. **Error Handling**: Handle missing/corrupted JSONL files gracefully
5. **Performance**: Use `include_messages=False` for list views

## Troubleshooting

### Issue: No projects found

```python
# Check if Claude projects directory exists
from pathlib import Path
claude_dir = Path.home() / ".claude" / "projects"
print(f"Exists: {claude_dir.exists()}")
print(f"Contents: {list(claude_dir.iterdir())}")
```

### Issue: Invalid JSON in session file

```python
# Skip invalid lines
try:
    entry = json.loads(line)
except json.JSONDecodeError:
    logger.warning(f"Invalid JSON at line {line_num}")
    continue
```

### Issue: Large sessions causing memory issues

```python
# Stream large sessions instead of loading all
def stream_session_lines(session_file: Path):
    with open(session_file, 'r') as f:
        for line in f:
            yield json.loads(line)
```

---

**Last Updated:** 2025-11-13
