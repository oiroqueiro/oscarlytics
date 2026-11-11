#!/bin/bash
set -e

PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)
DOTENV_FILE="$PROJECT_DIR/infra/.env"
PROJECTS_SRC="$PROJECT_DIR/apps/portfolio/content/projects"
CONTENT_YAML="$PROJECT_DIR/apps/portfolio/content/content.yaml"
STATIC_IMG_PROJECTS="$PROJECT_DIR/apps/portfolio/portfolio/static/img/projects"
DATA_IMG_PROJECTS="$PROJECT_DIR/data/portfolio_img/projects"

# Detect root vs non-root to adapt Systemd commands
if [ "$(id -u)" -eq 0 ]; then
    SYSTEMCTL_CMD="systemctl"
else
    SYSTEMCTL_CMD="systemctl --user"
fi

# Optional flag --pull / -p to pull the latest app image from GHCR and recreate the pod
if [ "$1" = "--pull" ] || [ "$1" = "-p" ]; then
    if [ -f "$DOTENV_FILE" ]; then
        GHCR_REGISTRY=$(grep '^GHCR_REGISTRY=' "$DOTENV_FILE" | cut -d= -f2- | tr -d '"' | tr -d "'")
    fi
    GHCR_REGISTRY="${GHCR_REGISTRY:-ghcr.io/oiroqueiro}"
    echo "☁️  Pulling latest application image from ${GHCR_REGISTRY}..."
    podman pull "${GHCR_REGISTRY}/portfolio-app:latest"

    echo "🔄 Restarting portfolio.service with the new image..."
    $SYSTEMCTL_CMD restart portfolio.service

    echo "⏳ Waiting for portfolio-app container to be ready..."
    for i in $(seq 1 20); do
        if [ "$(podman inspect -f '{{.State.Running}}' portfolio-app 2>/dev/null)" = "true" ]; then
            break
        fi
        sleep 1
    done
fi

# Sync project images from static/img/projects (generic fallbacks, no-clobber) and data/portfolio_img/projects into the running container
mkdir -p "$DATA_IMG_PROJECTS"
if [ -d "$STATIC_IMG_PROJECTS" ]; then
    cp -rn "$STATIC_IMG_PROJECTS/." "$DATA_IMG_PROJECTS/" 2>/dev/null || true
fi
if [ -d "$DATA_IMG_PROJECTS" ]; then
    echo "🖼️  Syncing project images into container..."
    podman exec portfolio-app mkdir -p /app/portfolio/static/img/projects
    podman cp "$DATA_IMG_PROJECTS/." portfolio-app:/app/portfolio/static/img/projects/
fi

# Sync Markdown projects and content.yaml from apps/portfolio/content/ into the running container
if [ -d "$PROJECTS_SRC" ]; then
    echo "📂 Copying Markdown files from $PROJECTS_SRC into container..."
    podman exec portfolio-app mkdir -p /app/mounted/projects /app/content/projects
    podman cp "$PROJECTS_SRC/." portfolio-app:/app/content/projects/
    podman cp "$PROJECTS_SRC/." portfolio-app:/app/mounted/projects/
fi

if [ -f "$CONTENT_YAML" ]; then
    podman cp "$CONTENT_YAML" portfolio-app:/app/content/content.yaml
    podman exec portfolio-app python /app/init_content.py
fi

echo "🔄 Syncing projects into PostgreSQL and Meilisearch..."
podman exec portfolio-app python /app/sync_projects.py

echo "✅ Portfolio updated and synchronized successfully!"


