-- Migration: Add last_summarized_message_id to project_summaries
-- Date: 2025-11-25
-- Purpose: Track which message was last included in summary for efficient summarization

ALTER TABLE project_summaries ADD COLUMN last_summarized_message_id INTEGER DEFAULT 0;
