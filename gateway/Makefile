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
	
	poetry run python3 -m grpc_tools.protoc \
        -Isrc/protos/user_context/ \
        --python_out=./src/protos/user_context/generated \
        --grpc_python_out=./src/protos/user_context/generated \
        --pyi_out=./src/protos/user_context/generated \
        ./src/protos/user_context/track.proto

	poetry run python3 -m grpc_tools.protoc \
        -Isrc/protos/user_context/ \
        --python_out=./src/protos/user_context/generated \
        --grpc_python_out=./src/protos/user_context/generated \
        --pyi_out=./src/protos/user_context/generated \
        ./src/protos/user_context/track_search.proto

	sed -i 's/^import track_search_pb2/from src.protos.user_context.generated import track_search_pb2/' src/protos/user_context/generated/*.py
	sed -i 's/^import track_search_pb2_grpc/from src.protos.user_context.generated import track_search_pb2_grpc/' src/protos/user_context/generated/*.py

	sed -i 's/^import track_pb2/from src.protos.user_context.generated import track_pb2/' src/protos/user_context/generated/*.py


	# Автоматическое исправление импортов
	sed -i 's/^import commands_pb2/from src.protos.user_context.generated import commands_pb2/' src/protos/user_context/generated/*.py
	sed -i 's/^import commands_pb2_grpc/from src.protos.user_context.generated import commands_pb2_grpc/' src/protos/user_context/generated/*.py

install:
	poetry add grpcio grpcio-tools

run:
	poetry run python3 main.py

clean:
	rm -rf ./src/protos/user_context/generated/*