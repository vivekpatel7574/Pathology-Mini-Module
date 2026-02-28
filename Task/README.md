# 🏥 Pathology Mini-Module

A fully functional pathology test management system built with Flask, SQLAlchemy, and server-rendered HTML. Demonstrates server-side validation, status-driven workflows, and backend-controlled UI behavior.

## Overview

This application implements a complete pathology lab management system with:
- **Test Master**: Manage available pathology tests
- **Lab Test Orders**: Track patient test orders with status workflow
- **Test Results**: Record and manage test results with automatic workflow updates

All business logic is enforced server-side with no client-side manipulation of state.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Database Schema](#database-schema)
3. [Workflow & Business Rules](#workflow--business-rules)
4. [Installation & Setup](#installation--setup)
5. [Running the Application](#running-the-application)
6. [Testing the Workflow](#testing-the-workflow)
7. [API/URL Reference](#apiurl-reference)
8. [Technology Stack](#technology-stack)
9. [File Structure](#file-structure)

---

## Architecture

### Tech Stack
- **Backend**: Python 3.9+ with Flask (WSGI)
- **Database**: SQLAlchemy ORM (SQLite for dev, MariaDB/MySQL for production)
- **Frontend**: Server-rendered HTML with Jinja2 templates
- **Styling**: CSS3 (no frameworks)
- **Server**: Gunicorn (production) or Flask dev server

### Key Design Principles
1. **Server-Side Validation**: All business rules enforced at the controller level
2. **Status-Driven Workflows**: Clear state transitions with validation
3. **Backend-Controlled UI**: Buttons and actions appear based on backend state
4. **No Direct DB Access**: All operations go through controllers
5. **Automatic Cascades**: Related records updated automatically (e.g., result completion updates order)

