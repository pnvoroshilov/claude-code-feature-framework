# Built-in Tools - Complete Reference

Comprehensive guide to all built-in tools available in Claude Agent SDK.

## Overview

Claude Code provides 20+ built-in tools for file operations, command execution, web access, and development workflows. Control access via `allowed_tools` and `disallowed_tools` in ClaudeAgentOptions.

## Tool Categories (TOON Format)

```
categories[6]{category,tool_count,primary_purpose}:
File Operations,6,"Reading, writing, editing, and searching files"
Execution,3,"Shell commands and background processes"
Web Access,2,"Internet search and content retrieval"
Development,2,"Notebooks and task management"
Orchestration,2,"Subagents and skills"
MCP,2,"MCP resource access"
```

## File Operations Tools

### Read

**Purpose:** Read file contents with optional line range control

**Parameters (TOON):**
```
params[3]{parameter,type,description}:
file_path,str,Absolute path to file (required)
offset,int,Starting line number (optional)
limit,int,Maximum lines to read (optional)
```

**Returns:** File contents with line numbers (cat -n format)

**Examples:**
```python
# Read entire file
"Read entire config file"
→ Claude uses: Read(file_path="/app/config.yaml")

# Read specific range
"Read lines 100-200 of server.py"
→ Claude uses: Read(file_path="/app/server.py", offset=100, limit=100)

# Read beginning
"Show first 50 lines of log"
→ Claude uses: Read(file_path="/var/log/app.log", limit=50)
```

**Features:**
- Supports text files, code, configuration files
- Can read images (returns visual representation)
- Can read PDFs (extracts text and visual content)
- Can read Jupyter notebooks (.ipynb files)
- Line numbers included for easy reference
- Truncates lines longer than 2000 characters

**Best Practices:**
- Use offset/limit for large files to reduce token usage
- Combine with Grep for targeted searching
- Use Glob to find file paths before reading

### Write

**Purpose:** Create new file or completely overwrite existing file

**Parameters:**
```
params[2]{parameter,type,description}:
file_path,str,Absolute path to file (required)
content,str,Complete file content (required)
```

**Returns:** Success confirmation

**Examples:**
```python
# Create new file
"Create a Python web server"
→ Claude uses: Write(
    file_path="/app/server.py",
    content="from flask import Flask\napp = Flask(__name__)"
)

# Overwrite existing
"Replace config.json with default settings"
→ Claude uses: Write(
    file_path="/app/config.json",
    content='{"debug": false, "port": 8080}'
)
```

**Important Notes:**
- **Destructive operation** - overwrites without backup
- Requires file path to be in allowed directories
- Creates parent directories if they don't exist
- Use Edit for partial modifications

**Best Practices:**
- Use Edit instead of Write for modifications to existing files
- Always Read file first before overwriting
- Consider permission_mode="acceptEdits" for automation

### Edit

**Purpose:** Replace specific text in existing file (non-destructive)

**Parameters:**
```
params[4]{parameter,type,description}:
file_path,str,Absolute path to file (required)
old_string,str,Exact text to replace (required)
new_string,str,Replacement text (required)
replace_all,bool,Replace all occurrences (default: false)
```

**Returns:** Success confirmation with changes made

**Examples:**
```python
# Single replacement
"Change API endpoint from /v1 to /v2"
→ Claude uses: Edit(
    file_path="/app/api.py",
    old_string='BASE_URL = "https://api.example.com/v1"',
    new_string='BASE_URL = "https://api.example.com/v2"'
)

# Replace all occurrences
"Rename variable user_id to userId everywhere"
→ Claude uses: Edit(
    file_path="/app/models.py",
    old_string="user_id",
    new_string="userId",
    replace_all=True
)
```

**Important Notes:**
- `old_string` must be **exact match** (including whitespace/indentation)
- Fails if `old_string` not found or ambiguous (multiple matches without replace_all)
- Must Read file first to ensure exact text matching
- Preserves file encoding and line endings

**Best Practices:**
- Include surrounding context in old_string for uniqueness
- Use replace_all for variable renaming
- Prefer Edit over Write for modifications to existing files
- Read file first to verify current content

### Grep

**Purpose:** Search files using regex patterns (ripgrep-based)

**Parameters:**
```
params[10]{parameter,type,default,description}:
pattern,str,required,Regular expression pattern to search
path,str,current_dir,File or directory to search
output_mode,str,files_with_matches,"Output type: content|files_with_matches|count"
glob,str,None,"File pattern filter (e.g., '*.py')"
type,str,None,"File type filter (e.g., 'python', 'js')"
-i,bool,False,Case insensitive search
-n,bool,True,Show line numbers (content mode only)
-A,int,0,Lines of context after match
-B,int,0,Lines of context before match
-C,int,0,Lines of context before and after
multiline,bool,False,Enable multiline pattern matching
head_limit,int,auto,Limit output lines/entries
offset,int,0,Skip first N results
```

**Output Modes:**
```
modes[3]{mode,returns,use_case}:
files_with_matches,File paths only (default),Finding files containing pattern
content,Matching lines with context,Viewing actual matches
count,Match counts per file,Quantitative analysis
```

**Examples:**
```python
# Find files containing pattern
"Find all Python files importing asyncio"
→ Claude uses: Grep(
    pattern="import asyncio",
    type="python"
)

# View matching content
"Show all TODO comments with context"
→ Claude uses: Grep(
    pattern="TODO:",
    output_mode="content",
    -C=2
)

# Case insensitive with file filter
"Search for 'database' in YAML files"
→ Claude uses: Grep(
    pattern="database",
    glob="*.yaml",
    -i=True,
    output_mode="content"
)

# Count occurrences
"Count how many times 'fetch' appears in each JavaScript file"
→ Claude uses: Grep(
    pattern="fetch",
    type="js",
    output_mode="count"
)
```

**Advanced Features:**
```python
# Multiline patterns
Grep(
    pattern=r"class.*?\{.*?constructor",
    multiline=True,
    type="js"
)

# Context lines
Grep(
    pattern="ERROR",
    path="/var/log/app.log",
    -B=5,  # 5 lines before
    -A=10, # 10 lines after
    output_mode="content"
)

# Limited results
Grep(
    pattern="function",
    type="js",
    head_limit=20,  # First 20 matches
    offset=10       # Skip first 10
)
```

**Best Practices:**
- Use `type` parameter for efficiency (faster than `glob`)
- Start with `files_with_matches` mode, then switch to `content`
- Use context lines (-A/-B/-C) to understand match surroundings
- Enable multiline for cross-line patterns
- Use head_limit to prevent overwhelming output

### Glob

**Purpose:** Find files matching glob patterns

**Parameters:**
```
params[2]{parameter,type,description}:
pattern,str,Glob pattern (required)
path,str,Directory to search (optional)
```

**Returns:** List of matching file paths sorted by modification time

**Glob Pattern Syntax:**
```
patterns[6]{pattern,matches,example}:
*,Any characters in filename,"*.py → all Python files"
**,Recursive directory traversal,"**/*.js → all JS in subdirs"
?,Single character,"test?.py → test1.py, testA.py"
[abc],Character set,"file[123].txt"
{a,b},Alternatives,"{src,test}/**/*.py"
**/*,All files recursively,"**/* → everything"
```

**Examples:**
```python
# Find all Python files
"Find all Python files in project"
→ Claude uses: Glob(pattern="**/*.py")

# Find config files
"List all YAML configuration files"
→ Claude uses: Glob(pattern="**/*.{yaml,yml}")

# Find test files
"Show all test files"
→ Claude uses: Glob(pattern="**/*test*.{py,js,ts}")

# Specific directory
"Find markdown files in docs/"
→ Claude uses: Glob(pattern="*.md", path="/project/docs")
```

**Best Practices:**
- Use specific patterns to reduce noise
- Combine with Read to process found files
- Use alternatives syntax for multiple extensions
- Results are sorted by modification time (newest first)

### NotebookEdit

**Purpose:** Edit Jupyter notebook (.ipynb) cells

**Parameters:**
```
params[5]{parameter,type,description}:
notebook_path,str,Absolute path to .ipynb file (required)
new_source,str,New cell content (required)
cell_id,str,Cell ID to edit (optional)
cell_type,str,"Cell type: code|markdown (required for insert)"
edit_mode,str,"Edit type: replace|insert|delete (default: replace)"
```

**Edit Modes:**
```
modes[3]{mode,action,use_case}:
replace,Replace existing cell content,Modify code or markdown
insert,Add new cell,Add new code or documentation
delete,Remove cell,Clean up notebook
```

**Examples:**
```python
# Replace cell content
"Update the data loading cell"
→ Claude uses: NotebookEdit(
    notebook_path="/project/analysis.ipynb",
    cell_id="cell_abc123",
    new_source="import pandas as pd\ndf = pd.read_csv('data.csv')"
)

# Insert new code cell
"Add a visualization cell"
→ Claude uses: NotebookEdit(
    notebook_path="/project/analysis.ipynb",
    cell_id="cell_after_this",
    cell_type="code",
    edit_mode="insert",
    new_source="df.plot(kind='bar')"
)

# Delete cell
"Remove the debugging cell"
→ Claude uses: NotebookEdit(
    notebook_path="/project/analysis.ipynb",
    cell_id="cell_xyz789",
    edit_mode="delete",
    new_source=""  # Required but unused
)
```

**Best Practices:**
- Read notebook first to get cell IDs
- Use cell_type when inserting
- Validate new_source syntax before editing
- Consider running cells after modification

## Execution Tools

### Bash

**Purpose:** Execute shell commands with timeout and background support

**Parameters:**
```
params[4]{parameter,type,default,description}:
command,str,required,Shell command to execute
timeout,int,120000,"Timeout in milliseconds (max: 600000 = 10 min)"
run_in_background,bool,False,Run command in background
description,str,None,Human-readable command description
```

**Returns:** stdout, stderr, and exit code

**Examples:**
```python
# Simple command
"List files in current directory"
→ Claude uses: Bash(command="ls -la")

# With timeout
"Run long-running test suite"
→ Claude uses: Bash(
    command="pytest tests/",
    timeout=300000  # 5 minutes
)

# Background execution
"Start development server in background"
→ Claude uses: Bash(
    command="npm run dev",
    run_in_background=True
)

# Chained commands
"Install and test package"
→ Claude uses: Bash(
    command="pip install -e . && pytest"
)
