#!/bin/bash

# ----- 1. PATHS -----
PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)
QUADLET_DIR="$HOME/.config/containers/systemd"
DOTENV_FILE="$PROJECT_DIR/infra/.env"

if [ ! -f "$DOTENV_FILE" ]; then
    echo "❌ Error: Could not find $DOTENV_FILE!"
    echo "Please create infra/.env using infra/env.example as a template."
    exit 1
fi

cd "$PROJECT_DIR"

# We export variables for envsubst
export $(grep -v '^#' "$DOTENV_FILE" | xargs)
export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@127.0.0.1:5432/${DB_NAME}"
export PWD
export PORTFOLIO_IMG_DIR="${PORTFOLIO_IMG_DIR:-$PROJECT_DIR/data/portfolio_img}"
export DOMAIN="${DOMAIN:-localhost}"
export DuckDNS_Token="${DuckDNS_Token:-}"
export GHCR_REGISTRY="${GHCR_REGISTRY:-ghcr.io/oiroqueiro}"

# ----- 2. DATA DIRS -----
echo "📂 Ensuring data directories exist..."
mkdir -p "$PROJECT_DIR/data/portfolio_db"
mkdir -p "$PROJECT_DIR/data/meilisearch_data"
mkdir -p "$PROJECT_DIR/data/portfolio_storage"
mkdir -p "$PORTFOLIO_IMG_DIR"

# Ensure non-root user (1000) inside container can write to bind mount
chmod 777 "$PROJECT_DIR/data/meilisearch_data"
chmod 777 "$PROJECT_DIR/data/portfolio_storage"

# ----- 3. GENERATION (Envsubst) -----
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

# ----- 4. LINKS -----
echo "🔗 Creating links in Quadlet..."
mkdir -p "$QUADLET_DIR"

# Link generated files
ln -sf "$PROJECT_DIR/infra/portfolio.generated.kube"             "$QUADLET_DIR/portfolio.kube"
ln -sf "$PROJECT_DIR/infra/portfolio.generated.yaml"             "$QUADLET_DIR/portfolio.yaml"
ln -sf "$PROJECT_DIR/infra/portfolio.generated.network"          "$QUADLET_DIR/portfolio.network"
ln -sf "$PROJECT_DIR/infra/portfolio_db.generated.volume"        "$QUADLET_DIR/portfolio_db.volume"
ln -sf "$PROJECT_DIR/infra/portfolio_meilisearch.generated.volume" "$QUADLET_DIR/portfolio_meilisearch.volume"
ln -sf "$PROJECT_DIR/infra/portfolio_storage.generated.volume"    "$QUADLET_DIR/portfolio_storage.volume"

# ----- 5. ACTIVATION -----
echo "🚀 Reloading systemd and starting the stack..."
systemctl --user daemon-reload
systemctl --user stop portfolio.service 2>/dev/null || true
systemctl --user start portfolio.service

echo "✅ Production stack 'portfolio' deployed successfully using GHCR images!"
echo "Podman is pulling images in the background."
echo ""
echo "----------------------------------------------------------------"
echo "To view live logs, run:"
echo "  journalctl --user -u portfolio.service -f"
echo "----------------------------------------------------------------"
