# Infrastructure

Local environment for running the labs without dependencies on external providers.

## Services

| Service | Profile | Port | Purpose |
|---------|---------|------|---------|
| Ollama | light, full | 11434 | Local LLM runtime |
| Open WebUI | light, full | 3000 | Web interface for interacting with models |
| ChromaDB | full | 8000 | Vector database (RAG modules and later) |

## Quick start

```bash
cd infrastructure
cp .env.example .env
# Edit .env for your hardware (see configuration section below)
docker-compose --profile light up -d
```

## Profiles

```bash
# Modules 01–04 or limited hardware
docker-compose --profile light up -d

# Modules 05 RAG, Agents, Memory (requires ChromaDB)
docker-compose --profile full up -d
```

## Hardware configuration

Edit `infrastructure/.env` before starting. The model set in `OLLAMA_MODEL` is
downloaded automatically when the devcontainer opens.

### CPU only (no GPU)

```bash
OLLAMA_MODEL=tinyllama
OLLAMA_MEMORY_LIMIT=4g
OLLAMA_NUM_PARALLEL=1
OLLAMA_CONTEXT_LENGTH=2048
```

> `tinyllama` is the lightest option (~600MB). Sufficient to validate the pipeline
> but with lower response quality.

### NVIDIA GPU with 4–6 GB VRAM (e.g. RTX 3060, GTX 1080)

```bash
OLLAMA_MODEL=mistral
OLLAMA_MEMORY_LIMIT=8g
OLLAMA_NUM_PARALLEL=1
OLLAMA_CONTEXT_LENGTH=4096
```

### NVIDIA GPU with 8 GB+ VRAM (e.g. RTX 3060 Ti, RTX 3070, RTX 4070)

```bash
OLLAMA_MODEL=mistral
OLLAMA_MEMORY_LIMIT=12g
OLLAMA_NUM_PARALLEL=2
OLLAMA_CONTEXT_LENGTH=8192
```

### NVIDIA GPU with 16 GB+ VRAM (e.g. RTX 3090, RTX 4090)

```bash
OLLAMA_MODEL=llama3
OLLAMA_MEMORY_LIMIT=20g
OLLAMA_NUM_PARALLEL=4
OLLAMA_CONTEXT_LENGTH=16384
```

## Available models

| Model | Size | Minimum VRAM | Quality |
|-------|------|-------------|---------|
| tinyllama | ~600 MB | 2 GB | Basic |
| mistral | ~4 GB | 4 GB | Good (recommended) |
| llama3 | ~4.7 GB | 6 GB | Very good |
| llama3:70b | ~40 GB | 24 GB | Excellent |

To change model at any time, edit `OLLAMA_MODEL` in `.env` and run:

```bash
docker exec -it ollama ollama pull <model>
```

## Verify services are running

```bash
# Ollama
curl http://localhost:11434/api/tags

# Loaded models
curl http://localhost:11434/api/tags | python -m json.tool

# Open WebUI
open http://localhost:3000    # macOS
start http://localhost:3000   # Windows

# ChromaDB (full profile only)
curl http://localhost:8000/api/v1/heartbeat
```

## Stop services

```bash
docker-compose down           # stop containers
docker-compose down -v        # stop + delete volumes (full reset)
```

## Upcoming services

Additional services will be added as the tutorial progresses:
- **n8n** — workflow orchestration (advanced modules)
- Additional vector database providers as needed
