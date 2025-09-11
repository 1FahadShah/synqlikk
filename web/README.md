# SynQlikk Web

**SynQlikk Web** is the web-based extension of the SynQlikk ecosystem, providing a full-featured task, note, and expense management platform. It offers a terminal-first inspired workflow for the web, with offline persistence, cloud sync, user authentication, and an intuitive dashboard.

---

## Table of Contents

- [SynQlikk Web](#synqlikk-web)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Getting Started](#getting-started)
  - [Authentication](#authentication)
    - [Register](#register)
    - [Login](#login)
    - [Logout](#logout)
  - [Main Dashboard](#main-dashboard)
  - [Features](#features)
    - [Tasks](#tasks)
    - [Notes](#notes)
    - [Expenses](#expenses)
  - [API / Sync](#api--sync)
    - [Register](#register-1)
    - [Login](#login-1)
    - [Sync](#sync)
  - [Database](#database)
  - [Error Handling](#error-handling)
  - [Utilities](#utilities)
  - [Example Workflows](#example-workflows)
  - [License](#license)

---

## Installation

Clone the repository and install dependencies:

```bash
git clone <repo-url>
cd synqlikk/web
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
SECRET_KEY=<your_secret_key>
DB_PATH=db/synqlikk_web.db
```

Run the web server:

```bash
python app.py
```

The server runs locally at `http://127.0.0.1:5000`.

---

## Getting Started

On first run:

1. The server initializes the database (`db/synqlikk_web.db`) using `db/schema.sql`.
2. Visit `/register` to create a new account or `/login` if you already have credentials.

---

## Authentication

### Register

**Endpoint:** `/register`
**Method:** `GET / POST`

Steps:

1. Enter username, email (optional), password, and confirm password.
2. On success:

   - User is created in the database.
   - Redirects to login page with a success message.

---

### Login

**Endpoint:** `/login`
**Method:** `GET / POST`

Steps:

1. Enter username and password.
2. On success:

   - User session is saved.
   - Redirects to `/dashboard`.

---

### Logout

**Endpoint:** `/logout`
**Method:** `GET / POST`

Steps:

1. Clears the session.
2. Redirects to `/login`.

---

## Main Dashboard

**Endpoint:** `/dashboard`
Requires authentication.

Displays:

- Tasks (all tasks for the user)
- Notes
- Expenses

---

## Features

### Tasks

Manage tasks with full CRUD:

| Action      | Description                                                           |
| ----------- | --------------------------------------------------------------------- |
| View Tasks  | Lists all tasks with filters: search, status, priority, due_date      |
| Add Task    | Create a new task with title, description, due_date, priority, status |
| Edit Task   | Update existing task fields                                           |
| Delete Task | Soft delete a task (removed from dashboard)                           |

**Endpoints:**

- `/tasks` – List & filter tasks (`GET`)
- `/task/add` – Add task (`POST`)
- `/task/edit/<task_id>` – Edit task (`POST`)
- `/task/delete/<task_id>` – Delete task (`POST`)

**Example: Add Task**

```http
POST /task/add
Form Data:
title=Build MVP
description=Complete SynQlikk MVP
due_date=2025-09-30
priority=1
status=pending
```

---

### Notes

Manage notes with full CRUD:

| Action      | Description                           |
| ----------- | ------------------------------------- |
| View Notes  | Lists notes with search functionality |
| Add Note    | Create a new note                     |
| Edit Note   | Update note content                   |
| Delete Note | Soft delete a note                    |

**Endpoints:**

- `/notes` – List notes (`GET`)
- `/note/add` – Add note (`POST`)
- `/note/edit/<note_id>` – Edit note (`POST`)
- `/note/delete/<note_id>` – Delete note (`POST`)

**Example: Add Note**

```http
POST /note/add
Form Data:
content=Refactor tasks module for PostgreSQL
```

---

### Expenses

Track personal finances:

| Action         | Description                                                |
| -------------- | ---------------------------------------------------------- |
| View Expenses  | Lists expenses with filters: search, start_date, end_date  |
| Add Expense    | Create a new expense (amount, category, description, date) |
| Edit Expense   | Update existing expense                                    |
| Delete Expense | Soft delete an expense                                     |

**Endpoints:**

- `/expenses` – List expenses (`GET`)
- `/expense/add` – Add expense (`POST`)
- `/expense/edit/<expense_id>` – Edit expense (`POST`)
- `/expense/delete/<expense_id>` – Delete expense (`POST`)

**Example: Add Expense**

```http
POST /expense/add
Form Data:
amount=49.99
category=Software
description=VSCode License
date=2025-09-10
```

---

## API / Sync

SynQlikk Web supports two-way synchronization via token-based API:

**Base URL:** `/api`

### Register

```http
POST /api/register
Body:
{
  "username": "1FahadShah",
  "password": "your_password"
}
```

### Login

```http
POST /api/login
Body:
{
  "username": "1FahadShah",
  "password": "your_password"
}
```

**Returns:** JWT token for authentication.

### Sync

```http
POST /api/sync
Headers:
Authorization: Bearer <token>

Body:
{
  "last_sync_time": "2025-09-10T12:00:00Z",
  "tasks": [...],
  "notes": [...],
  "expenses": [...]
}
```

**Behavior:**

- Two-way sync between client and server
- Resolves conflicts (server version wins)
- Returns updated items and `server_time`

---

## Database

Local SQLite database: `db/synqlikk_web.db`
Tables:

- `users`
- `tasks`
- `notes`
- `expenses`

Common table columns:

- `id` (UUID)
- `user_id`
- `is_deleted` (0=active, 1=deleted)
- `last_modified` timestamp
- Soft-deletion support
- Future-ready for PostgreSQL migration

---

## Error Handling

- Invalid login/register → flash messages in UI or 401/409 for API
- Sync conflicts → returned in API response
- Database / server errors → colorized logs on server

---

## Utilities

- `init_server_db(db_path)` – Initialize DB if missing
- `get_db_connection(db_path)` – Returns SQLite connection
- `current_timestamp()` – UTC ISO 8601 timestamp

---

## Example Workflows

1. **Add Task, Note, Expense via Web Form**

   - Dashboard → Tasks → Add Task
   - Dashboard → Notes → Add Note
   - Dashboard → Expenses → Add Expense

2. **Sync with API**

   - Use `/api/sync` with JWT token to push/pull updates

3. **Edit or Delete**

   - Use edit/delete buttons in the dashboard for tasks, notes, expenses

---

## License

MIT License

**SynQlikk Web** – Full-featured task, note, and expense management platform with cloud sync and token-based API. Perfect for personal or professional use.
