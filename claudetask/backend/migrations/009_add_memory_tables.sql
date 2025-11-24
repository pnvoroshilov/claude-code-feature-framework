-- Migration: Add conversation memory and project summary tables
-- Date: 2025-11-23
-- Purpose: Enable cross-session memory persistence for Claude Code

-- Table for storing all conversation messages
CREATE TABLE IF NOT EXISTS conversation_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,           -- UUID of the project
    session_id TEXT,                    -- Session identifier
    task_id INTEGER,                    -- Optional task reference
    message_type TEXT NOT NULL,         -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,              -- Full raw message content
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,                      -- JSON metadata

    -- Foreign key to tasks table
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_conv_project ON conversation_memory(project_id);
CREATE INDEX IF NOT EXISTS idx_conv_timestamp ON conversation_memory(project_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_conv_session ON conversation_memory(session_id);
CREATE INDEX IF NOT EXISTS idx_conv_task ON conversation_memory(task_id);
CREATE INDEX IF NOT EXISTS idx_conv_type ON conversation_memory(message_type);

-- Table for project summaries (3-5 pages of context)
CREATE TABLE IF NOT EXISTS project_summaries (
    project_id TEXT PRIMARY KEY,        -- UUID of the project
    summary TEXT,                       -- 3-5 pages of summarized context
    key_decisions TEXT,                 -- JSON array of key decisions
    tech_stack TEXT,                    -- JSON array of technologies
    patterns TEXT,                      -- JSON array of discovered patterns
    gotchas TEXT,                       -- JSON array of gotchas/issues
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,

    -- Foreign key to projects table
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Table for RAG metadata (tracks what's indexed)
CREATE TABLE IF NOT EXISTS memory_rag_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    message_id INTEGER NOT NULL,
    indexed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    collection_name TEXT,
    embedding_model TEXT,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (message_id) REFERENCES conversation_memory(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_rag_project ON memory_rag_status(project_id);
CREATE INDEX IF NOT EXISTS idx_rag_message ON memory_rag_status(message_id);

-- Table for memory sessions (tracks memory loading)
CREATE TABLE IF NOT EXISTS memory_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    context_loaded_at DATETIME,
    summary_version INTEGER,
    messages_loaded INTEGER DEFAULT 0,
    rag_results_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_mem_session ON memory_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_mem_project_session ON memory_sessions(project_id, session_id);