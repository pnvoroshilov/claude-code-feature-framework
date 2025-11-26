-- Migration: Add storage_mode column to project_settings
-- Purpose: Enable per-project storage mode selection (local vs mongodb)
-- Author: ClaudeTask Framework
-- Date: 2025-11-26

-- Add storage_mode column with default 'local' for backward compatibility
ALTER TABLE project_settings
ADD COLUMN storage_mode TEXT NOT NULL DEFAULT 'local';

-- Valid values: 'local' (SQLite + ChromaDB) or 'mongodb' (MongoDB Atlas + Vector Search)
-- Immutable after project creation (enforced in application layer)

-- Create index for faster storage mode lookups
CREATE INDEX IF NOT EXISTS idx_project_settings_storage_mode
ON project_settings(storage_mode);

-- Add comment explaining the column (SQLite supports this via pragma)
-- storage_mode:
--   - 'local': SQLite + ChromaDB with all-MiniLM-L6-v2 embeddings (384d)
--   - 'mongodb': MongoDB Atlas + Vector Search with voyage-3-large embeddings (1024d)

-- Update existing projects to use 'local' storage mode (backward compatibility)
UPDATE project_settings
SET storage_mode = 'local'
WHERE storage_mode IS NULL OR storage_mode = '';

-- Verify migration
SELECT COUNT(*) as total_projects,
       SUM(CASE WHEN storage_mode = 'local' THEN 1 ELSE 0 END) as local_storage,
       SUM(CASE WHEN storage_mode = 'mongodb' THEN 1 ELSE 0 END) as mongodb_storage
FROM project_settings;
