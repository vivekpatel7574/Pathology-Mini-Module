#!/usr/bin/env python
"""
Pathology Module Application Entry Point
WSGI-based Flask application for pathology test management
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import PathologyTest, LabTestOrder, LabTestResult, NamingSeries

# Create Flask app
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db,
        'PathologyTest': PathologyTest,
        'LabTestOrder': LabTestOrder,
        'LabTestResult': LabTestResult,
        'NamingSeries': NamingSeries,
    }


@app.cli.command()
def init_db():
    """Initialize the database with tables"""
    with app.app_context():
        db.create_all()
        print("✓ Database initialized successfully")


@app.cli.command()
def seed_db():
    """Populate database with sample data for testing"""
    from datetime import datetime, date, timedelta
    from app.controllers import PathologyTestController, LabTestOrderController
    
    with app.app_context():
        # Check if data already exists
        if PathologyTest.query.first():
            print("Database already has data. Skipping seed.")
            return
        
        print("Seeding database with sample data...")
        
        # Create sample tests
        tests_data = [
            {
                'test_name': 'Complete Blood Count',
                'test_code': 'CBC',
                'sample_type': 'Blood',
                'normal_range': '4.5-11.0 (10^9/L)',
                'price': 50.00,
            },
            {
                'test_name': 'Thyroid Stimulating Hormone',
                'test_code': 'TSH',
                'sample_type': 'Serum',
                'normal_range': '0.4-4.0 (mIU/L)',
                'price': 75.00,
            },
            {
                'test_name': 'Fasting Blood Sugar',
                'test_code': 'FBS',
                'sample_type': 'Blood',
                'normal_range': '70-110 (mg/dL)',
                'price': 40.00,
            },
            {
                'test_name': 'Lipid Profile',
                'test_code': 'LIPID',
                'sample_type': 'Serum',
                'normal_range': 'Total: <200 mg/dL',
                'price': 60.00,
            },
            {
                'test_name': 'Liver Function Test',
                'test_code': 'LFT',
                'sample_type': 'Blood',
                'normal_range': 'SGPT: 7-56 U/L',
                'price': 85.00,
            },
        ]
        
        created_tests = []
        for test_data in tests_data:
            try:
                test = PathologyTestController.create_test(**test_data)
                created_tests.append(test)
                print(f"  ✓ Created test: {test.test_name} ({test.test_code})")
            except Exception as e:
                print(f"  ✗ Error creating test: {e}")
        
        # Create sample orders
        if created_tests:
            orders_data = [
                {
                    'patient_name': 'Mr patel',
                    'patient_phone': '+91 9898745612',
                    'test_id': created_tests[0].id,
                    'order_date': date.today(),
                },
                {
                    'patient_name': 'Patel Sir',
                    'patient_phone': '9898255612',
                    'test_id': created_tests[1].id,
                    'order_date': date.today(),
                },
                {
                    'patient_name': 'V',
                    'patient_phone': '9898745625',
                    'test_id': created_tests[2].id,
                    'order_date': date.today() + timedelta(days=1),
                },
            ]
            
            for order_data in orders_data:
                try:
                    order = LabTestOrderController.create_order(**order_data)
                    print(f"  ✓ Created order: {order.order_id}")
                except Exception as e:
                    print(f"  ✗ Error creating order: {e}")
        
        print("✓ Database seeding complete!")


if __name__ == '__main__':
    # For development
    print("🏥 Pathology Module - Starting Flask Application")
    print("=" * 50)
    print("Database: MySQL (XAMPP)")
    print("Host: localhost:3306")
    print("User: root")
    print("Database: pathology_db")
    print("URL: http://localhost:5000")
    print("=" * 50)
    print("\nUseful commands:")
    print("  python setup_mysql.py     Create MySQL database")
    print("  flask init-db              Initialize tables")
    print("  flask seed-db              Seed database with sample data")
    print("=" * 50)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

