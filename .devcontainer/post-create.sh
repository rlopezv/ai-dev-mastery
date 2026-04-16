#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# 1. Python dependencies — one requirements.txt per module
# ---------------------------------------------------------------------------
echo "[post-create] Installing Python dependencies..."
pip install \
  -r labs/llm-fundamentals/requirements.txt \
  -r labs/llm-apis/requirements.txt \
  -r labs/prompt-engineering/requirements.txt \
  -r labs/structured-outputs/requirements.txt \
  -r labs/rag/requirements.txt \
  -r labs/memory-context/requirements.txt \
  -r labs/ai-agents/requirements.txt
