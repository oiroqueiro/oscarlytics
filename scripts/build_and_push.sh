#!/bin/bash

# ----- 1. PATHS & CONFIG -----
PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$PROJECT_DIR"

# Ensure registry is set, default to user's GHCR if missing
REGISTRY="${GHCR_REGISTRY:-ghcr.io/oiroqueiro}"

# ----- 2. BUILD HARDENED IMAGES -----
echo "🏗️  Building hardened Portfolio App image..."
podman build -t "${REGISTRY}/portfolio-app:latest" -f "$PROJECT_DIR/apps/portfolio/Containerfile.app" "$PROJECT_DIR/apps/portfolio"

echo "🏗️  Building hardened Nginx image..."
podman build -t "${REGISTRY}/portfolio-nginx:latest" -f "$PROJECT_DIR/infra/Containerfile.nginx" "$PROJECT_DIR/infra"

echo "🏗️  Building hardened ACME.sh image..."
podman build -t "${REGISTRY}/portfolio-acmesh:latest" -f "$PROJECT_DIR/infra/Containerfile.acmesh" "$PROJECT_DIR/infra"

# ----- 3. PUSH IMAGES TO REGISTRY -----
echo "☁️  Pushing images to registry (${REGISTRY})..."
podman push "${REGISTRY}/portfolio-app:latest"
podman push "${REGISTRY}/portfolio-nginx:latest"
podman push "${REGISTRY}/portfolio-acmesh:latest"

echo "✅ All images successfully built and pushed to ${REGISTRY}!"
echo "You can now run ./scripts/deploy_prod.sh on your production server."
