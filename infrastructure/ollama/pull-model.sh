#!/usr/bin/env sh
# Pulls the model configured via OLLAMA_MODEL.
# Runs as a one-shot init container after the ollama service is healthy.
set -eu

MODEL="${OLLAMA_MODEL:-llama3.2}"
HOST="${OLLAMA_HOST:-http://ollama:11434}"

echo "[ollama-init] Pulling model: ${MODEL}"
ollama pull "${MODEL}"
echo "[ollama-init] Done."
