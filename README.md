# AI Dev Mastery

Una hoja de ruta progresiva para dominar el desarrollo de soluciones con Inteligencia Artificial — desde los fundamentos hasta producción.

## Estructura del repositorio

```text
ai-dev-mastery/
├── docs/          ← documentación teórica por módulo
├── labs/          ← laboratorios prácticos por módulo
├── infrastructure/← entorno local (Ollama, WebUI, ChromaDB)
├── meta/          ← estándares de calidad y plantillas
└── .devcontainer/ ← configuración de entorno VSCode
```

## Módulos

| # | Módulo | Nivel |
|---|--------|-------|
| 01 | [LLM Fundamentals](docs/01-llm-fundamentals/README.md) | Foundational |
| 02 | [LLM APIs](docs/02-llm-apis/README.md) | Foundational |
| 03 | [Prompt Engineering](docs/03-prompt-engineering/README.md) | Foundational |
| 04 | [Structured Outputs & Tool Usage](docs/04-structured-outputs/README.md) | Intermediate |
| 05 | [RAG](docs/05-rag/README.md) | Intermediate |
| 06 | [Memory & Context Management](docs/06-memory-context/README.md) | Intermediate |
| 07 | [AI Agents](docs/07-ai-agents/README.md) | Intermediate |
| 08 | [Frameworks & Tools](docs/08-frameworks-tools/README.md) | Intermediate |
| 09 | [AI con Java](docs/09-ai-java/README.md) | Intermediate |
| 10 | [Evaluation & Testing](docs/10-evaluation-testing/README.md) | Advanced |
| 11 | [Safety & Guardrails](docs/11-safety-guardrails/README.md) | Advanced |
| 12 | [Performance & Optimization](docs/12-performance-optimization/README.md) | Advanced |
| 13 | [Deployment & Scaling](docs/13-deployment-scaling/README.md) | Advanced |
| 14 | [Observabilidad y MLOps](docs/14-observabilidad-mlops/README.md) | Advanced |
| 15 | [Arquitecturas de Referencia](docs/15-reference-architectures/README.md) | Advanced |
| 16 | [Real-World Projects](docs/16-real-world-projects/README.md) | Advanced |

## Cómo empezar

### 1. Configurar el entorno

Requisitos previos:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [VSCode](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

→ Consulta la [Guía de VSCode y DevContainers](docs/guides/vscode-devcontainer.md) para instrucciones detalladas.

### 2. Levantar la infraestructura local

```bash
cd infrastructure
cp .env.example .env
docker-compose --profile light up -d
```

Servicios disponibles:
- **Ollama** → http://localhost:11434 (API de modelos locales)
- **Open WebUI** → http://localhost:3000 (interfaz web)

### 3. Seguir el índice

Empieza por el módulo 01 y sigue el orden — cada módulo construye sobre el anterior.

## Documentación

- [Guía de VSCode y DevContainers](docs/guides/vscode-devcontainer.md)
- [Estándares de documentación](meta/README.md)
- [Infraestructura local](infrastructure/README.md)

## Laboratorios

→ Ver [índice de laboratorios](labs/README.md)
