# SynQlikk CLI

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**SynQlikk CLI** is a powerful local-first productivity tool that allows you to manage **tasks, notes, and expenses** with offline-first capabilities and **two-way server synchronization**. It provides a **terminal-based interface**, secure authentication, and automatic sync with a remote server.

---

## Table of Contents

- [SynQlikk CLI](#synqlikk-cli)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Getting Started](#getting-started)
  - [Authentication](#authentication)
    - [Login](#login)
    - [Register](#register)
    - [Logout](#logout)
  - [Main Menu \& Features](#main-menu--features)
    - [Tasks](#tasks)
    - [Notes](#notes)
    - [Expenses](#expenses)
    - [Sync with Server](#sync-with-server)
  - [Database](#database)
  - [Error Handling](#error-handling)
  - [Utilities](#utilities)
  - [Example Workflows](#example-workflows)
    - [Add a Task, Note, and Expense \& Sync](#add-a-task-note-and-expense--sync)
  - [License](#license)

---

## Features

- **User Authentication**

  - Secure login and registration via server API
  - Local session storage (`.synqlikk_session.json`)
  - Automatic syncing on login/registration

- **Tasks Management**

  - Add, view, edit, delete tasks
  - Task attributes: `title`, `description`, `due_date`, `priority`, `status`
  - Standardized status: `pending`, `in_progress`, `completed`

- **Notes Management**

  - Add, view, edit, delete notes
  - Long notes handled with preview in tables
  - Automatic tracking of last modification

- **Expenses Management**

  - Add, view, edit, delete expenses
  - Attributes: `amount`, `category`, `description`, `date`
  - Optional description, automatic local timestamping

- **Two-way Sync**

  - Push local changes to server
  - Pull server updates to local DB
  - Conflict resolution (server wins)
  - Full sync or incremental sync
  - Tracks last sync time in session

- **Offline-first**

  - Local SQLite database for offline access
  - Data persisted and queued for next sync

- **CLI-first Design**
  - Colorized menus using Colorama
  - Numbered tables using Tabulate
  - Clear, structured, and intuitive navigation

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/1FahadShah/synqlikk.git
cd synqlikk/cli
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the CLI:

```bash
python main.py
```

---

## Getting Started

On first run, SynQlikk will:

1. Initialize the local database (`db/local_cache.db`) using the schema in `db/schema.sql`.
2. Display the **authentication menu** if no active session exists.
3. Prompt the user to login or register.

---

## Authentication

### Login

```bash
python main.py
```

Select **Login**, then enter:

```text
Username: <your_username>
Password: <your_password>
```

On successful login:

- Local session is saved in `.synqlikk_session.json`
- Automatic full sync of server data to local DB

### Register

Select **Register**, then enter:

```text
Username: <desired_username>
Password: <password>
```

On success:

- User is registered with server
- Session is saved locally
- Full server sync occurs automatically

### Logout

From the main menu:

```
5. Logout / Exit
```

- Automatically syncs final local changes
- Deletes local session file

---

## Main Menu & Features

After authentication, the **main menu** allows access to:

```
1. Tasks
2. Notes
3. Expenses
4. Sync with Server
5. Logout / Exit
```

### Tasks

Manage tasks via CRUD:

| Command     | Description                                                        |
| ----------- | ------------------------------------------------------------------ |
| View Tasks  | Displays all tasks in a numbered table                             |
| Add Task    | Create a new task (`title`, `description`, `due_date`, `priority`) |
| Edit Task   | Modify an existing task                                            |
| Delete Task | Mark a task for deletion (removed on next sync)                    |

**Example: Add Task**

```text
Title: Build MVP
Description: Complete SynQlikk MVP
Due date (YYYY-MM-DD, optional): 2025-09-30
Priority (1=High, 2=Medium, 3=Low) [2]: 1
```

### Notes

Manage personal notes:

| Command     | Description                                 |
| ----------- | ------------------------------------------- |
| View Notes  | Lists all notes with preview (max 60 chars) |
| Add Note    | Create a new note                           |
| Edit Note   | Modify an existing note                     |
| Delete Note | Mark a note for deletion                    |

**Example: Add Note**

```text
Note content: Refactor tasks module to support PostgreSQL
```

### Expenses

Track personal finances:

| Command        | Description                                                               |
| -------------- | ------------------------------------------------------------------------- |
| View Expenses  | Lists expenses in a numbered table                                        |
| Add Expense    | Create a new expense (`amount`, `category`, `date`, optional description) |
| Edit Expense   | Modify an existing expense                                                |
| Delete Expense | Mark an expense as deleted                                                |

**Example: Add Expense**

```text
Amount: 49.99
Category: Software
Date (YYYY-MM-DD): 2025-09-10
Description (optional): VSCode License
```

### Sync with Server

- Two-way sync of **tasks, notes, and expenses**
- Optional **full sync** (`force_full=True`) pulls all server records
- Handles conflicts automatically (server wins)
- Tracks `last_sync_time` in `.synqlikk_session.json`

**Manual Sync Example**

```python
from cli import sync
sync.sync_all()
```

---

## Database

- Local SQLite database: `db/local_cache.db`
- Tables: `tasks`, `notes`, `expenses`
- Schema stored in `db/schema.sql`
- All tables include:

  - `id` (UUID)
  - `user_id`
  - `synced` flag (0=unsynced, 1=synced)
  - `is_deleted` flag (0=active, 1=deleted)
  - `last_modified` timestamp

- Future-proof for PostgreSQL migration

---

## Error Handling

- **APIError**: Network or server API failures
- **AuthenticationError**: Invalid login/registration or session
- **SyncConflictError**: Detected sync conflicts (server version kept)
- CLI provides colorized warnings and error messages

---

## Utilities

- `utils.initialize_local_db()`: Creates DB and applies schema if missing
- `utils.get_db_connection()`: Returns SQLite connection
- `utils.current_timestamp()`: UTC timestamp in ISO 8601 format
- Colorized print helpers: `print_success`, `print_info`, `print_warning`, `print_error`

---

## Example Workflows

### Add a Task, Note, and Expense & Sync

```bash
python main.py
# Login or Register
```

**Tasks**

```
1. Tasks > Add Task
Title: Write README
Due date: 2025-09-11
Priority: 1
```

**Notes**

```
2. Notes > Add Note
Note content: Write detailed README.md for SynQlikk CLI
```

**Expenses**

```
3. Expenses > Add Expense
Amount: 20.0
Category: Software
Date: 2025-09-11
```

**Sync**

```
4. Sync with Server
```

---

## License

[MIT License](LICENSE)

---

**SynQlikk CLI** – Terminal-first productivity, offline-first persistence, and cloud sync. Perfect for personal or professional task, note, and expense management.
