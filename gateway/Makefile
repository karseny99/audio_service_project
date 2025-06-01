generate:
	# 1. Создаем директории
	mkdir -p src/protos/user_context/generated
	mkdir -p src/protos/streaming_context/generated

	# 2. Генерируем код
	poetry run python3 -m grpc_tools.protoc \
		-Isrc/protos/user_context/ \
		--python_out=./src/protos/user_context/generated \
		--grpc_python_out=./src/protos/user_context/generated \
		--pyi_out=./src/protos/user_context/generated \
		./src/protos/user_context/commands.proto

	# 2. Генерируем код
	poetry run python3 -m grpc_tools.protoc \
		-Isrc/protos/streaming_context/ \
		--python_out=./src/protos/streaming_context/generated \
		--grpc_python_out=./src/protos/streaming_context/generated \
		--pyi_out=./src/protos/streaming_context/generated \
		./src/protos/streaming_context/streaming.proto
	
	# Автоматическое исправление импортов
	sed -i 's/^import commands_pb2/from src.protos.user_context.generated import commands_pb2/' src/protos/user_context/generated/*.py
	sed -i 's/^import commands_pb2_grpc/from src.protos.user_context.generated import commands_pb2_grpc/' src/protos/user_context/generated/*.py

	
	sed -i 's/^import streaming_pb2/from src.protos.streaming_context.generated import streaming_pb2/' src/protos/streaming_context/generated/*.py
	sed -i 's/^import streaming_pb2_grpc/from src.protos.streaming_context.generated import streaming_pb2_grpc/' src/protos/streaming_context/generated/*.py

install:
	poetry add grpcio grpcio-tools

run:
	poetry run python3 main.py

clean:
	rm -rf ./src/protos/user_context/generated/*
	rm -rf ./src/protos/streaming_context/generated/*