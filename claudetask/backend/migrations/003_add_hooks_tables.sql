-- Migration: Add hooks tables
-- Run this migration to add support for Claude Code hooks management

-- Default hooks provided by the framework
CREATE TABLE IF NOT EXISTS default_hooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    file_name VARCHAR(100) NOT NULL,
    hook_config JSON NOT NULL,
    setup_instructions TEXT,
    dependencies JSON,
    is_active BOOLEAN DEFAULT 1,
    is_favorite BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Custom hooks created by users
CREATE TABLE IF NOT EXISTS custom_hooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id VARCHAR NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    file_name VARCHAR(100) NOT NULL,
    hook_config JSON NOT NULL,
    setup_instructions TEXT,
    dependencies JSON,
    status VARCHAR(20) DEFAULT 'active',
    error_message TEXT,
    created_by VARCHAR(100) DEFAULT 'user',
    is_favorite BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Junction table for project-hook many-to-many relationship
CREATE TABLE IF NOT EXISTS project_hooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id VARCHAR NOT NULL,
    hook_id INTEGER NOT NULL,
    hook_type VARCHAR(10) NOT NULL,
    enabled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    enabled_by VARCHAR(100) DEFAULT 'user',
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_custom_hooks_project ON custom_hooks(project_id);
CREATE INDEX IF NOT EXISTS idx_project_hooks_project ON project_hooks(project_id);
CREATE INDEX IF NOT EXISTS idx_default_hooks_category ON default_hooks(category);
CREATE INDEX IF NOT EXISTS idx_custom_hooks_category ON custom_hooks(category);
