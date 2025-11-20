-- Migration: Add worktree_enabled field to project_settings table
-- Date: 2025-11-20

-- Add worktree_enabled column to project_settings table
ALTER TABLE project_settings ADD COLUMN worktree_enabled BOOLEAN DEFAULT 1 NOT NULL;

-- Update existing project settings to have worktree_enabled = true (1)
UPDATE project_settings SET worktree_enabled = 1 WHERE worktree_enabled IS NULL;
