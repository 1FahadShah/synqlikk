# SynQlikk: An Offline-First Personal Organizer

**Video Demo:** <YOUR_YOUTUBE_URL_HERE>
<br>
**Live Demo:** https://synqlikk-demo.1fahadshah.com
<br>
**Code:** https://github.com/1FahadShah/harvard-CS50x/tree/main/synqlikk-cs50-final-project

---

## Description

SynQlikk is a robust, offline-first personal organizer designed to manage tasks, notes, and expenses. It was developed as my final project for Harvard's CS50x. The core mission of SynQlikk is to provide a reliable and seamless user experience, regardless of internet connectivity. It achieves this through a unique dual-component architecture: a fast, local Command-Line Interface (CLI) for offline data management, and a full-featured Flask Web Application that provides a graphical user interface and serves as the central server for data synchronization.

The primary problem SynQlikk solves is that of data accessibility and consistency in a world of intermittent connectivity. Many applications fail or provide a degraded experience when offline. SynQlikk is built on the principle that a user should always have access to their critical information. By allowing all create, read, update, and delete (CRUD) operations to happen on a local database via the CLI, a user can continue to be productive anywhere. When a connection is available, a powerful, custom-built sync engine allows the user to reconcile their local changes with the central server in a single, efficient transaction, ensuring their data is consistent across both the web and their local machine.

---

## Key Features

- **Offline-First CLI**: A complete command-line application that works without an internet connection, storing data in a local SQLite database.
- **Web Dashboard**: A full-featured, responsive web interface built with Flask for managing data from any browser.
- **Two-Way Batch Sync**: An efficient, single-endpoint API (`/api/sync`) that handles pushing and pulling all local and server changes in one transaction.
- **Token-Based (JWT) Authentication**: A secure, modern authentication system for the API, ensuring that all client-server communication is protected.
- **User-Friendly CLI**: A polished command-line experience with interactive menus, tabulated data displays, and CRUD operations by sequence number, not database ID.
- **Auto-Sync on Exit**: The CLI automatically saves any unsynced local changes to the server upon logout or exit, preventing data loss.

---

## Architectural Design and Key Decisions

The development of SynQlikk was guided by a "Web/API-First" strategy, a modern approach where the server-side logic and its API are built and finalized before the client application. This ensures a clear and stable contract for the client to interact with and promotes a clean separation of concerns.

Several key architectural decisions were made to ensure the robustness and scalability of the synchronization system:

- **UUIDs for Conflict-Free Sync**: A critical design choice was to use universally unique identifiers (UUIDs) for all primary keys. In an offline-first model where multiple clients can create data independently, using sequential integers would inevitably lead to ID collisions. UUIDs guarantee that every record has a globally unique ID, eliminating this entire class of problems.
- **Two-Way Batch Synchronization**: The sync mechanism is designed for efficiency. Instead of making separate network requests for every single change, the CLI bundles all its local changes into a single JSON payload and sends it to a unified `/api/sync` endpoint. The server processes these changes and, in the same response, sends back a batch of all changes that have occurred on the server since the client's last sync. This single-transaction approach is far more efficient than a "chatty" CRUD API.
- **"Last Write Wins" Conflict Resolution**: To handle cases where a record might be edited on both the web and the CLI while offline, SynQlikk employs a "last write wins" strategy. Every record has a `last_modified` timestamp, generated using timezone-aware UTC. When the server receives a change, it compares timestamps. The record with the newer timestamp is considered the authoritative version, ensuring data consistency.
- **Soft Deletes for Data Integrity**: To ensure that deletions can be synchronized, records are never permanently removed from the database. Instead, they are "soft deleted" by setting an `is_deleted` flag to `1`. This allows a deletion to be treated as a simple update that can be reliably propagated to other clients.
- **SQLite for Simplicity, PostgreSQL for Production**: The project was prototyped and developed using SQLite for its simplicity and file-based nature, which is ideal for the offline cache. The architecture is designed to be seamlessly migrated to a more robust database like PostgreSQL for production deployment on a platform like Render.

---

## File Breakdown

The project is organized into two main application modules, `web` and `cli`, supported by a `db` module.

### `web/` - The Flask Server & API

This package contains the entire server-side application.

- `__init__.py`: The main application factory. It initializes the Flask app, loads configuration, and registers all the different parts of the application (Blueprints).
- `models.py`: The data access layer. This is the only part of the web app that directly communicates with the `server.db` database. It contains all the functions for creating, reading, updating, and deleting records.
- `forms.py`: Defines the web forms for user registration and login using the Flask-WTF library, providing server-side validation and CSRF protection.
- `auth.py`: A Flask Blueprint that handles the routes for the web-based user authentication (e.g., `/login`, `/register`).
- `routes.py`: A Flask Blueprint for the main user-facing pages, such as the dashboard and the dedicated pages for managing tasks, notes, and expenses.
- `sync_api.py`: A Flask Blueprint that exposes the JSON API for the CLI, including the crucial token-based authentication and the unified `/api/sync` endpoint.
- `templates/`: Contains all the Jinja2 HTML templates for the web interface.

### `cli/` - The Command-Line Interface

This package is the offline-first client application.

- `main.py`: The main entry point for the CLI. It contains the main application loop that directs the user to the appropriate menu.
- `menus.py`: Defines the user interface for the CLI, including the main menu and sub-menus for tasks, notes, and expenses.
- `utils.py`: A central utility hub for the CLI. It manages the connection to `local_cache.db` and handles the reading and writing of the `~/.synqlikk/config.json` file.
- `auth.py`: The client-side authentication module. It makes `requests` calls to the server's API to register and log in users and saves the received session token.
- `tasks.py`, `notes.py`, `expenses.py`: These modules contain the local CRUD logic. Each function operates directly on the `local_cache.db` and marks any changes with `synced = 0`.
- `sync.py`: The heart of the CLI's online functionality. The `sync_all()` function gathers all local changes, sends them to the server's `/api/sync` endpoint, and processes the response to update its local cache.

---

## Reflection & Future Vision

This project was an exercise in system design thinking, not just a simple CRUD application. The goal was to build a real system that could handle the complex challenges of data consistency in a distributed, offline-first environment.

This project also marks the first milestone in my personal "AI Systems Builder" roadmap. A solid, reliable data foundation like SynQlikk is the prerequisite for building intelligent systems. The next phase for `synqlikk.1fahadshah.com` will be to evolve it into an AI-native knowledge system, with features like autonomous expense categorization and intelligent task prioritization built on top of this robust sync engine. This was just the rehearsal; the real stage is coming.

---

## AI Usage Citation

For this project, I utilized AI assistants (Google's Gemini and OpenAI's ChatGPT) as a pair-programming partner and a learning tool. The AI was used to accelerate development by generating boilerplate code, providing different architectural perspectives, helping debug complex issues (such as timezone-naive timestamp conflicts and Python import path errors), and refining code to follow best practices. The core architectural decisions and the final implementation were directed and written by me, with the AI acting as a tool to enhance productivity, not to supplant the engineering process, in accordance with CS50's academic honesty policy.
