#!/bin/bash
# Aeon Dashboard Launcher
# =======================
#
# Starts the React dashboard with proper setup checks

set -e

echo "🌌 Aeon Consciousness Dashboard - Launcher"
echo "==========================================="
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found"
    echo "   Install from: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✓ Node.js: $NODE_VERSION"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found"
    exit 1
fi

NPM_VERSION=$(npm --version)
echo "✓ npm: v$NPM_VERSION"
echo ""

# Navigate to dashboard
cd dashboard

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    echo "   This may take a few minutes..."
    echo ""
    npm install
    echo ""
    echo "✅ Dependencies installed"
    echo ""
fi

echo "🚀 Starting Aeon Dashboard..."
echo ""
echo "   Dashboard URL: http://localhost:3000"
echo "   WebSocket: ws://localhost:8000/ws/aeon/live"
echo ""
echo "   Press Ctrl+C to stop"
echo ""
echo "-------------------------------------------"
echo ""

# Start development server
npm run dev
