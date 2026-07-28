#!/bin/bash
set -e

HOME_DIR="/root/.acme.sh"
DOMAIN="${DOMAIN:-oscarlytics.com}"
DUCK_TOKEN="${DuckDNS_Token}"
CHALLENGE_ALIAS="${CHALLENGE_ALIAS:-oscarlytics-oauth.duckdns.org}"

echo "🔒 Starting ACME SSL sidecar for domain: ${DOMAIN}..."

export DuckDNS_Token="${DUCK_TOKEN}"

check_cert_validity() {
    if [ ! -f "$HOME_DIR/fullchain.pem" ]; then
        return 1
    fi
    ISSUER=$(openssl x509 -in "$HOME_DIR/fullchain.pem" -noout -issuer 2>/dev/null || true)
    if echo "$ISSUER" | grep -qi "localhost"; then
        echo "⚠️ Certificate is self-signed: $ISSUER"
        return 1
    fi
    if ! openssl x509 -checkend 2592000 -noout -in "$HOME_DIR/fullchain.pem" 2>/dev/null; then
        echo "⚠️ Certificate expires in less than 30 days or is expired."
        return 1
    fi
    return 0
}

issue_and_install() {
    echo "🔑 Issuing production Let's Encrypt SSL certificate..."
    /opt/acme.sh/acme.sh --register-account -m "oscar@${DOMAIN}" --server letsencrypt --home "$HOME_DIR" || true
    
    /opt/acme.sh/acme.sh --issue \
        --dns dns_duckdns \
        -d "$DOMAIN" \
        --challenge-alias "$CHALLENGE_ALIAS" \
        --server letsencrypt \
        --home "$HOME_DIR" \
        --dnssleep 20 \
        --force
        
    /opt/acme.sh/acme.sh --install-cert \
        -d "$DOMAIN" \
        --ecc \
        --fullchain-file "$HOME_DIR/fullchain.pem" \
        --key-file "$HOME_DIR/privkey.pem" \
        --home "$HOME_DIR"
        
    echo "✅ SSL Certificate successfully issued and installed to $HOME_DIR/fullchain.pem"
}

if ! check_cert_validity; then
    echo "⚡ Valid certificate not found or expiring soon. Issuing now..."
    issue_and_install || echo "⚠️ Issuance attempt failed or deferred."
else
    echo "✅ Certificate is valid."
fi

echo "🔄 Running cron check loop every 12 hours..."
while true; do
    sleep 43200
    /opt/acme.sh/acme.sh --cron --home "$HOME_DIR" || true
    if ! check_cert_validity; then
        issue_and_install || true
    fi
done
