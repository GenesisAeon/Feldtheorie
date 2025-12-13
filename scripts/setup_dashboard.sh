#!/bin/bash
# Dashboard Setup Script
# ======================

set -e

echo "📊 Setting up Aeon Dashboard"
echo "============================="
echo ""

cd dashboard

echo "📦 Installing npm dependencies..."
echo ""

# Install with progress
npm install

echo ""
echo "✅ Dashboard setup complete!"
echo ""
echo "Next steps:"
echo "  1. Start backend: uvicorn api.server:app --reload --port 8000"
echo "  2. Start dashboard: npm run dev (in dashboard/)"
echo "  3. Visit: http://localhost:3000"
echo ""
