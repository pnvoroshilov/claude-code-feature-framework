-- Migration: Add testing configuration fields to project_settings
-- Date: 2025-11-25
-- Description: Adds test_directory, test_framework, auto_merge_tests, test_staging_dir columns

-- Add test_directory column (default: 'tests')
ALTER TABLE project_settings ADD COLUMN test_directory TEXT DEFAULT 'tests';

-- Add test_framework column (default: 'pytest')
ALTER TABLE project_settings ADD COLUMN test_framework TEXT DEFAULT 'pytest';

-- Add auto_merge_tests column (default: true/1)
ALTER TABLE project_settings ADD COLUMN auto_merge_tests BOOLEAN DEFAULT 1 NOT NULL;

-- Add test_staging_dir column (default: 'tests/staging')
ALTER TABLE project_settings ADD COLUMN test_staging_dir TEXT DEFAULT 'tests/staging';
