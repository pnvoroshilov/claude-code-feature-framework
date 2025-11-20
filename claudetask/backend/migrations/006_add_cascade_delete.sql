-- Migration 006: Add CASCADE DELETE to all foreign keys referencing projects.id
-- This ensures that when a project is deleted, all related records are automatically deleted

-- SQLite doesn't support ALTER TABLE to modify foreign keys directly
-- We need to recreate tables with CASCADE DELETE

-- Note: This migration will be applied via Python script that handles the complex table recreation
