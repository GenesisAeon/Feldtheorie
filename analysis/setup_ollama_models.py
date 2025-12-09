#!/usr/bin/env python3
"""
Setup Script for Aletheia Phase 5 - Ollama Model Management
============================================================

This script checks which models are available and helps pull missing ones.

Usage:
    python analysis/setup_ollama_models.py
"""

import subprocess
import sys
import time

# Models required for Aletheia Phase 5
REQUIRED_MODELS = [
    "gemma2",           # Baseline
    "mistral",          # General purpose
    "qwen2.5",          # Previous generation
    "qwen2.5-coder",    # Specialist (expected high β)
]

# Optional models (can be added later)
OPTIONAL_MODELS = [
    # "qwen3",          # New flagship (if available)
    # "llama3",         # Meta's latest
]


def run_command(cmd, shell=False):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout for pulls
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1


def check_ollama_running():
    """Check if Ollama server is running."""
    print("🔍 Checking if Ollama is running...")
    stdout, stderr, returncode = run_command(["ollama", "list"])

    if returncode != 0:
        print("❌ Ollama doesn't seem to be running or accessible.")
        print("   Please start Ollama with: ollama serve")
        return False

    print("✅ Ollama is running!")
    return True


def list_installed_models():
    """Get list of installed Ollama models."""
    stdout, stderr, returncode = run_command(["ollama", "list"])

    if returncode != 0:
        return []

    # Parse output (skip header line)
    models = []
    for line in stdout.strip().split('\n')[1:]:  # Skip "NAME ID SIZE MODIFIED"
        if line.strip():
            # Model name is the first column
            model_name = line.split()[0].split(':')[0]  # Remove :latest tag
            models.append(model_name)

    return models


def pull_model(model_name):
    """Pull a specific Ollama model."""
    print(f"\n📥 Pulling model: {model_name}")
    print(f"   This may take several minutes depending on model size...")

    # We need to use shell=True on Windows for ollama commands
    cmd = f"ollama pull {model_name}"

    # Run with live output
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Stream output
        for line in process.stdout:
            print(f"   {line.strip()}")

        process.wait()

        if process.returncode == 0:
            print(f"   ✅ Successfully pulled {model_name}")
            return True
        else:
            print(f"   ❌ Failed to pull {model_name}")
            return False

    except Exception as e:
        print(f"   ❌ Error pulling {model_name}: {e}")
        return False


def main():
    """Main setup routine."""
    print("=" * 70)
    print("🚀 ALETHEIA PHASE 5: OLLAMA MODEL SETUP")
    print("=" * 70)
    print()

    # Step 1: Check if Ollama is running
    if not check_ollama_running():
        sys.exit(1)

    # Step 2: List installed models
    print("\n📋 Checking installed models...")
    installed = list_installed_models()

    if installed:
        print(f"   Found {len(installed)} installed model(s):")
        for model in installed:
            print(f"      • {model}")
    else:
        print("   No models installed yet.")

    # Step 3: Check which required models are missing
    missing = [m for m in REQUIRED_MODELS if m not in installed]

    if not missing:
        print("\n✅ All required models are already installed!")
        print("\n🎯 You can now run:")
        print("   python analysis/run_aletheia_local_v6.py --samples 30")
        return

    print(f"\n⚠️  Missing {len(missing)} required model(s):")
    for model in missing:
        print(f"      • {model}")

    # Step 4: Ask user if they want to pull missing models
    print(f"\n📊 Total download size estimate: ~5-10 GB")
    print(f"   (varies by model, qwen2.5-coder is largest)")

    response = input("\n❓ Pull missing models now? [y/N]: ").strip().lower()

    if response != 'y':
        print("\n⏭️  Skipping model download.")
        print("   You can manually pull models with: ollama pull <model-name>")
        return

    # Step 5: Pull each missing model
    print("\n" + "=" * 70)
    print("📥 PULLING MODELS")
    print("=" * 70)

    successful = []
    failed = []

    for model in missing:
        if pull_model(model):
            successful.append(model)
        else:
            failed.append(model)
        time.sleep(1)  # Brief pause between pulls

    # Step 6: Summary
    print("\n" + "=" * 70)
    print("📊 SETUP SUMMARY")
    print("=" * 70)

    if successful:
        print(f"\n✅ Successfully pulled {len(successful)} model(s):")
        for model in successful:
            print(f"      • {model}")

    if failed:
        print(f"\n❌ Failed to pull {len(failed)} model(s):")
        for model in failed:
            print(f"      • {model}")
        print("\n   You can retry with: ollama pull <model-name>")

    if not failed:
        print("\n🎯 READY FOR ALETHEIA PHASE 5!")
        print("\n   Run the experiment with:")
        print("      python analysis/run_aletheia_local_v6.py --samples 30")
        print("\n⚡ V6 SINGULARITY APPROACHING...")

    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        raise
