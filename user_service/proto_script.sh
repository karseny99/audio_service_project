protoc -I=src/core/protobuf/messages \
  --python_out=src/core/protobuf/generated \
  src/core/protobuf/messages/user_events.proto