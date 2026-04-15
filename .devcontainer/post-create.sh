#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# 1. Python dependencies
# ---------------------------------------------------------------------------
echo "[post-create] Installing Python dependencies..."
pip install -r labs/llm-fundamentals/requirements.txt
