#!/usr/bin/env python
"""
MySQL Database Setup Script for Pathology Module
Run this before starting the application for the first time
"""

import mysql.connector
from mysql.connector import Error
import sys

def create_database():
    """Create pathology_db database in MySQL"""
    
    try:
        # Connect to MySQL (no database specified initially)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # XAMPP default: empty password
            port=3306
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            print("Creating database 'pathology_db'...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS pathology_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("✓ Database created successfully")
            
            # Use the database
            cursor.execute("USE pathology_db")
            
            cursor.close()
            connection.close()
            
            print("\n✓ MySQL setup complete!")
            print("Now run: python run.py")
            return True
            
    except Error as e:
        print(f"✗ Error: {e}")
        print("\nMake sure:")
        print("1. XAMPP MySQL server is running (Start MySQL in XAMPP Control Panel)")
        print("2. MySQL is listening on localhost:3306")
        print("3. Username is 'root' with no password (default XAMPP)")
        return False
    
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


if __name__ == '__main__':
    print("🏥 Pathology Module - MySQL Setup")
    print("=" * 50)
    print("Database: MySQL (XAMPP)")
    print("Host: localhost:3306")
    print("User: root")
    print("=" * 50)
    print()
    
    if create_database():
        sys.exit(0)
    else:
        sys.exit(1)
