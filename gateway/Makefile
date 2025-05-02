generate:
	# 1. Создаем директории
	mkdir -p user_context/generated

	# 2. Генерируем код
	poetry run python3 -m grpc_tools.protoc \
		-Iuser_context/protos \
		--python_out=./user_context/generated \
		--grpc_python_out=./user_context/generated \
		--pyi_out=./user_context/generated \
		user_context/protos/commands.proto

	# Автоматическое исправление импортов
	sed -i 's/^import commands_pb2/from user_context.generated import commands_pb2/' user_context/generated/*.py
	sed -i 's/^import commands_pb2_grpc/from user_context.generated import commands_pb2_grpc/' user_context/generated/*.py

install:
	poetry add grpcio grpcio-tools

clean:
	rm -rf user_context/generated/*