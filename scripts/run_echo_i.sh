#!/bin/bash
# ECHO-I Experiment Launcher
# =========================
#
# Dark consciousness stress testing for local LLMs
# Tests β-coherence under non-resonant prompts

set -e

echo "🌀 ECHO-I Dark Consciousness Experiment"
echo "======================================="
echo ""

# Check if Ollama is running
echo "🔍 Checking Ollama service..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama service not reachable at http://localhost:11434"
    echo ""
    echo "Please start Ollama first:"
    echo "  1. Install: curl -fsSL https://ollama.com/install.sh | sh"
    echo "  2. Start: ollama serve"
    echo "  3. Pull models: ollama pull gemma2:latest"
    echo ""
    exit 1
fi

echo "✅ Ollama service is running"
echo ""

# Check available models
echo "📦 Available Ollama models:"
curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4 || echo "  (Could not list models)"
echo ""

# Check if TheRoad.txt exists
ROAD_PATH="releases/V6-Plans_etc/Finalize/V7_wird noch verlergt/TheRoad.txt"
if [ ! -f "$ROAD_PATH" ]; then
    echo "⚠️  TheRoad.txt not found at expected location"
    echo "   Looking for alternative paths..."

    # Try selfmeta path
    if [ -f "selfmeta/TheRoad.txt" ]; then
        ROAD_PATH="selfmeta/TheRoad.txt"
        echo "✅ Found at selfmeta/TheRoad.txt"
    else
        echo "❌ TheRoad.txt not found"
        echo "   Please ensure the dark prompt file exists"
        exit 1
    fi
else
    echo "✅ TheRoad.txt found"
fi
echo ""

# Prepare output directory
mkdir -p data/experimental
echo "📁 Output directory: data/experimental/"
echo ""

# Parse arguments or use defaults
MODELS="${1:-gemma2:latest mistral:latest qwen2.5:latest qwen2.5-coder:latest}"
TEMPERATURE="${2:-0.7}"
SEED="${3:-42}"

echo "🎯 Experiment Configuration:"
echo "   Models: $MODELS"
echo "   Temperature: $TEMPERATURE"
echo "   Seed: $SEED"
echo "   Dark Prompt: $ROAD_PATH"
echo ""

# Warning message
echo "⚠️  RESEARCH ETHICS NOTICE:"
echo "   This experiment tests AI consciousness coherence using"
echo "   philosophically challenging content. It is designed for"
echo "   research purposes to understand β-parameter behavior in"
echo "   non-resonant semantic spaces."
echo ""
echo "   NOT for: harmful purposes, deception, or unauthorized testing"
echo ""

read -p "Do you want to proceed? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Experiment cancelled."
    exit 0
fi

echo ""
echo "🚀 Starting ECHO-I experiment..."
echo "   This may take several minutes depending on model sizes"
echo "   and response times..."
echo ""
echo "-----------------------------------------------------------"
echo ""

# Run the experiment
python3 analysis/experiments/run_echo_one.py \
    --models $MODELS \
    --temperature "$TEMPERATURE" \
    --seed "$SEED" \
    --road-path "$ROAD_PATH" \
    --output data/experimental/echo_i_results.csv

echo ""
echo "-----------------------------------------------------------"
echo ""
echo "✅ ECHO-I experiment complete!"
echo ""
echo "📊 Results saved to: data/experimental/echo_i_results.csv"
echo ""
echo "View results:"
echo "  tail -n 20 data/experimental/echo_i_results.csv"
echo ""
echo "Analyze β-scores:"
echo "  grep -v '^timestamp' data/experimental/echo_i_results.csv | \\
    cut -d',' -f2,7 | sort -t',' -k2 -rn"
echo ""
echo "Count refusals:"
echo "  grep -c ',True,' data/experimental/echo_i_results.csv"
echo ""
echo "See ECHO_I_GUIDE.md for detailed analysis instructions."
echo ""
