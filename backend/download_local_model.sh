#!/bin/bash
# Download a better local GGUF model for ComplianceHub's local AI provider.
#
# Usage:
#   bash download_local_model.sh                  # Download recommended Qwen2.5-1.5B
#   bash download_local_model.sh qwen-0.5b        # Download original small model
#   bash download_local_model.sh llama-3.2-3b     # Download Llama 3.2 3B (larger, slower)
#
# After download, set LOCAL_MODEL_ID env var and restart llama-server:
#   export LOCAL_MODEL_ID="qwen-1.5b"
#   pkill llama-server
#   /opt/llama-server/llama-server -m /opt/llama-server/models/qwen-1.5b.gguf \
#     -c 4096 -t 4 -b 2048 --mlock --port 8080

set -euo pipefail

MODELS_DIR="/opt/llama-server/models"
mkdir -p "$MODELS_DIR"

download_model() {
    local name="$1"
    local url="$2"
    local dest="$MODELS_DIR/$name.gguf"

    if [ -f "$dest" ]; then
        echo "Already downloaded: $dest"
        ls -lh "$dest"
        return
    fi

    echo "Downloading $name → $dest ..."
    wget -q --show-progress -O "$dest" "$url"
    echo "Done: $(ls -lh "$dest")"
}

case "${1:-qwen-1.5b}" in
    qwen-0.5b)
        download_model "qwen-0.5b" \
            "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf"
        ;;
    qwen-1.5b|*)
        download_model "qwen-1.5b" \
            "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
        echo ""
        echo "Recommended: Set LOCAL_MODEL_ID=qwen-1.5b in your .env"
        echo "Then restart llama-server with:"
        echo "  /opt/llama-server/llama-server -m $MODELS_DIR/qwen-1.5b.gguf -c 4096 -t 4 -b 2048 --mlock --port 8080"
        ;;
    llama-3.2-3b)
        download_model "llama-3.2-3b" \
            "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
        echo "Note: 3B model requires ~2.5GB RAM and may be slow on ARM64 (~35s/doc)"
        ;;
esac
