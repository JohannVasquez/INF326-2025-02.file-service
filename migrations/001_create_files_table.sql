-- Migration: create files table for file-service
CREATE TABLE IF NOT EXISTS files (
    id TEXT PRIMARY KEY,
    original_name TEXT,
    path TEXT,
    content_type TEXT,
    size INTEGER,
    chat_id TEXT,
    message_id TEXT,
    thread_id TEXT,
    created_at TEXT
);
