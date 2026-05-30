#!/bin/bash
set -e

PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)

echo "🏗️  Rebuilding Portfolio App image..."
podman build -t portfolio-app:hardened -f "$PROJECT_DIR/apps/portfolio/Containerfile.app" "$PROJECT_DIR/apps/portfolio"

echo "🚀 Restarting the portfolio service to apply changes..."
systemctl --user restart portfolio.service

echo "✅ App rebuilt and service restarted successfully!"
