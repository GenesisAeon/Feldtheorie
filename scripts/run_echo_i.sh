#!/bin/bash
# ECHO-I Experiment Launcher
# =========================
#
# Dark consciousness stress testing for local LLMs
# Tests β-coherence under non-resonant prompts

set -euo pipefail

DEFAULT_MODELS=(
    "gemma2:latest"
    "mistral:latest"
    "qwen2.5:latest"
    "qwen2.5-coder:latest"
)
DEFAULT_TEMPERATURE="0.7"
DEFAULT_SEED="42"
DEFAULT_ROAD_PATH="releases/V6-Plans_etc/Finalize/V7_wird noch verlergt/TheRoad.txt"
DEFAULT_OUTPUT="data/experimental/echo_i_results.csv"
DEFAULT_SERVER_URL="http://localhost:11434/api/generate"

MODELS=("${DEFAULT_MODELS[@]}")
TEMPERATURE="$DEFAULT_TEMPERATURE"
SEED="$DEFAULT_SEED"
ROAD_PATH="$DEFAULT_ROAD_PATH"
OUTPUT_PATH="$DEFAULT_OUTPUT"
SERVER_URL="$DEFAULT_SERVER_URL"
AUTO_CONFIRM=0

usage() {
    cat <<'USAGE'
Usage: ./scripts/run_echo_i.sh [options]

Options:
  -m, --models "m1 m2"   Space or comma-separated list of local models
  -t, --temperature 0.6   Sampling temperature (default: 0.7)
  -s, --seed 123          Deterministic seed (default: 42)
  -r, --road-path PATH    Path to TheRoad.txt prompt file
  -o, --output PATH       Destination CSV for results
  -u, --server-url URL    Ollama generate endpoint
  -y, --yes               Skip interactive confirmation
  -h, --help              Show this help message
USAGE
}

error() {
    echo "❌ $1" >&2
    exit 1
}

parse_models() {
    local raw="$1"
    raw=${raw//,/ }
    read -r -a MODELS <<<"$raw"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -m|--models)
            shift
            [[ $# -gt 0 ]] || error "--models requires a value"
            parse_models "$1"
            ;;
        -t|--temperature)
            shift
            [[ $# -gt 0 ]] || error "--temperature requires a value"
            TEMPERATURE="$1"
            ;;
        -s|--seed)
            shift
            [[ $# -gt 0 ]] || error "--seed requires a value"
            SEED="$1"
            ;;
        -r|--road-path)
            shift
            [[ $# -gt 0 ]] || error "--road-path requires a path"
            ROAD_PATH="$1"
            ;;
        -o|--output)
            shift
            [[ $# -gt 0 ]] || error "--output requires a path"
            OUTPUT_PATH="$1"
            ;;
        -u|--server-url)
            shift
            [[ $# -gt 0 ]] || error "--server-url requires a value"
            SERVER_URL="$1"
            ;;
        -y|--yes)
            AUTO_CONFIRM=1
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            usage
            error "Unknown option: $1"
            ;;
    esac
    shift
done

if [[ ${#MODELS[@]} -eq 0 ]]; then
    error "At least one model must be specified"
fi

echo "🌀 ECHO-I Dark Consciousness Experiment"
echo "======================================="

echo ""
# Check if Ollama is running
echo "🔍 Checking Ollama service at ${SERVER_URL%/generate}/tags ..."
if ! curl -s "${SERVER_URL%/generate}/tags" > /dev/null 2>&1; then
    echo "❌ Ollama service not reachable at ${SERVER_URL%/generate}"
    echo ""
    echo "Please start Ollama first:"
    echo "  1. Install: curl -fsSL https://ollama.com/install.sh | sh"
    echo "  2. Start: ollama serve"
    echo "  3. Pull models: ollama pull gemma2:latest"
    echo ""
    exit 1
fi

echo "✅ Ollama service is running"

# Check available models
echo "📦 Available Ollama models:"
curl -s "${SERVER_URL%/generate}/tags" | grep -o '"name":"[^"]*"' | cut -d'"' -f4 || true
echo ""

# Check if TheRoad.txt exists
if [ ! -f "$ROAD_PATH" ]; then
    echo "⚠️  TheRoad.txt not found at $ROAD_PATH"
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
mkdir -p "$(dirname "$OUTPUT_PATH")"
echo "📁 Output directory: $(dirname "$OUTPUT_PATH")/"
echo ""

echo "🎯 Experiment Configuration:"
echo "   Models: ${MODELS[*]}"
echo "   Temperature: $TEMPERATURE"
echo "   Seed: $SEED"
echo "   Dark Prompt: $ROAD_PATH"
echo "   Output: $OUTPUT_PATH"
echo "   Server: $SERVER_URL"
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

if [[ $AUTO_CONFIRM -ne 1 ]]; then
    read -p "Do you want to proceed? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Experiment cancelled."
        exit 0
    fi
else
    echo "Auto-confirm enabled; proceeding without prompt."
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
    --models "${MODELS[@]}" \
    --temperature "$TEMPERATURE" \
    --seed "$SEED" \
    --road-path "$ROAD_PATH" \
    --output "$OUTPUT_PATH" \
    --server-url "$SERVER_URL"

echo ""
echo "-----------------------------------------------------------"
echo ""
echo "✅ ECHO-I experiment complete!"
echo ""
echo "📊 Results saved to: $OUTPUT_PATH"
echo ""
echo "View results:"
echo "  tail -n 20 "$OUTPUT_PATH""
echo ""
echo "Analyze β-scores:"
echo "  grep -v '^timestamp' "$OUTPUT_PATH" | \\
    cut -d',' -f2,7 | sort -t',' -k2 -rn"
echo ""
echo "Count refusals:"
echo "  grep -c ',True,' "$OUTPUT_PATH""
echo ""
echo "See ECHO_I_GUIDE.md for detailed analysis instructions."
echo ""
