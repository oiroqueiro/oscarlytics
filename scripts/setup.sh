#!/bin/bash

# ----- 1. PATHS & DETECTION -----
PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)
DOTENV_FILE="$PROJECT_DIR/infra/.env"

if [ ! -f "$DOTENV_FILE" ]; then
    DOTENV_FILE="$PROJECT_DIR/.env"
fi

if [ "$(id -u)" -eq 0 ]; then
    echo "👤 Running as root. Quadlets will be installed system-wide (global mode)."
    QUADLET_DIR="/etc/containers/systemd"
    SYSTEMCTL_CMD="systemctl"
else
    echo "👤 Running as non-root user. Quadlets will be installed in rootless mode."
    QUADLET_DIR="$HOME/.config/containers/systemd"
    SYSTEMCTL_CMD="systemctl --user"
fi

cd "$PROJECT_DIR"

# We export variables for envsubst
export $(grep -v '^#' "$DOTENV_FILE" | xargs)
export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@127.0.0.1:5432/${DB_NAME}"
export PWD
export PORTFOLIO_IMG_DIR="${PORTFOLIO_IMG_DIR:-$PROJECT_DIR/data/portfolio_img}"
export DOMAIN="${DOMAIN:-localhost}"
export DuckDNS_Token="${DuckDNS_Token:-}"

# ----- 2. DATA DIRS -----
echo "📂 Ensuring data directories exist..."
mkdir -p "$PROJECT_DIR/data/portfolio_db"
mkdir -p "$PROJECT_DIR/data/meilisearch_data"
mkdir -p "$PROJECT_DIR/data/portfolio_storage"
mkdir -p "$PORTFOLIO_IMG_DIR"

# Seed the image directory with initial app images if empty
if [ -z "$(ls -A "$PORTFOLIO_IMG_DIR")" ]; then
    cp -r "$PROJECT_DIR/apps/portfolio/portfolio/static/img/"* "$PORTFOLIO_IMG_DIR/" 2>/dev/null || true
fi

# Ensure non-root user (1000) inside container can write to bind mount
chmod 777 "$PROJECT_DIR/data/meilisearch_data"
chmod 777 "$PROJECT_DIR/data/portfolio_storage"

# ----- 3. BUILD HARDENED IMAGES -----
echo "🏗️  Building hardened Meilisearch image..."
podman build -t portfolio-meilisearch:hardened -f "$PROJECT_DIR/infra/Containerfile.meilisearch" "$PROJECT_DIR/infra"

echo "🏗️  Building hardened Portfolio App image..."
podman build -t portfolio-app:hardened -f "$PROJECT_DIR/apps/portfolio/Containerfile.app" "$PROJECT_DIR/apps/portfolio"

echo "🏗️  Building hardened Nginx image..."
podman build -t portfolio-nginx:hardened -f "$PROJECT_DIR/infra/Containerfile.nginx" "$PROJECT_DIR/infra"

echo "🏗️  Building hardened ACME.sh image..."
podman build -t portfolio-acmesh:hardened -f "$PROJECT_DIR/infra/Containerfile.acmesh" "$PROJECT_DIR/infra"

# ----- 4. GENERATION -----
echo "⚙️  Generating .generated files for the stack..."

# Mapping: Original -> Generated
declare -A FILES=(
    ["infra/portfolio_db.volume"]="infra/portfolio_db.generated.volume"
    ["infra/portfolio_meilisearch.volume"]="infra/portfolio_meilisearch.generated.volume"
    ["infra/portfolio_storage.volume"]="infra/portfolio_storage.generated.volume"
    ["infra/portfolio.network"]="infra/portfolio.generated.network"
    ["infra/portfolio.yaml"]="infra/portfolio.generated.yaml"
    ["infra/portfolio.kube"]="infra/portfolio.generated.kube"
)

for SRC in "${!FILES[@]}"; do
    DEST="${FILES[$SRC]}"
    envsubst < "$SRC" > "$DEST"
done

# ----- 5. LINKS -----
echo "🔗 Creating links in Quadlet directory ($QUADLET_DIR)..."
mkdir -p "$QUADLET_DIR"
# Clean up old portfolio and meilisearch links
rm -f "$QUADLET_DIR"/portfolio*
rm -f "$QUADLET_DIR"/meilisearch*

# Link generated and static Quadlet files
ln -sf "$PROJECT_DIR/infra/portfolio.generated.kube"             "$QUADLET_DIR/portfolio.kube"
ln -sf "$PROJECT_DIR/infra/portfolio.generated.yaml"             "$QUADLET_DIR/portfolio.yaml"
ln -sf "$PROJECT_DIR/infra/portfolio.generated.network"          "$QUADLET_DIR/portfolio.network"
ln -sf "$PROJECT_DIR/infra/portfolio_db.generated.volume"        "$QUADLET_DIR/portfolio_db.volume"
ln -sf "$PROJECT_DIR/infra/portfolio_meilisearch.generated.volume" "$QUADLET_DIR/portfolio_meilisearch.volume"
ln -sf "$PROJECT_DIR/infra/portfolio_storage.generated.volume"    "$QUADLET_DIR/portfolio_storage.volume"
ln -sf "$PROJECT_DIR/infra/portfolio_certs.volume"               "$QUADLET_DIR/portfolio_certs.volume"

# ----- 6. ACTIVATION -----
echo "🚀 Reloading systemd..."
$SYSTEMCTL_CMD daemon-reload

echo "🛑 Stopping old service instances if running..."
$SYSTEMCTL_CMD stop portfolio.service 2>/dev/null || true

echo "🌐 Starting network service (portfolio-network)..."
$SYSTEMCTL_CMD start portfolio-network.service

echo "💾 Starting persistent volume services..."
$SYSTEMCTL_CMD start portfolio_db-volume.service portfolio_meilisearch-volume.service portfolio_storage-volume.service portfolio_certs-volume.service

echo "🚀 Starting main portfolio service..."
$SYSTEMCTL_CMD start portfolio.service

echo "✅ Stack 'portfolio' consolidated and synchronized!"
echo ""
echo "----------------------------------------------------------------"
echo "🌐 Your application is starting at: http://localhost:8080"
echo "🔍 Meilisearch is starting at: http://localhost:7700"
echo "----------------------------------------------------------------"
echo "To view live logs, you can optionally run:"
if [ "$(id -u)" -eq 0 ]; then
  echo "  journalctl -u portfolio.service -f"
else
  echo "  journalctl --user -u portfolio.service -f"
fi
echo "----------------------------------------------------------------"