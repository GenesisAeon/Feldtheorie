@echo off
REM UTAC Data Harvest - Automated Setup Script (Windows)
REM Run this after downloading all files to automatically organize them

echo.
echo UTAC DATA HARVEST - AUTOMATED SETUP
echo ======================================
echo.

REM Create directory structure
echo Creating directory structure...
mkdir utac-data-harvest\data\raw 2>nul
mkdir utac-data-harvest\sigillin\datasets 2>nul
mkdir utac-data-harvest\scripts 2>nul
mkdir utac-data-harvest\tests 2>nul

REM Move CSV files
echo Moving CSV datasets...
move 01_*.csv utac-data-harvest\data\raw\ >nul 2>&1
move 02_*.csv utac-data-harvest\data\raw\ >nul 2>&1
move 03_*.csv utac-data-harvest\data\raw\ >nul 2>&1
move 04_*.csv utac-data-harvest\data\raw\ >nul 2>&1
move 05_*.csv utac-data-harvest\data\raw\ >nul 2>&1

REM Move scripts
echo Moving Python scripts...
move generate_sigillin.py utac-data-harvest\scripts\ >nul 2>&1
move dashboard.py utac-data-harvest\scripts\ >nul 2>&1
move test_data_integrity.py utac-data-harvest\tests\ >nul 2>&1

REM Move documentation
echo Moving documentation...
move README_UTAC_Data_Harvest.md utac-data-harvest\README.md >nul 2>&1
move UTAC_DATA_HARVEST_SUMMARY.md utac-data-harvest\ >nul 2>&1
move QUICK_START.md utac-data-harvest\ >nul 2>&1

REM Create requirements.txt
echo Creating requirements.txt...
echo pyyaml^>=6.0 > utac-data-harvest\requirements.txt

REM Enter directory
cd utac-data-harvest

echo.
echo Setup complete!
echo.
echo Dataset Summary:
dir /b data\raw\*.csv 2>nul | find /c /v "" 
echo.
echo Next Steps:
echo    1. Install dependencies:  pip install -r requirements.txt
echo    2. Validate data:         python tests\test_data_integrity.py --all
echo    3. Generate metadata:     python scripts\generate_sigillin.py --all
echo    4. View dashboard:        python scripts\dashboard.py
echo.
echo Read QUICK_START.md for detailed instructions
echo.
echo Happy data harvesting!
echo.
pause
