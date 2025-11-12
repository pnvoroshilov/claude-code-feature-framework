-- Migration: Add project_mode field to projects table
-- Date: 2025-11-12
-- Description: Adds project_mode column to support simple and development modes

ALTER TABLE projects ADD COLUMN project_mode TEXT DEFAULT 'simple' NOT NULL;

-- Update existing projects to simple mode by default
UPDATE projects SET project_mode = 'simple' WHERE project_mode IS NULL OR project_mode = '';
