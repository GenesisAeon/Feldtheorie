#!/bin/bash
# UTAC Data Harvest - Automated Setup Script
# Run this after downloading all files to automatically organize them

echo "🌀 UTAC DATA HARVEST - AUTOMATED SETUP"
echo "======================================"
echo ""

# Create directory structure
echo "📂 Creating directory structure..."
mkdir -p utac-data-harvest/data/raw
mkdir -p utac-data-harvest/sigillin/datasets
mkdir -p utac-data-harvest/scripts
mkdir -p utac-data-harvest/tests

# Move CSV files
echo "📊 Moving CSV datasets..."
mv 01_*.csv utac-data-harvest/data/raw/ 2>/dev/null
mv 02_*.csv utac-data-harvest/data/raw/ 2>/dev/null
mv 03_*.csv utac-data-harvest/data/raw/ 2>/dev/null
mv 04_*.csv utac-data-harvest/data/raw/ 2>/dev/null
mv 05_*.csv utac-data-harvest/data/raw/ 2>/dev/null

# Move scripts
echo "🛠️  Moving Python scripts..."
mv generate_sigillin.py utac-data-harvest/scripts/ 2>/dev/null
mv dashboard.py utac-data-harvest/scripts/ 2>/dev/null
mv test_data_integrity.py utac-data-harvest/tests/ 2>/dev/null

# Move documentation
echo "📄 Moving documentation..."
mv README_UTAC_Data_Harvest.md utac-data-harvest/README.md 2>/dev/null
mv UTAC_DATA_HARVEST_SUMMARY.md utac-data-harvest/ 2>/dev/null
mv QUICK_START.md utac-data-harvest/ 2>/dev/null

# Create requirements.txt
echo "📝 Creating requirements.txt..."
echo "pyyaml>=6.0" > utac-data-harvest/requirements.txt

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x utac-data-harvest/scripts/*.py 2>/dev/null
chmod +x utac-data-harvest/tests/*.py 2>/dev/null

# Enter directory
cd utac-data-harvest

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Dataset Summary:"
ls -1 data/raw/*.csv 2>/dev/null | wc -l | xargs echo "   Datasets:"
echo ""
echo "🚀 Next Steps:"
echo "   1. Install dependencies:  pip install -r requirements.txt"
echo "   2. Validate data:         python3 tests/test_data_integrity.py --all"
echo "   3. Generate metadata:     python3 scripts/generate_sigillin.py --all"
echo "   4. View dashboard:        python3 scripts/dashboard.py"
echo ""
echo "📖 Read QUICK_START.md for detailed instructions"
echo ""
echo "🌀 Happy data harvesting!"
