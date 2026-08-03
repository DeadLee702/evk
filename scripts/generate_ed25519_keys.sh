#!/usr/bin/env bash
set -euo pipefail
KEY_DIR=${1:-$HOME/.z12/keystore}
mkdir -p "$KEY_DIR"
PRIV="$KEY_DIR/gemini_ed25519"
PUB="$PRIV.pub"
if [ -f "$PRIV" ]; then
  echo "Key already exists at $PRIV"
  exit 1
fi
# Generate ed25519 keypair with ssh-keygen (openssh format)
ssh-keygen -t ed25519 -f "$PRIV" -N "" -C "gemini@z12"
# Convert public key to raw hex/PEM if needed; many libs can use the OpenSSH public key.
echo "Private key: $PRIV"
echo "Public key: $PUB"
