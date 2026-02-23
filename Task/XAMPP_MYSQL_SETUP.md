# XAMPP MySQL Setup Guide

## Complete Setup Steps for Pathology Module with XAMPP MySQL

### 1. Start XAMPP MySQL Server

1. Open **XAMPP Control Panel**
2. Click **"Start"** next to **"MySQL"**
3. Wait for it to show as running (green indicator)

**Expected Output:**
```
MySQL: running [PID xxxx] 
```

### 2. Install Python Dependencies

```bash
cd c:\Vivu\Task

# Install all required packages
pip install -r requirements.txt
```

**Packages installed:**
- Flask 3.0.0 - Web framework
- SQLAlchemy 2.0.23 - ORM
- PyMySQL 1.1.0 - MySQL driver for SQLAlchemy
- mysql-connector-python 8.2.0 - Direct MySQL connector
- python-dotenv 1.0.0 - Environment variables
- gunicorn 21.2.0 - Production server

### 3. Create MySQL Database

Run the setup script:

```bash
python setup_mysql.py
```

**Output:**
```
🏥 Pathology Module - MySQL Setup
==================================================
Database: MySQL (XAMPP)
Host: localhost:3306
User: root
==================================================

Creating database 'pathology_db'...
✓ Database created successfully

✓ MySQL setup complete!
Now run: python run.py
```

### 4. Initialize Database Tables

```bash
# Create all tables
flask --app run init-db
```

**Output:**
```
✓ Database initialized successfully
```

### 5. Seed Sample Data (Optional)

```bash
# Add sample tests and orders
flask --app run seed-db
```

**Sample Data Created:**
- 5 pathology tests (CBC, TSH, FBS, LIPID, LFT)
- 3 sample orders
- Ready for immediate testing

### 6. Start the Application

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

Useful commands:
  python setup_mysql.py     Create MySQL database
  flask init-db              Initialize tables
  flask seed-db              Seed database with sample data
==================================================

 * Serving Flask app 'run'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

### 7. Access the Application

Open browser and navigate to:
```
http://localhost:5000
```

---

## Database Configuration

### Connection String
```
mysql+pymysql://root:@localhost:3306/pathology_db
```

### Components:
- **Protocol**: `mysql+pymysql://` (using PyMySQL driver)
- **User**: `root` (XAMPP default)
- **Password**: Empty (XAMPP default)
- **Host**: `localhost`
- **Port**: `3306` (MySQL default)
- **Database**: `pathology_db` (created by setup script)

### File Location
- **Config**: `app/__init__.py` (line 21)
- **Setup Script**: `setup_mysql.py`

---

## Troubleshooting

### ❌ MySQL Server Not Running
```
Error: (2003, "Can't connect to MySQL server on 'localhost:3306'")
```

**Solution:**
1. Open XAMPP Control Panel
2. Click "Start" for MySQL
3. Wait 5-10 seconds for it to start
4. Check for green indicator
5. Retry setup

### ❌ "Access denied for user 'root'@'localhost'"
```
Error: (1045, "Access denied for user 'root'@'localhost'")
```

**Solution:**
1. XAMPP default is: user=`root`, password=``(empty)
2. If you changed the password, update in `app/__init__.py`:
   ```python
   'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/pathology_db'
   ```

### ❌ "Database 'pathology_db' doesn't exist"
```
Error: (1049, "Unknown database 'pathology_db'")
```

**Solution:**
1. Run setup script first:
   ```bash
   python setup_mysql.py
   ```
2. Then initialize tables:
   ```bash
   flask --app run init-db
   ```

### ❌ "No module named 'mysql'"
```
Error: ModuleNotFoundError: No module named 'mysql'
```

**Solution:**
```bash
pip install mysql-connector-python
pip install PyMySQL
```

### ❌ "Port 3306 already in use"
```
Error: Address already in use
```

**Solution:**
1. MySQL is likely already running from previous session
2. Check XAMPP Control Panel - MySQL should show as running
3. You don't need to start it again, just use it

---

## Verifying Database Connection

### Method 1: Using Flask Shell
```bash
# Start Flask shell
flask --app run shell

# In the shell, test the connection:
>>> from app import db
>>> db.engine.execute("SELECT 1")
<sqlalchemy.sql.elements.TextClause object>

# Exit
>>> exit()
```

### Method 2: Using MySQL Workbench
1. Open MySQL Workbench
2. Create new connection:
   - **Connection Name**: Pathology_Dev
   - **Hostname**: localhost
   - **Port**: 3306
   - **Username**: root
   - **Password**: (leave empty)
3. Click "Test Connection"
4. Should say "Connection successful"

### Method 3: Using phpMyAdmin (XAMPP Built-in)
1. Open browser: `http://localhost/phpmyadmin`
2. Login with username: `root` (no password)
3. Left sidebar should show `pathology_db` database
4. Expand it to see tables

---

## Database Tables Structure

### Tables Created:
1. **pathology_test** - Master list of tests
2. **naming_series** - Auto-ID generation for orders
3. **lab_test_order** - Patient test orders
4. **lab_test_result** - Test results

### View Tables:
```bash
# In Flask shell
>>> from app.models import PathologyTest, LabTestOrder, LabTestResult
>>> PathologyTest.query.all()
>>> LabTestOrder.query.all()
>>> LabTestResult.query.all()
```

---

## Managing Data

### Add Sample Tests Manually
```bash
flask --app run shell

>>> from app.controllers import PathologyTestController
>>> test = PathologyTestController.create_test(
...     test_name='My Test',
...     test_code='MYTEST',
...     sample_type='Blood',
...     normal_range='0-100',
...     price=100.00
... )
>>> exit()
```

### Reset Database
```bash
# Delete all data and recreate tables
flask --app run shell

>>> from app import db
>>> db.drop_all()
>>> db.create_all()
>>> exit()

# Re-seed
flask --app run seed-db
```

### Query Database Directly
```bash
# In Flask shell
>>> from app.models import *
>>> 
>>> # Count records
>>> PathologyTest.query.count()
>>> LabTestOrder.query.count()
>>> 
>>> # Get all tests
>>> tests = PathologyTest.query.all()
>>> for test in tests:
...     print(f"{test.test_code}: {test.test_name} - ${test.price}")
>>>
>>> # Filter by status
>>> orders = LabTestOrder.query.filter_by(status='Draft').all()
```

---

## Production Deployment with XAMPP

For local development, XAMPP MySQL is perfect. For production:

1. **Use dedicated MySQL server** (not XAMPP)
2. **Change connection string**:
   ```python
   'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://user:password@prod-host:3306/pathology_db'
   ```
3. **Use Gunicorn** instead of Flask dev server
4. **Enable backups** and monitoring
5. **Use environment variables** for secrets:
   ```python
   import os
   db_uri = os.getenv('DATABASE_URL', 'mysql+pymysql://root:@localhost:3306/pathology_db')
   ```

---

## Quick Checklist

- [ ] XAMPP installed
- [ ] MySQL running (green indicator in XAMPP Control Panel)
- [ ] Python 3.9+ installed
- [ ] `pip install -r requirements.txt`
- [ ] `python setup_mysql.py` (creates database)
- [ ] `flask --app run init-db` (creates tables)
- [ ] `flask --app run seed-db` (adds sample data)
- [ ] `python run.py` (starts server)
- [ ] Open `http://localhost:5000` in browser
- [ ] See dashboard with statistics

---

## Support

If you encounter issues:
1. Check MySQL is running in XAMPP Control Panel
2. Verify phpMyAdmin shows `pathology_db` database
3. Check `requirements.txt` packages are installed
4. Review error messages in Flask console
5. Check firewall not blocking port 3306

---

**Ready to use!** Your Pathology Module is now using MySQL from XAMPP. 🚀
