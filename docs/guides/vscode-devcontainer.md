# Guía de VSCode y DevContainers

Esta guía cubre la configuración del entorno de desarrollo, el uso del devcontainer y el flujo de trabajo diario con VSCode para este repositorio.

---

## Requisitos previos

Instala las siguientes herramientas antes de continuar:

| Herramienta | Versión mínima | Enlace |
|-------------|---------------|--------|
| Docker Desktop | 4.x | https://www.docker.com/products/docker-desktop |
| VSCode | 1.80+ | https://code.visualstudio.com |
| Dev Containers (extensión) | Latest | [Marketplace](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) |

---

## Primera apertura con DevContainer

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd ai-dev-mastery
```

### 2. Abrir en VSCode

```bash
code .
```

### 3. Reabrir en el contenedor

VSCode detectará automáticamente el `.devcontainer/` y mostrará una notificación en la esquina inferior derecha:

```
Folder contains a Dev Container configuration file. Reopen folder to develop in a container.
```

Haz clic en **Reopen in Container**.

Si no aparece la notificación:
- Abre la paleta de comandos (`Cmd+Shift+P` / `Ctrl+Shift+P`)
- Ejecuta: `Dev Containers: Reopen in Container`

### 4. Esperar a que el contenedor arranque

La primera vez descarga la imagen base y las extensiones — puede tardar varios minutos. Las siguientes aperturas son inmediatas.

---

## Extensiones incluidas

El devcontainer instala automáticamente:

| Extensión | Propósito |
|-----------|-----------|
| Python + Pylance | Soporte Python e IntelliSense |
| Black Formatter | Formateo automático de código |
| Ruff | Linting rápido |
| Jupyter | Notebooks cuando sea necesario |
| Markdown All in One | Edición de documentación |
| markdownlint | Validación de Markdown |
| YAML | Validación de frontmatter |
| GitLens | Historial y anotaciones Git |
| Git Graph | Visualización de ramas |
| Error Lens | Errores inline en el editor |
| Todo Tree | Gestión de TODOs en el código |

---

## Levantar la infraestructura local

La infraestructura (Ollama, WebUI, ChromaDB) corre en Docker pero **fuera** del devcontainer. Ábrela en una terminal de tu sistema (no en VSCode):

```bash
cd infrastructure
cp .env.example .env        # solo la primera vez
docker-compose --profile light up -d
```

### Perfiles disponibles

| Perfil | Servicios | Cuándo usarlo |
|--------|-----------|---------------|
| `light` | Ollama + Open WebUI | Módulos 01-08, recursos limitados |
| `full` | Ollama + Open WebUI + ChromaDB | Módulos 05+ (RAG, Agents) |

### Verificar que los servicios están activos

```bash
# Ollama
curl http://localhost:11434/api/tags

# Open WebUI → abre en el navegador
open http://localhost:3000

# ChromaDB (solo profile full)
curl http://localhost:8000/api/v1/heartbeat
```

### Cargar un modelo en Ollama

```bash
docker exec -it ollama ollama pull mistral
```

---

## Flujo de trabajo diario

### Apertura del entorno

1. Abre Docker Desktop — asegúrate de que está corriendo
2. Levanta la infraestructura si no está activa:
   ```bash
   cd infrastructure && docker-compose --profile light up -d
   ```
3. Abre VSCode y acepta **Reopen in Container** si aparece, o usa la paleta de comandos

### Trabajar con un módulo

Cada módulo tiene su propia estructura en `docs/` y `labs/`. Para trabajar en un lab:

```bash
# Desde el terminal integrado de VSCode (dentro del devcontainer)
cd labs/05-rag
python -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env
# Edita .env con tu configuración local

cd lab-02-retrieval-playground
python main.py
```

### Cambiar entre módulos con devcontainer específico

Algunos módulos tienen su propio devcontainer en `.devcontainer/modules/[módulo]/`. Para usarlo:

1. Abre la paleta de comandos (`Cmd+Shift+P`)
2. Ejecuta: `Dev Containers: Switch Container`
3. Selecciona el módulo correspondiente

> **Nota:** el devcontainer base es suficiente para la mayoría de módulos. Los devcontainers específicos solo son necesarios cuando el módulo requiere dependencias adicionales del sistema.

---

## Parar la infraestructura

```bash
cd infrastructure
docker-compose down
```

Para parar y eliminar los volúmenes (reset completo):

```bash
docker-compose down -v
```

---

## Troubleshooting habitual

### El devcontainer no arranca

```
Error: Cannot connect to Docker daemon
```

→ Asegúrate de que Docker Desktop está corriendo antes de abrir VSCode.

### Puerto ya en uso

```
Error: Bind for 0.0.0.0:11434 failed: port is already allocated
```

→ Cambia el puerto en `infrastructure/.env`:
```bash
OLLAMA_PORT=11435
```

### Ollama no responde desde el devcontainer

Los puertos `11434`, `3000` y `8000` están configurados como `forwardPorts` en el devcontainer. Si Ollama no responde:

1. Verifica que el contenedor de Ollama está corriendo: `docker ps`
2. Verifica que el puerto está forwarded en VSCode (panel **Ports** en la barra inferior)

### El modelo no está cargado

```
Error: model not found
```

→ Descarga el modelo manualmente:
```bash
docker exec -it ollama ollama pull mistral
```

### Extensiones no instaladas

Si las extensiones no se instalan automáticamente:
- Abre la paleta de comandos
- Ejecuta: `Dev Containers: Rebuild Container`

---

## Recursos adicionales

- [Dev Containers documentation](https://code.visualstudio.com/docs/devcontainers/containers)
- [Ollama documentation](https://ollama.ai/docs)
- [Open WebUI documentation](https://docs.openwebui.com)
