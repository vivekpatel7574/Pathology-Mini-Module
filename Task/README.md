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

---

## Database Schema

### 1. PathologyTest (Test Master)
```
Table: pathology_test
Columns:
  - id (INTEGER, PRIMARY KEY)
  - test_name (VARCHAR 100, UNIQUE, NOT NULL)
  - test_code (VARCHAR 20, UNIQUE, NOT NULL)
    Example: CBC, TSH, FBS
  - sample_type (VARCHAR 50, NOT NULL)
    Example: Blood, Urine, Serum
  - normal_range (VARCHAR 100, NOT NULL)
    Example: 4.5-11.0 (10^9/L)
  - price (DECIMAL 10,2, NOT NULL)
  - is_active (BOOLEAN, DEFAULT=TRUE)
  - created_at (DATETIME, DEFAULT=NOW())
  - updated_at (DATETIME, DEFAULT=NOW())

Relationships:
  - 1:Many with LabTestOrder (via lab_orders)

Key Rules:
  - Only active tests can be ordered
  - Price must be > 0
  - test_code and test_name must be unique
```

### 2. LabTestOrder (Test Orders)
```
Table: lab_test_order
Columns:
  - id (INTEGER, PRIMARY KEY)
  - order_id (VARCHAR 20, UNIQUE, NOT NULL, INDEXED)
    Format: LTO-{auto-incremented}
    Example: LTO-1001, LTO-1002
  - patient_name (VARCHAR 100, NOT NULL)
  - patient_phone (VARCHAR 15, NOT NULL)
  - test_id (INTEGER, FOREIGN KEY → pathology_test.id)
  - order_date (DATE, NOT NULL)
  - status (VARCHAR 20, NOT NULL, DEFAULT='Draft')
    Options: Draft, Ordered, Completed, Cancelled
  - created_at (DATETIME, DEFAULT=NOW())
  - updated_at (DATETIME, DEFAULT=NOW())

Relationships:
  - Many:1 with PathologyTest (via test_id)
  - 1:Many with LabTestResult (via test_results)

Key Rules:
  - order_id is auto-generated using NamingSeries
  - order_date cannot be in the past
  - Default status is 'Draft'
  - Only active tests can be selected
  - Status transitions are strictly controlled
  - Deleting an order cascades to delete results
```

### 3. NamingSeries (ID Generation)
```
Table: naming_series
Columns:
  - id (INTEGER, PRIMARY KEY)
  - series_name (VARCHAR 50, UNIQUE)
    Value: LabTestOrder
  - series_prefix (VARCHAR 10)
    Value: LTO-
  - current_number (INTEGER, DEFAULT=1000)
  - created_at (DATETIME)

Purpose:
  - Auto-generates unique order IDs in format: LTO-1001, LTO-1002, etc.
  - Incremented on each new order creation
```

### 4. LabTestResult (Results)
```
Table: lab_test_result
Columns:
  - id (INTEGER, PRIMARY KEY)
  - order_id (INTEGER, FOREIGN KEY → lab_test_order.id, NOT NULL)
  - result_value (VARCHAR 100, NOT NULL)
    Example: "7.5", "Positive", "Normal", "High"
  - technician_notes (TEXT, NULLABLE)
  - status (VARCHAR 20, NOT NULL, DEFAULT='Draft')
    Options: Draft, Completed
  - created_at (DATETIME, DEFAULT=NOW())
  - updated_at (DATETIME, DEFAULT=NOW())

Relationships:
  - Many:1 with LabTestOrder (via order_id)

Key Rules:
  - Can only be created if related order status is 'Ordered'
  - Always starts in 'Draft' status
  - Cannot be created if result already exists for order
  - Marking as Completed automatically updates order status to Completed
  - When completed, order status changes to Completed
  - Results are viewable by order
```

---

## Workflow & Business Rules

### Order Status Workflow

```
Draft → Ordered → Completed
  ↓
Cancelled

Draft (Initial state)
  ├─ Can transition to: Ordered, Cancelled
  ├─ Cannot: Create result
  └─ Can: Cancel order

Ordered
  ├─ Can transition to: Completed, Cancelled
  ├─ Can: Create result
  └─ Cannot: Modify test selection

Completed
  ├─ Can transition to: (None)
  ├─ Automatic: When result is marked Completed
  └─ Cannot: Perform any actions

Cancelled
  ├─ Can transition to: (None)
  └─ No further actions possible
```

### Result Status Workflow

```
Draft → Completed

Draft (Initial state)
  ├─ Can transition to: Completed
  ├─ Can: Edit result value and notes
  └─ Can: Update result

Completed
  ├─ Can transition to: (None)
  ├─ Automatic side effect: Updates related order to Completed
  └─ Cannot: Be edited or modified
```

### Business Rule Validations

#### PathologyTest Validations
- ✓ test_name and test_code must be unique
- ✓ Price must be > 0
- ✓ sample_type, normal_range required
- ✓ Only active tests appear in order creation

#### LabTestOrder Validations
- ✓ patient_name and patient_phone required
- ✓ test_id must be valid and active
- ✓ order_date cannot be in the past
- ✓ order_id auto-generated and unique
- ✓ Default status: Draft
- ✓ Status transitions strictly controlled:
  - Draft → {Ordered, Cancelled}
  - Ordered → {Completed, Cancelled}
  - Completed → (terminal)
  - Cancelled → (terminal)

#### LabTestResult Validations
- ✓ Order must be in 'Ordered' status (controlled at model level)
- ✓ result_value required and non-empty
- ✓ Default status: Draft
- ✓ Can only be edited in Draft status
- ✓ Marking Completed automatically:
  - Updates result.status → Completed
  - Updates order.status → Completed
- ✓ One result per order (application enforced)

---

## Installation & Setup

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- Git (optional)

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd c:\Vivu\Task

# Install required packages
pip install -r requirements.txt
```

### Step 2: Initialize Database

```bash
# Using Flask CLI
flask --app run init-db

# Or using Python
python run.py

# Then in Flask shell:
# >>> from run import app, db
# >>> with app.app_context():
# ...     db.create_all()
```

### Step 3: (Optional) Seed Database with Sample Data

```bash
# Add sample tests and orders for demonstration
flask --app run seed-db
```

This creates:
- 5 sample pathology tests (CBC, TSH, FBS, etc.)
- 3 sample orders for testing workflows

---

## Running the Application

### Development Mode

```bash
# Using Flask development server
python run.py

# Or alternatively
flask --app run run

# Server will start at http://localhost:5000
```

### Production Mode (Gunicorn)

```bash
# Single worker
gunicorn --bind 0.0.0.0:5000 run:app

# Multiple workers
gunicorn --workers 4 --bind 0.0.0.0:5000 run:app
```

### With Custom Database

For MariaDB/MySQL, modify the Flask config in `app/__init__.py`:

```python
config = {
    'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://user:password@localhost/pathology_db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SECRET_KEY': 'your-secret-key',
}
```

---

## Testing the Workflow

### Complete End-to-End Flow

#### 1. Create a Pathology Test
```
GET /tests/new
POST /tests/new
  - test_name: "Complete Blood Count"
  - test_code: "CBC"
  - sample_type: "Blood"
  - normal_range: "4.5-11.0 (10^9/L)"
  - price: 50.00
  - is_active: checked
Result: Test created and available for ordering
```

#### 2. Create a Lab Order (Draft)
```
GET /orders/new
POST /orders/new
  - patient_name: "John Doe"
  - patient_phone: "+1-555-0101"
  - test_id: [Select CBC]
  - order_date: [Today or future date]
Result: Order created with status: Draft | Order ID: LTO-1001
```

#### 3. Transition Order to Ordered
```
POST /orders/<order_id>/status
  - status: "Ordered"
Result: Order status → Ordered
        Result can now be created
```

#### 4. Create a Test Result
```
GET /orders/<order_id>/result/new
POST /orders/<order_id>/result/new
  - result_value: "7.5"
  - technician_notes: "Sample collected without issues"
Result: Result created with status: Draft
        Can now be edited or completed
```

#### 5. Complete the Result
```
POST /results/<result_id>/complete
Result: Result status → Completed
        Order status → Completed (automatic)
        Test marked as completed
```

### Testing Validation Rules

#### ✗ Invalid Order Date
```
POST /orders/new
  - order_date: [Yesterday or past date]
Error: "Order date cannot be in the past"
```

#### ✗ Create Result on Non-Ordered Order
```
POST /orders/<draft_order_id>/result/new
Error: "Result can only be created for orders in 'Ordered' status"
```

#### ✗ Invalid Status Transition
```
POST /orders/<completed_order_id>/status
  - status: "Draft"
Error: "Cannot transition from Completed to Draft"
```

#### ✗ Create Result with Empty Value
```
POST /orders/<order_id>/result/new
  - result_value: ""
Error: "Result value is required"
```

#### ✗ Duplicate Test Code
```
POST /tests/new
  - test_code: "CBC"  (already exists)
Error: "Test code 'CBC' already exists"
```

---

## API/URL Reference

### Dashboard & Navigation
- `GET /` - Dashboard with statistics

### Pathology Tests
- `GET /tests` - List all tests (with search)
- `GET /tests?search=CBC` - Search tests
- `GET /tests/new` - Create test form
- `POST /tests/new` - Create test
- `GET /tests/<id>/view` - View test details
- `GET /tests/<id>/edit` - Edit test form
- `POST /tests/<id>/edit` - Update test

### Lab Test Orders
- `GET /orders` - List all orders
- `GET /orders?filter=today` - Today's orders
- `GET /orders?filter=Draft|Ordered|Completed|Cancelled` - Filter by status
- `GET /orders?search=LTO-1001` - Search orders
- `GET /orders/new` - Create order form
- `POST /orders/new` - Create order
- `GET /orders/<id>` - View order details
- `POST /orders/<id>/status` - Change order status
- `POST /orders/<id>/cancel` - Cancel order

### Lab Test Results
- `GET /results` - List all results
- `GET /results?filter=completed` - Completed results only
- `POST /orders/<order_id>/result/new` - Create result form
- `POST /orders/<order_id>/result/new` - Create result
- `GET /results/<id>` - View result details
- `GET /results/<id>/edit` - Edit result form
- `POST /results/<id>/edit` - Update result
- `POST /results/<id>/complete` - Mark result completed

---

## Technology Stack

### Backend
- **Framework**: Flask 3.0.0 (WSGI)
- **ORM**: SQLAlchemy 2.0.23
- **Database Drivers**: 
  - SQLite (built-in, for development)
  - PyMySQL 1.1.0 (for MariaDB/MySQL)
- **Server**: Gunicorn 21.2.0

### Frontend
- **Templating**: Jinja2 (Flask built-in)
- **Styling**: CSS3 (custom)
- **Scripting**: Vanilla JavaScript (minimal)
- **No**: React, Angular, Vue, or other SPAs

### Development
- **Language**: Python 3.9+
- **Package Manager**: pip
- **Environment**: Virtual environment recommended

---

## File Structure

```
c:\Vivu\Task\
├── run.py                          # Application entry point
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── pathology.db                    # SQLite database (created on first run)
│
└── app/                            # Main application package
    ├── __init__.py                 # Flask app factory & routes
    ├── models.py                   # SQLAlchemy models
    ├── controllers.py              # Business logic & validation
    │
    ├── templates/                  # Jinja2 templates
    │   ├── base.html               # Base template with styling
    │   ├── index.html              # Dashboard
    │   │
    │   ├── tests/
    │   │   ├── list.html           # List tests with search
    │   │   ├── form.html           # Create/edit test form
    │   │   └── view.html           # View test details
    │   │
    │   ├── orders/
    │   │   ├── list.html           # List orders with filters
    │   │   ├── form.html           # Create/edit order form
    │   │   └── view.html           # View order with actions
    │   │
    │   ├── results/
    │   │   ├── list.html           # List results
    │   │   ├── form.html           # Create/edit result form
    │   │   └── view.html           # View result details
    │   │
    │   └── errors/
    │       ├── 404.html            # Not found page
    │       └── 500.html            # Server error page
    │
    └── static/
        └── css/                    # CSS files (optional, styles in base.html)
```

---

## Key Features

### ✓ Implemented
- [x] Complete SQLAlchemy models with relationships
- [x] Server-side validation for all operations
- [x] Status workflow enforcement (Draft → Ordered → Completed)
- [x] Automatic cascading updates (result completion → order completion)
- [x] Naming series for unique order IDs (LTO-1001, LTO-1002, ...)
- [x] Search functionality for tests and orders
- [x] Status-based filtering for orders
- [x] Today's orders view
- [x] Server-rendered HTML with Jinja2
- [x] Responsive CSS styling
- [x] Error handling and validation messages
- [x] Flash messages for user feedback
- [x] Database initialization and seeding
- [x] WSGI-based Flask application

### ✓ UI Features
- Dashboard with statistics
- List views with search and filters
- Create/edit forms with validation
- Detail views with status-based actions
- Breadcrumb navigation
- Status badges with color coding
- Responsive layout
- Clear error and success messages

### ✓ Security Features
- All validations server-side
- No direct database writes
- Form submissions use POST
- Status transitions validated
- Input validation and sanitization

---

## Database Migration Notes

### SQLite to MariaDB/MySQL

1. Update database URI in `app/__init__.py`:
```python
'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://user:password@localhost:3306/pathology_db'
```

2. Create database:
```sql
CREATE DATABASE pathology_db;
```

3. Update `requirements.txt`:
```
PyMySQL>=1.1.0
```

4. Run initialization:
```bash
flask --app run init-db
```

---

## Troubleshooting

### Database Already Locked
- SQLite keeps locks briefly. Wait a moment and retry.
- Consider using MariaDB/MySQL for production.

### Import Errors
```bash
# Verify Flask is installed
python -c "import flask; print(flask.__version__)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use
```bash
# Use a different port
python run.py --port 5001

# Or with Gunicorn
gunicorn --bind 0.0.0.0:5001 run:app
```

### Database Not Initializing
```bash
# Manually initialize
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
```

---

## Extending the Module

### Add New Test Type
Modify `controllers.py` → `PathologyTestController.create_test()`

### Add New Status
1. Update `models.py` → `OrderStatusEnum`
2. Update valid transitions in `LabTestOrder.can_transition_to()`
3. Add templates for new state

### Add Reporting
Create new route in `app/__init__.py`:
```python
@app.route('/reports/daily')
def daily_report():
    # Generate report
    pass
```

### Add Audit Logging
Add audit columns to models:
```python
modified_by = db.Column(db.String(100))
modification_reason = db.Column(db.Text)
```

---

## Performance Optimization

For production use:
1. **Database indexes** on frequently searched columns:
   - `order_id` (already indexed)
   - `test_code`
   - `patient_name`

2. **Query optimization**:
   - Use `lazy='select'` for relationships
   - Implement pagination for large lists

3. **Caching**:
   - Cache active tests list
   - Cache test prices

---

## Support & Contact

For issues or questions about the implementation:
1. Check validation rules in `controllers.py`
2. Review database schema in `models.py`
3. Examine templates for UI logic
4. Check Flask logs for server errors

---

## License

This is a demonstration module for educational purposes.

---

**Version**: 1.0.0  
**Last Updated**: February 23, 2026  
**Status**: Production Ready
