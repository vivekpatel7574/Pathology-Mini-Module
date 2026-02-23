# Quick Start Guide

Get the Pathology Module running in under 5 minutes with XAMPP MySQL!

## Prerequisites

- XAMPP installed (MySQL server)
- Python 3.9+ installed
- MySQL service running in XAMPP

## 1. Start XAMPP MySQL (30 seconds)

1. Open **XAMPP Control Panel**
2. Click **"Start"** next to **MySQL**
3. Wait for green indicator (running status)

## 2. Install Dependencies (1 minute)

```bash
cd c:\Vivu\Task
pip install -r requirements.txt
```

## 3. Initialize MySQL Database (30 seconds)

```bash
# Create pathology_db database
python setup_mysql.py
```

**Output:**
```
✓ MySQL setup complete!
```

## 4. Create Database Tables (30 seconds)

```bash
# Create all tables
flask --app run init-db
```

## 5. Seed Sample Data (Optional)

```bash
# Add sample tests and orders
flask --app run seed-db
```

## 6. Start the Server (10 seconds)

```bash
python run.py
```

**Output:**
```
🏥 Pathology Module - Starting Flask Application
==================================================
Database: MySQL (XAMPP)
Host: localhost:3306
User: root
Database: pathology_db
URL: http://localhost:5000
==================================================
```

## 7. Open in Browser

Navigate to: **http://localhost:5000**

---

## Test the Complete Workflow (3 minutes)

### Scenario: Order a CBC Test and Complete the Result

#### Step 1: Create a Test (if not already seeded)
- Click **"Tests"** → **"➕ Create New Test"**
- Fill in:
  - Test Code: `CBC`
  - Test Name: `Complete Blood Count`
  - Sample Type: `Blood`
  - Normal Range: `4.5-11.0 (10^9/L)`
  - Price: `50.00`
  - Check: "Active"
- Click **"Create Test"** ✓

#### Step 2: Create an Order
- Click **"Orders"** → **"➕ Create New Order"**
- Fill in:
  - Patient Name: `John Smith`
  - Patient Phone: `+1-555-0101`
  - Select Test: `Complete Blood Count (CBC) - ₹5,000.00`
  - Order Date: Today or future date
- Click **"Create Order"** ✓
- **Status**: Draft | **Order ID**: LTO-1001

#### Step 3: Mark Order as Ready
- Click **"✓ Mark as Ordered"** button
- **Status changes**: Draft → Ordered ✓

#### Step 4: Add a Result
- Click **"➕ Create Result"** button
- Enter:
  - Result Value: `7.5`
  - Technician Notes: `Normal range`
- Click **"Create Result"** ✓
- **Status**: Draft

#### Step 5: Complete the Result
- Click **"✓ Mark as Completed"**
- **Two changes happen automatically**:
  - Result status: Draft → Completed ✓
  - Order status: Ordered → Completed ✓

---

## Testing Validation Rules

### ❌ Test Invalid Scenarios

#### 1. Cannot Create Order in Past
- Go to **"Orders"** → **"Create New Order"**
- Select order_date: Yesterday or earlier
- **Expected Error**: "Order date cannot be in the past" ✓

#### 2. Cannot Create Result on Draft Order
- Create new order (stays in Draft)
- Try to create result: **"➕ Create Result"** button is not visible
- **Expected**: Only Ordered orders allow result creation ✓

#### 3. Cannot Edit Completed Result
- Complete a result (Step 5 above)
- Try to click "Edit Result": **Button disappears** ✓
- **Expected**: Only Draft results are editable ✓

#### 4. Cannot Use Inactive Test
- Create a test and mark as **Inactive**
- Go to **"Create New Order"**
- Try to select it: **Option not available** ✓
- **Expected**: Only active tests appear ✓

#### 5. Duplicate Test Code
- Create test with code: `CBC`
- Try to create another with code: `CBC`
- **Expected Error**: "Test code 'CBC' already exists" ✓

---

## Useful Commands

### Flask Shell (Interactive Testing)
```bash
# Start Flask shell
flask --app run shell

# In the shell:
>>> from app.controllers import *
>>> from app.models import *

# Create a test
>>> test = PathologyTestController.create_test(
...     test_name='Test Name',
...     test_code='TEST',
...     sample_type='Blood',
...     normal_range='0-100',
...     price=100.00
... )

# List tests
>>> PathologyTestController.list_active_tests()

# Create order
>>> order = LabTestOrderController.create_order(
...     patient_name='John',
...     patient_phone='555-0101',
...     test_id=1,
...     order_date='2026-02-24'
... )

# Exit
>>> exit()
```

### Reset Database
```bash
# Drop all tables and recreate
flask --app run shell

>>> from app import db
>>> db.drop_all()
>>> db.create_all()
>>> exit()

# Reinitialize
flask --app run seed-db
```

### View Database with MySQL
```bash
# Method 1: phpMyAdmin (XAMPP built-in)
# Open: http://localhost/phpmyadmin
# Login: root / (no password)
# Browse: pathology_db database

# Method 2: Flask shell
flask --app run shell

>>> from app.models import *
>>> PathologyTest.query.all()
>>> LabTestOrder.query.all()
>>> exit()
```

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| **MySQL not running** | Open XAMPP Control Panel → Click "Start" for MySQL |
| **Port 5000 already in use** | Use different port: `python run.py --port 5001` |
| **Database not found** | Run `python setup_mysql.py` first |
| **Access denied for user 'root'** | XAMPP default password is empty - no password needed |
| **Can't connect to MySQL on localhost:3306** | Start MySQL in XAMPP Control Panel and wait 10 seconds |
| **Module not found** | Run `pip install -r requirements.txt` |
| **Database locked** | Wait 10 seconds or restart server |
| **Templates not found** | Verify `app/templates/` folder exists |
| **404 errors** | Check URL format (e.g., `/orders/1` not `/orders?id=1`) |

---

## Sample Data Created by Seed

Running `flask seed-db` creates:

### Tests
| Code | Name | Sample Type | Price |
|------|------|-------------|-------|
| CBC | Complete Blood Count | Blood | ₹5,000.00 |
| TSH | Thyroid Stimulating Hormone | Serum | ₹7,500.00 |
| FBS | Fasting Blood Sugar | Blood | ₹4,000.00 |
| LIPID | Lipid Profile | Serum | ₹6,000.00 |
| LFT | Liver Function Test | Blood | ₹8,500.00 |

### Orders
| Order ID | Patient | Test | Status |
|----------|---------|------|--------|
| LTO-1001 | John Doe | CBC | Draft |
| LTO-1002 | Jane Smith | TSH | Draft |
| LTO-1003 | Bob Johnson | FBS | Draft |

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│         Browser (Server-Rendered HTML)      │
│              (Jinja2 Templates)             │
└──────────────────┬──────────────────────────┘
                   │ HTTP Requests
                   ▼
┌─────────────────────────────────────────────┐
│      Flask WSGI Application (run.py)        │
│         - Routes (/orders, /tests, etc)     │
│         - Form handling                     │
│         - User feedback (flash messages)    │
└──────────────────┬──────────────────────────┘
                   │ Calls
                   ▼
┌─────────────────────────────────────────────┐
│      Controllers (controllers.py)            │
│    - PathologyTestController                │
│    - LabTestOrderController                 │
│    - LabTestResultController                │
│    ✓ ALL Business logic & validation        │
│    ✓ Status transition control              │
│    ✓ Error handling                         │
└──────────────────┬──────────────────────────┘
                   │ Uses
                   ▼
┌─────────────────────────────────────────────┐
│    SQLAlchemy Models (models.py)            │
│  - PathologyTest (test master)              │
│  - LabTestOrder (orders with workflow)      │
│  - LabTestResult (results)                  │
│  - NamingSeries (auto-ID generation)        │
└──────────────────┬──────────────────────────┘
                   │ Manages
                   ▼
┌─────────────────────────────────────────────┐
│    SQLite / MariaDB / MySQL                 │
│    pathology.db (development)               │
└─────────────────────────────────────────────┘

All business logic at Controller layer ✓
No frontend-driven state changes ✓
Server-side validation only ✓
```

---

## Production Deployment

### Using Gunicorn + Nginx

```bash
# Install production server
pip install gunicorn

# Start with Gunicorn (4 workers)
gunicorn --workers 4 --bind 0.0.0.0:5000 run:app

# With logging
gunicorn --workers 4 --bind 0.0.0.0:5000 --access-logfile - --error-logfile - run:app
```

### Database Configuration
Update `app/__init__.py`:
```python
'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://user:password@db.example.com:3306/pathology'
```

### Security Checklist
- [ ] Change `SECRET_KEY` in config
- [ ] Set `debug=False`
- [ ] Use HTTPS in production
- [ ] Implement authentication (add user login)
- [ ] Add rate limiting
- [ ] Enable CORS properly
- [ ] Use environment variables for secrets

---

## Need Help?

1. **Check README.md** for detailed documentation
2. **Review test scenarios** above
3. **Check error messages** in browser
4. **View Flask logs** in terminal
5. **Inspect database** using sqlite3 or database client

---

**Ready to go! Start with Step 1 and you'll be up and running.** 🚀
