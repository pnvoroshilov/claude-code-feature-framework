-- Migration: Add manual_testing_mode and manual_review_mode to project_settings
-- Date: 2025-11-21
-- Purpose: Support UC-04 (testing variants) and UC-05 (review variants)

-- Add manual_testing_mode column (UC-04)
ALTER TABLE project_settings ADD COLUMN manual_testing_mode BOOLEAN DEFAULT 1 NOT NULL;

-- Add manual_review_mode column (UC-05)
ALTER TABLE project_settings ADD COLUMN manual_review_mode BOOLEAN DEFAULT 1 NOT NULL;

-- Set defaults for existing projects
-- Default to manual mode (true) for backward compatibility
UPDATE project_settings SET manual_testing_mode = 1 WHERE manual_testing_mode IS NULL;
UPDATE project_settings SET manual_review_mode = 1 WHERE manual_review_mode IS NULL;
