# Infrastructure

Entorno local para ejecutar los laboratorios sin dependencias sobre proveedores externos.

## Servicios

| Servicio | Perfil | Puerto | Propósito |
|----------|--------|--------|-----------|
| Ollama | light, full | 11434 | LLM runtime local |
| Open WebUI | light, full | 3000 | Interfaz web para interactuar con modelos |
| ChromaDB | full | 8000 | Base de datos vectorial (módulos RAG+) |

## Inicio rápido

```bash
cd infrastructure
cp .env.example .env
# Edita .env según tu hardware (ver sección de configuración)
docker-compose --profile light up -d
```

## Perfiles

```bash
# Módulos 01-08 o recursos limitados
docker-compose --profile light up -d

# Módulos RAG, Agents, Memory (requiere ChromaDB)
docker-compose --profile full up -d
```

## Configuración por hardware

Edita `infrastructure/.env` antes de arrancar. El modelo configurado en `OLLAMA_MODEL` se descargará automáticamente al abrir el devcontainer.

### CPU only (sin GPU)

```bash
OLLAMA_MODEL=tinyllama
OLLAMA_MEMORY_LIMIT=4g
OLLAMA_NUM_PARALLEL=1
OLLAMA_CONTEXT_LENGTH=2048
```

> `tinyllama` es el más ligero (~600MB). Suficiente para validar el pipeline pero con menor calidad de respuesta.

### NVIDIA GPU con 4-6GB VRAM (ej: RTX 3060, GTX 1080)

```bash
OLLAMA_MODEL=mistral
OLLAMA_MEMORY_LIMIT=8g
OLLAMA_NUM_PARALLEL=1
OLLAMA_CONTEXT_LENGTH=4096
```

### NVIDIA GPU con 8GB+ VRAM (ej: RTX 3060 Ti, RTX 3070, RTX 4070)

```bash
OLLAMA_MODEL=mistral
OLLAMA_MEMORY_LIMIT=12g
OLLAMA_NUM_PARALLEL=2
OLLAMA_CONTEXT_LENGTH=8192
```

### NVIDIA GPU con 16GB+ VRAM (ej: RTX 3090, RTX 4090)

```bash
OLLAMA_MODEL=llama3
OLLAMA_MEMORY_LIMIT=20g
OLLAMA_NUM_PARALLEL=4
OLLAMA_CONTEXT_LENGTH=16384
```

## Modelos disponibles

| Modelo | Tamaño | VRAM mínima | Calidad |
|--------|--------|-------------|---------|
| tinyllama | ~600MB | 2GB | Básica |
| mistral | ~4GB | 4GB | Buena (recomendado) |
| llama3 | ~4.7GB | 6GB | Muy buena |
| llama3:70b | ~40GB | 24GB | Excelente |

Cambia de modelo en cualquier momento editando `OLLAMA_MODEL` en `.env` y ejecutando:

```bash
docker exec -it ollama ollama pull <modelo>
```

## Verificar que los servicios están activos

```bash
# Ollama
curl http://localhost:11434/api/tags

# Modelos cargados
curl http://localhost:11434/api/tags | python -m json.tool

# Open WebUI
open http://localhost:3000    # macOS
start http://localhost:3000   # Windows

# ChromaDB (solo profile full)
curl http://localhost:8000/api/v1/heartbeat
```

## Parar servicios

```bash
docker-compose down           # para los contenedores
docker-compose down -v        # para + elimina volúmenes (reset completo)
```

## Servicios futuros

A medida que avance el tutorial se añadirán:
- **n8n** — orquestación de workflows (módulos avanzados)
- Otros proveedores de vector DB según necesidades
