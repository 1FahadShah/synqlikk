-- SynQlikk DB Schema
-- Version 1.0
-- Applied to BOTH local_cache.db and server.db

-- ============================================
-- Users Table
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,         -- UUID v4
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    modified_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    is_deleted INTEGER DEFULT 0
);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)