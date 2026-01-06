#!/usr/bin/env bash
set -euo pipefail

# Directory setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
PROTO_DIR="$ROOT_DIR/proto"

# Ensure protoc is available
"$SCRIPT_DIR/ensure_protoc.sh"

# Activate virtual environment
if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
  echo "Error: Virtual environment not found at $VENV_DIR" >&2
  exit 1
fi
source "$VENV_DIR/bin/activate"

# Proto files to compile
PROTO_FILES=(
  "market/market.proto"
  "trade/trade.proto"
  "broker/broker.proto"
  "model/model.proto"
  "statistic/statistic.proto"
  "types/amount/amount.proto"
)

# Compile all proto files
echo "Compiling protocol buffers..."
for proto_file in "${PROTO_FILES[@]}"; do
  echo "  - $proto_file"
  python -m grpc_tools.protoc \
    -I "$PROTO_DIR" \
    --python_out="$PROTO_DIR" \
    --grpc_python_out="$PROTO_DIR" \
    "$PROTO_DIR/$proto_file"
done

echo "Protocol buffer compilation complete!"

# Deactivate instead of deleting venv
deactivate
