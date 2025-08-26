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
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);


-- ============================================
-- Tasks Table
-- ============================================

CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,               -- UUID v4
  user_id TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  due_date TEXT,                     -- ISO 8601 Date or DateTime
  priority INTEGER DEFAULT 2,        -- 1=High, 2=Medium, 3=Low
  status TEXT DEFAULT 'pending',     -- 'pending' or 'done'
  is_deleted INTEGER DEFAULT 0,
  deleted_at TEXT,
  last_modified TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  synced INTEGER DEFAULT 0,          -- 0=not synced, 1=synced
  FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_tasks_user_lastmod ON tasks(user_id, last_modified);


-- ============================================
-- Notes Table
-- ============================================

CREATE TABLE IF NOT EXISTS notes (
  id TEXT PRIMARY KEY,               -- UUID v4
  user_id TEXT NOT NULL,
  content TEXT NOT NULL,
  is_deleted INTEGER DEFAULT 0,
  deleted_at TEXT,
  last_modified TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  synced INTEGER DEFAULT 0,
  FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_notes_user_lastmod ON notes(user_id, last_modified);


-- ============================================
-- Expenses Table
-- ============================================

CREATE TABLE IF NOT EXISTS expenses (
  id TEXT PRIMARY KEY,               -- UUID v4
  user_id TEXT NOT NULL,
  amount REAL NOT NULL,
  category TEXT NOT NULL,
  description TEXT,
  date TEXT NOT NULL,                -- ISO 8601 Date YYYY-MM-DD
  is_deleted INTEGER DEFAULT 0,
  deleted_at TEXT,
  last_modified TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  synced INTEGER DEFAULT 0,
  FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_expenses_user_lastmod ON expenses(user_id, last_modified);