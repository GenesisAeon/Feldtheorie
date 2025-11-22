#!/bin/bash

# UTAC Data Harvest - Phase 1 Integration Script
# Automatically validates and integrates 5 new high-priority datasets
# Date: 2025-11-15

echo "🌀 UTAC DATA HARVEST - PHASE 1 INTEGRATION"
echo "==========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "data/raw" ]; then
    echo -e "${RED}❌ Error: Not in utac-data-harvest directory${NC}"
    echo "Please run this script from the utac-data-harvest root directory"
    exit 1
fi

echo "📂 Checking for CSV files..."
echo ""

# Define the CSV files
CSV_FILES=(
    "Vaginal_Microbiome_CST_Transitions.csv"
    "Huntingtons_Disease_CAG_Threshold.csv"
    "AMOC_Paleoclimate_Collapses.csv"
    "ALS_TDP43_Phase_Separation.csv"
    "Oral_Microbiome_Periodontitis.csv"
)

# Counter for successful operations
SUCCESS_COUNT=0
TOTAL_FILES=${#CSV_FILES[@]}

# Process each CSV file
for csv_file in "${CSV_FILES[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Processing: $csv_file"
    echo ""
    
    # Check if file exists in current directory
    if [ ! -f "$csv_file" ]; then
        echo -e "${YELLOW}⚠️  Warning: $csv_file not found in current directory${NC}"
        echo "   Skipping..."
        continue
    fi
    
    # Step 1: Validate CSV format
    echo "🔍 Step 1: Validating CSV format..."
    if python3 tests/test_data_integrity.py --file "$csv_file" 2>/dev/null; then
        echo -e "${GREEN}✅ Validation passed${NC}"
    else
        echo -e "${RED}❌ Validation failed${NC}"
        echo "   Please fix errors before continuing"
        continue
    fi
    
    # Step 2: Copy to data/raw/
    echo "📋 Step 2: Copying to data/raw/..."
    cp "$csv_file" "data/raw/"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Copy successful${NC}"
    else
        echo -e "${RED}❌ Copy failed${NC}"
        continue
    fi
    
    # Step 3: Generate Sigillin metadata
    echo "🏷️  Step 3: Generating Sigillin metadata..."
    python3 scripts/generate_sigillin.py --file "data/raw/$csv_file" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Sigillin metadata generated${NC}"
    else
        echo -e "${RED}❌ Metadata generation failed${NC}"
        continue
    fi
    
    echo -e "${GREEN}✨ $csv_file successfully integrated!${NC}"
    ((SUCCESS_COUNT++))
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 INTEGRATION SUMMARY"
echo "======================"
echo -e "Successfully integrated: ${GREEN}$SUCCESS_COUNT${NC}/$TOTAL_FILES datasets"
echo ""

# Update dashboard if all files successful
if [ $SUCCESS_COUNT -eq $TOTAL_FILES ]; then
    echo "🎉 ALL DATASETS INTEGRATED SUCCESSFULLY!"
    echo ""
    echo "📈 Running dashboard update..."
    python3 scripts/dashboard.py
    echo ""
    echo -e "${GREEN}✅ Phase 1 Integration Complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review generated Sigillin metadata in sigillin/datasets/"
    echo "  2. Commit changes to git repository"
    echo "  3. Begin Phase 2 data collection (see PHASE1_DATASETS_README.md)"
else
    echo -e "${YELLOW}⚠️  Some datasets could not be integrated${NC}"
    echo "Please review errors above and fix issues"
    echo ""
    echo "To retry integration:"
    echo "  ./integrate_phase1.sh"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
