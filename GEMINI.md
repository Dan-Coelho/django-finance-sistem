# Gemini Context: Finanpy Project

This document provides a comprehensive overview of the Finanpy project to serve as a context for AI-assisted development.

## 1. Project Overview

Finanpy is a full-stack web application for personal finance management. It is built with Python and Django, following a modular architecture. The frontend is rendered using Django Template Language (DTL) and styled with TailwindCSS.

- **Project Name:** Finanpy
- **Backend:** Python, Django
- **Database:** SQLite
- **Frontend:** Django Template Language (DTL), TailwindCSS
- **Package Management:** `uv`

The application allows users to manage their personal finances by tracking transactions (revenues and expenses) across different accounts and categories.

### Architecture

The project follows a standard Django modular structure, where functionality is separated into distinct "apps":

- `app`: Main project configuration (settings, root URL configuration).
- `users`: Handles user creation, authentication, and management.
- `profiles`: Manages user profile data.
- `accounts`: Manages financial accounts (e.g., bank accounts, wallets).
- `categories`: Manages transaction categories.
- `transactions`: Manages the financial transactions themselves.

The project also includes a `docs` directory containing detailed documentation, and a `prd.md` file which is the Product Requirement Document, outlining the project's vision, features, and technical details.

## 2. Building and Running

The following are the essential commands for setting up and running the project locally.

1.  **Set up the virtual environment:**
    *   Create the environment: `uv venv`
    *   Activate the environment:
        *   Linux/macOS: `source .venv/bin/activate`
        *   Windows: `.venv\Scripts\activate`

2.  **Install dependencies:**
    ```bash
    uv sync
    ```

3.  **Prepare the database:**
    ```bash
    python manage.py migrate
    ```

4.  **Create an administrator user:**
    ```bash
    python manage.py createsuperuser
    ```

5.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

The application will be available at `http://127.0.0.1:8000/`.

## 3. Development Conventions

To ensure code quality and consistency, the project adheres to the following conventions.

- **Linter & Formatter:** `ruff` is used for both linting and formatting.
- **Code Style:** The codebase follows the PEP 8 style guide and principles of Clean Code.
- **Language:** All code (variables, functions, comments) is written in English. The user-facing interface is in Portuguese.
- **Logging:** A structured logging system is configured to track application events and errors.
- **Testing:** (TODO: Test framework and execution commands are not yet defined, but tests are expected to be created for new features and bug fixes).
