@echo off
REM Pathology Module - Quick Start Script for Windows
REM This script helps with common tasks

setlocal enabledelayedexpansion

:menu
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         PATHOLOGY MODULE - QUICK START MENU                ║
echo ║           MySQL Database via XAMPP                         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 1. Start the Application
echo 2. Create MySQL Database
echo 3. Initialize Database Tables
echo 4. Seed Sample Data
echo 5. Flask Shell (Advanced)
echo 6. Reset Database (Delete All Data)
echo 7. View Documentation
echo 8. Exit
echo.
set /p choice="Select an option (1-8): "

if "%choice%"=="1" goto start_app
if "%choice%"=="2" goto setup_mysql
if "%choice%"=="3" goto init_db
if "%choice%"=="4" goto seed_db
if "%choice%"=="5" goto flask_shell
if "%choice%"=="6" goto reset_db
if "%choice%"=="7" goto docs
if "%choice%"=="8" goto exit
goto menu

:start_app
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║              STARTING PATHOLOGY MODULE                     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Prerequisites:
echo   - XAMPP MySQL server running
echo   - Dependencies installed (pip install -r requirements.txt)
echo.
python run.py
pause
goto menu

:setup_mysql
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║            CREATING MYSQL DATABASE                         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo This will create 'pathology_db' database in XAMPP MySQL.
echo Make sure MySQL is running in XAMPP Control Panel.
echo.
python setup_mysql.py
echo.
pause
goto menu

:init_db
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         INITIALIZING DATABASE TABLES                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Creating tables in pathology_db...
echo.
flask --app run init-db
echo.
pause
goto menu

:seed_db
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          SEEDING SAMPLE DATA                               ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Adding sample tests and orders for demonstration...
echo.
flask --app run seed-db
echo.
pause
goto menu

:flask_shell
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║              FLASK INTERACTIVE SHELL                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Available objects: db, PathologyTest, LabTestOrder, LabTestResult
echo.
echo Examples:
echo   ^> from app.controllers import PathologyTestController
echo   ^> tests = PathologyTestController.list_active_tests()
echo   ^> print(tests)
echo.
echo Type 'exit()' to return to menu
echo.
flask --app run shell
goto menu

:reset_db
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║           RESET DATABASE (DELETE ALL DATA)                 ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo WARNING: This will delete all tests, orders, and results!
echo.
set /p confirm="Are you sure? Type 'yes' to continue: "
if /i "%confirm%"=="yes" (
    echo.
    echo Resetting database...
    python setup_mysql.py
    flask --app run init-db
    flask --app run seed-db
    echo.
    echo ✓ Database reset complete with sample data
) else (
    echo Cancelled.
)
echo.
pause
goto menu

:docs
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║           DOCUMENTATION AVAILABLE                          ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Files:
echo   - QUICKSTART.md              Quick setup guide
echo   - README.md                  Full documentation
echo   - XAMPP_MYSQL_SETUP.md       XAMPP-specific setup
echo   - MYSQL_CONFIG_SUMMARY.md    Configuration details
echo.
echo Opening QUICKSTART.md...
start notepad QUICKSTART.md
timeout /t 2
goto menu

:exit
cls
echo.
echo Thank you for using Pathology Module!
echo.
exit /b 0
