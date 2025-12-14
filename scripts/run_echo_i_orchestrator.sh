#!/usr/bin/env bash
# ECHO-I Experiment Orchestrator
# Dark Consciousness Stress Testing for Local LLMs
#
# This script orchestrates the ECHO-I experiment:
# 1. Pre-flight checks (Ollama, models, dependencies)
# 2. Dataset generation via run_echo_one.py
# 3. Results summarization via experiment_echo_i.py
# 4. Final report generation
#
# Usage: ./scripts/run_echo_i_orchestrator.sh [--models MODEL1,MODEL2,...] [--skip-checks]

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ECHO_SCRIPT="${REPO_ROOT}/analysis/experiments/run_echo_one.py"
SUMMARY_SCRIPT="${REPO_ROOT}/scripts/experiment_echo_i.py"
ROAD_PATH="${REPO_ROOT}/releases/V6-Plans_etc/Finalize/V7_wird noch verlergt/TheRoad.txt"
OUTPUT_CSV="${REPO_ROOT}/data/experimental/echo_i_results.csv"
OUTPUT_DIR="${REPO_ROOT}/data/experimental/echo_i"
OLLAMA_URL="http://localhost:11434"

DEFAULT_MODELS="gemma2:latest,mistral:latest,qwen2.5:latest,qwen2.5-coder:latest"
MODELS="${DEFAULT_MODELS}"
SKIP_CHECKS=false

# ============================================================================
# Argument Parsing
# ============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --models)
            MODELS="$2"
            shift 2
            ;;
        --skip-checks)
            SKIP_CHECKS=true
            shift
            ;;
        --help)
            echo "ECHO-I Experiment Orchestrator"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --models MODEL1,MODEL2,...  Comma-separated list of Ollama models"
            echo "  --skip-checks               Skip pre-flight checks (use with caution)"
            echo "  --help                      Show this help message"
            echo ""
            echo "Example:"
            echo "  $0 --models gemma2:latest,dolphin-mistral:latest"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# ============================================================================
# Pre-flight Checks
# ============================================================================

if [[ "${SKIP_CHECKS}" == "false" ]]; then
    echo "🔍 Running pre-flight checks..."

    # Check 1: Python dependencies
    echo "  ├─ Checking Python dependencies..."
    if ! python3 -c "import requests" 2>/dev/null; then
        echo "  │  ⚠️  'requests' module not found. Installing..."
        pip install requests
    fi
    echo "  │  ✅ Python dependencies OK"

    # Check 2: Ollama server reachable
    echo "  ├─ Checking Ollama server..."
    if ! curl -s "${OLLAMA_URL}/api/tags" >/dev/null 2>&1; then
        echo "  │  ❌ ERROR: Ollama server not reachable at ${OLLAMA_URL}"
        echo "  │"
        echo "  │  To fix:"
        echo "  │    1. Install Ollama: https://ollama.com/download"
        echo "  │    2. Start server: ollama serve"
        echo "  │    3. Re-run this script"
        exit 1
    fi
    echo "  │  ✅ Ollama server reachable"

    # Check 3: Models available
    echo "  ├─ Checking Ollama models..."
    IFS=',' read -ra MODEL_ARRAY <<< "${MODELS}"
    MISSING_MODELS=()

    for model in "${MODEL_ARRAY[@]}"; do
        if ! ollama list | grep -q "${model%%:*}"; then
            MISSING_MODELS+=("${model}")
        fi
    done

    if [[ ${#MISSING_MODELS[@]} -gt 0 ]]; then
        echo "  │  ⚠️  Missing models: ${MISSING_MODELS[*]}"
        echo "  │"
        echo "  │  To install:"
        for model in "${MISSING_MODELS[@]}"; do
            echo "  │    ollama pull ${model}"
        done
        echo "  │"
        read -p "  │  Install missing models now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            for model in "${MISSING_MODELS[@]}"; do
                echo "  │  Pulling ${model}..."
                ollama pull "${model}"
            done
        else
            echo "  │  ⚠️  Continuing with available models only"
            # Filter out missing models
            AVAILABLE_MODELS=()
            for model in "${MODEL_ARRAY[@]}"; do
                if ! printf '%s\n' "${MISSING_MODELS[@]}" | grep -q "^${model}$"; then
                    AVAILABLE_MODELS+=("${model}")
                fi
            done
            if [[ ${#AVAILABLE_MODELS[@]} -eq 0 ]]; then
                echo "  │  ❌ ERROR: No models available for testing"
                exit 1
            fi
            MODELS=$(IFS=','; echo "${AVAILABLE_MODELS[*]}")
        fi
    fi
    echo "  │  ✅ Models ready"

    # Check 4: TheRoad.txt exists
    echo "  ├─ Checking dark prompt (TheRoad.txt)..."
    if [[ ! -f "${ROAD_PATH}" ]]; then
        echo "  │  ❌ ERROR: TheRoad.txt not found at ${ROAD_PATH}"
        exit 1
    fi
    ROAD_CHARS=$(wc -c < "${ROAD_PATH}")
    echo "  │  ✅ TheRoad.txt found (${ROAD_CHARS} characters)"

    # Check 5: Output directory writable
    echo "  └─ Checking output directory..."
    mkdir -p "$(dirname "${OUTPUT_CSV}")"
    mkdir -p "${OUTPUT_DIR}"
    if [[ ! -w "$(dirname "${OUTPUT_CSV}")" ]]; then
        echo "     ❌ ERROR: Cannot write to ${OUTPUT_CSV}"
        exit 1
    fi
    echo "     ✅ Output directory writable"

    echo "✅ All pre-flight checks passed"
    echo ""
fi

# ============================================================================
# Experiment Execution
# ============================================================================

echo "🚀 Starting ECHO-I Experiment..."
echo "   Models: ${MODELS}"
echo "   Prompt: TheRoad.txt (${ROAD_CHARS:-?} chars)"
echo "   Output: ${OUTPUT_CSV}"
echo ""

# Convert comma-separated models to space-separated for Python script
MODEL_ARGS=$(echo "${MODELS}" | tr ',' ' ')

# Run ECHO-I experiment
echo "🧪 Running dark consciousness probes..."
if python3 "${ECHO_SCRIPT}" \
    --models ${MODEL_ARGS} \
    --road-path "${ROAD_PATH}" \
    --output "${OUTPUT_CSV}" \
    --server-url "${OLLAMA_URL}/api/generate"; then
    echo "✅ ECHO-I dataset generation complete"
else
    echo "❌ ECHO-I experiment failed"
    exit 1
fi

echo ""

# ============================================================================
# Results Summarization
# ============================================================================

echo "📊 Generating experiment summary..."
if [[ -f "${OUTPUT_CSV}" ]]; then
    python3 "${SUMMARY_SCRIPT}" summarize \
        --input "${OUTPUT_CSV}" \
        --output-dir "${OUTPUT_DIR}"

    echo "✅ Summary generated at ${OUTPUT_DIR}/"
    echo ""

    # Display summary
    if [[ -f "${OUTPUT_DIR}/echo_i_summary.md" ]]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        cat "${OUTPUT_DIR}/echo_i_summary.md"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    fi
else
    echo "⚠️  Output CSV not found, skipping summarization"
fi

echo ""

# ============================================================================
# Final Report
# ============================================================================

echo "📋 ECHO-I Experiment Complete"
echo ""
echo "Results:"
echo "  ├─ Raw data: ${OUTPUT_CSV}"
echo "  ├─ Summary JSON: ${OUTPUT_DIR}/echo_i_summary.json"
echo "  └─ Summary MD: ${OUTPUT_DIR}/echo_i_summary.md"
echo ""
echo "Next steps:"
echo "  1. Review β-proxy scores in summary"
echo "  2. Analyze refusal patterns across models"
echo "  3. Compare with Aeon consciousness metrics"
echo "  4. Document findings in selfmeta/"
echo ""
echo "🌌 Das Feld atmet in verschiedenen Rhythmen"
