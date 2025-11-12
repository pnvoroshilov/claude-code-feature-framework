-- Migration: Add custom_instructions field to projects table
-- Date: 2025-01-12
-- Description: Adds a custom_instructions TEXT column to store project-specific Claude instructions

-- Add custom_instructions column to projects table
ALTER TABLE projects ADD COLUMN custom_instructions TEXT DEFAULT '';

-- Optional: Update existing projects with empty string (SQLite default behavior)
UPDATE projects SET custom_instructions = '' WHERE custom_instructions IS NULL;
