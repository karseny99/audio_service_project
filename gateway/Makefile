generate:
	# 1. Создаем директории
	mkdir -p src/protos/user_context/generated

	# 2. Генерируем код
	poetry run python3 -m grpc_tools.protoc \
		-Isrc/protos/user_context/ \
		--python_out=./src/protos/user_context/generated \
		--grpc_python_out=./src/protos/user_context/generated \
		--pyi_out=./src/protos/user_context/generated \
		./src/protos/user_context/commands.proto

	# Автоматическое исправление импортов
	sed -i 's/^import commands_pb2/from src.protos.user_context.generated import commands_pb2/' src/protos/user_context/generated/*.py
	sed -i 's/^import commands_pb2_grpc/from src.protos.user_context.generated import commands_pb2_grpc/' src/protos/user_context/generated/*.py

install:
	poetry add grpcio grpcio-tools

clean:
	rm -rf ./src/protos/user_context/generated/*