# 🏥 Pathology Lab Management System

A complete, production-ready web application for managing pathology tests, lab orders, and test results using Flask, SQLAlchemy, and MySQL.

## 📋 Features

- **Test Management**: Create and manage pathology tests with detailed information
- **Order Workflow**: Create patient orders with automatic ID generation (LTO-1001, LTO-1002, etc.)
- **Status-Driven Workflow**: 
  - Orders: Draft → Ordered → Completed (with cancellation at any point)
  - Results: Draft → Completed
- **Server-Side Validation**: 20+ validation rules enforced on the backend
- **Responsive UI**: Server-rendered HTML with CSS styling
- **Auto-ID Generation**: Unique order IDs generated automatically
- **Cascading Updates**: Result completion automatically updates order status
- **Search & Filter**: Quick search for tests, orders, and results

## 🛠️ Technology Stack

**Backend:**
- Flask 3.0.0 (WSGI Web Framework)
- SQLAlchemy 2.0.23 (ORM)
- Python 3.9+

**Database:**
- MySQL 5.7+ (via XAMPP)
- PyMySQL 1.1.0 (SQLAlchemy driver)

**Frontend:**
- Jinja2 (Server-side templating)
- CSS3 (Responsive styling)
- Vanilla JavaScript (minimal)

## 📁 Project Structure

```
pathology-module/
├── app/
│   ├── __init__.py              # Flask app & 50+ routes
│   ├── models.py                # SQLAlchemy ORM models
│   ├── controllers.py           # Business logic & validation
│   └── templates/               # 15 HTML templates
│       ├── base.html
│       ├── index.html
│       ├── tests/
│       ├── orders/
│       ├── results/
│       └── errors/
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
├── setup_mysql.py               # Database setup script
├── start.bat                    # Windows batch menu
└── README.md                    # Full documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- MySQL 5.7+ (XAMPP recommended)
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pathology-module.git
   cd pathology-module
   ```

2. **Create virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start MySQL** (XAMPP)
   - Open XAMPP Control Panel
   - Click "Start" for MySQL
   - Wait for green indicator

5. **Create database**
   ```bash
   python setup_mysql.py
   ```

6. **Initialize tables**
   ```bash
   flask --app run init-db
   ```

7. **Seed sample data** (optional)
   ```bash
   flask --app run seed-db
   ```

8. **Start the application**
   ```bash
   python run.py
   ```

9. **Open in browser**
   ```
   http://localhost:5000
   ```

## 📊 Database Schema

### Tables

**pathology_test**
- id (PK)
- test_name: Test name
- test_code: Unique code (e.g., CBC, TSH)
- sample_type: Type of sample (Blood, Urine, etc.)
- normal_range: Expected normal value
- price: Test cost in INR
- is_active: Active/Inactive status

**lab_test_order**
- id (PK)
- order_id: Unique order ID (LTO-1001, etc.)
- test_id (FK)
- patient_name: Patient name
- patient_phone: Contact number
- order_date: Date of order
- status: Draft/Ordered/Completed/Cancelled
- created_at, updated_at

**lab_test_result**
- id (PK)
- order_id (FK)
- result_value: Test result
- technician_notes: Additional notes
- status: Draft/Completed
- created_at, updated_at

**naming_series**
- series: Series code (LTO)
- next_number: Next auto-increment value

## 🔄 Workflow Example

1. **Create Test** → Test master data (e.g., Blood Group test)
2. **Create Order** → Patient requests test (Order ID: LTO-1001)
3. **Mark as Ordered** → Prepare for test collection
4. **Create Result** → Enter test result
5. **Complete Result** → Mark result as complete
   - *Automatic: Order status updates to Completed*

## ✅ Validation Rules

- Test must be active to create orders
- Order date cannot be in the past
- Results can only be created for "Ordered" orders
- Status transitions strictly controlled (no skipping)
- Only Draft results can be edited
- All validation is server-side only

## 🔐 Security Features

- Server-side validation (not client-side)
- SQL injection protection via SQLAlchemy ORM
- Status control enforced by backend
- Foreign key constraints
- Unique constraints on IDs

## 📚 Documentation

- **00_START_HERE.txt** - Quick reference guide
- **QUICKSTART.md** - 5-minute setup guide
- **README.md** - Complete documentation
- **XAMPP_MYSQL_SETUP.md** - MySQL troubleshooting

## 🐛 Troubleshooting

**MySQL Connection Failed**
- Ensure XAMPP MySQL is running
- Check host is localhost:3306
- Verify user is "root" with no password

**Port 5000 Already in Use**
- Change port in `run.py`
- Or kill process: `lsof -ti:5000 | xargs kill`

**Templates Not Found**
- Ensure Flask app paths are correct
- Clear browser cache and restart Flask

## 🚀 Deployment

**Development:** Flask development server (included)

**Production:** Use Gunicorn + Nginx
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

**Cloud Platforms:** Heroku, AWS, DigitalOcean, Docker

## 📝 Environment Configuration

Create a `.env` file (optional):
```
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=mysql+pymysql://root:@localhost:3306/pathology_db
```

## 📊 Statistics

- **Python Code**: 900+ lines
- **HTML Templates**: 15 files
- **CSS Styling**: 600+ lines
- **Flask Routes**: 50+
- **Validation Rules**: 20+
- **Database Tables**: 4
- **Setup Time**: ~5 minutes

## 📖 API Endpoints

### Tests
- `GET /tests` - List all tests
- `GET /tests/list` - List active tests
- `POST /tests/new` - Create test
- `GET /tests/<id>/view` - View test
- `POST /tests/<id>/edit` - Edit test

### Orders
- `GET /orders` - List all orders
- `POST /orders/new` - Create order
- `GET /orders/<id>/view` - View order
- `POST /orders/<id>/mark-ordered` - Mark as ordered
- `POST /orders/<id>/cancel` - Cancel order

### Results
- `GET /results` - List all results
- `GET /results/<id>/view` - View result
- `POST /results/new` - Create result
- `POST /results/<id>/edit` - Edit result
- `POST /results/<id>/complete` - Complete result

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add YourFeature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

Built with ❤️ for healthcare lab management.

## 🆘 Support

For issues and questions:
1. Check the documentation files
2. Review XAMPP_MYSQL_SETUP.md for MySQL issues
3. Open an issue on GitHub

---

**Status:** ✅ Production Ready  
**Version:** 1.0.0  
**Last Updated:** February 23, 2026

🏥 **Happy Testing!**
