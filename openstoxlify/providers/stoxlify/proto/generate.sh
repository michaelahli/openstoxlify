#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
"$SCRIPT_DIR/ensure_protoc.sh"

ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
PROTO_DIR="$ROOT_DIR/proto"

source "$VENV_DIR/bin/activate"

python -m grpc_tools.protoc \
  -I "$PROTO_DIR" \
  --python_out="$PROTO_DIR" \
  --grpc_python_out="$PROTO_DIR" \
  "$PROTO_DIR/market/market.proto"

rm -rf $VENV_DIR
