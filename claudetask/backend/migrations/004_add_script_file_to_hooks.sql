-- Migration: Add script_file column to hooks tables
-- This migration adds support for separate script files (e.g., post-push-docs.sh)

-- Add script_file to default_hooks
ALTER TABLE default_hooks ADD COLUMN script_file VARCHAR(100);

-- Add script_file to custom_hooks
ALTER TABLE custom_hooks ADD COLUMN script_file VARCHAR(100);
