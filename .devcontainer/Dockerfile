FROM mcr.microsoft.com/devcontainers/python:3.11-bookworm

# System utilities needed by the labs and post-create script
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip once at build time
RUN pip install --upgrade pip
