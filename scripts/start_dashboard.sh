#!/bin/bash
# Aeon Dashboard Launcher
# =======================
#
# Starts the React dashboard with proper setup checks

set -euo pipefail

# Allow host/port overrides for container and remote debugging contexts
DASHBOARD_HOST=${DASHBOARD_HOST:-0.0.0.0}
DASHBOARD_PORT=${DASHBOARD_PORT:-3000}

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)

cd "$PROJECT_ROOT"
if [ ! -f "dashboard/package.json" ]; then
    echo "❌ Dashboard package.json not found (expected at $PROJECT_ROOT/dashboard/package.json)"
    echo "   Ensure you are running within the Feldtheorie repository."
    exit 1
fi

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
echo "   Dashboard URL: http://${DASHBOARD_HOST}:${DASHBOARD_PORT}"
echo "   WebSocket: ws://${DASHBOARD_HOST}:8000/ws/aeon/live"
echo ""
echo "   Press Ctrl+C to stop"
echo ""
echo "-------------------------------------------"
echo ""

# Start development server
npm run dev -- --host "${DASHBOARD_HOST}" --port "${DASHBOARD_PORT}"
