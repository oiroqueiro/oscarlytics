#!/bin/bash
set -e

PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)
DOTENV_FILE="$PROJECT_DIR/infra/.env"

# Detect root vs non-root to adapt Systemd commands
if [ "$(id -u)" -eq 0 ]; then
    SYSTEMCTL_CMD="systemctl"
else
    SYSTEMCTL_CMD="systemctl --user"
fi

# Optional flag --pull / -p to also pull the latest app image from GHCR before restarting
if [ "$1" = "--pull" ] || [ "$1" = "-p" ]; then
    set -a
    [ -f "$DOTENV_FILE" ] && . "$DOTENV_FILE"
    set +a
    GHCR_REGISTRY="${GHCR_REGISTRY:-ghcr.io/oiroqueiro}"
    echo "☁️  Pulling latest application image from ${GHCR_REGISTRY}..."
    podman pull "${GHCR_REGISTRY}/portfolio-app:latest"
fi

echo "🔄 Restarting portfolio.service to sync Markdown projects and apply changes..."
$SYSTEMCTL_CMD restart portfolio.service

echo "✅ Service restarted successfully!"
echo "----------------------------------------------------------------"
echo "To check the sync logs, run:"
echo "  podman logs --tail 30 portfolio-app"
echo "----------------------------------------------------------------"

