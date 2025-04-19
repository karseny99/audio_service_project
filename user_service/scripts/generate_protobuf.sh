#!/bin/bash
# Generates Python code from .proto files
python -m grpc_tools.protoc \
  --proto_path=src/core/protobuf/messages/ \
  --python_out=src/core/protobuf/generated/ \
  src/core/protobuf/messages/*.proto
