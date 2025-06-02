generate:
	# 1. Создаем директории
	mkdir -p src/protos/user_context/generated
	mkdir -p src/protos/streaming_context/generated
	mkdir -p src/protos/listening_history_context/generated

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


	# 2. Генерируем код
	poetry run python3 -m grpc_tools.protoc \
		-Isrc/protos/streaming_context/ \
		--python_out=./src/protos/streaming_context/generated \
		--grpc_python_out=./src/protos/streaming_context/generated \
		--pyi_out=./src/protos/streaming_context/generated \
		./src/protos/streaming_context/streaming.proto
	

	sed -i 's/^import streaming_pb2/from src.protos.streaming_context.generated import streaming_pb2/' src/protos/streaming_context/generated/*.py
	sed -i 's/^import streaming_pb2_grpc/from src.protos.streaming_context.generated import streaming_pb2_grpc/' src/protos/streaming_context/generated/*.py

	poetry run python3 -m grpc_tools.protoc \
		-Isrc/protos/listening_history_context/ \
		--python_out=./src/protos/listening_history_context/generated \
		--grpc_python_out=./src/protos/listening_history_context/generated \
		--pyi_out=./src/protos/listening_history_context/generated \
		./src/protos/listening_history_context/LikeCommands.proto

	sed -i 's/^import LikeCommands_pb2/from src.protos.listening_history_context.generated import LikeCommands_pb2/' src/protos/listening_history_context/generated/*.py
	sed -i 's/^import LikeCommands_pb2_grpc/from src.protos.listening_history_context.generated import LikeCommands_pb2_grpc/' src/protos/listening_history_context/generated/*.py


install:
	poetry add grpcio grpcio-tools

run:
	poetry run python3 main.py

clean:
	rm -rf ./src/protos/user_context/generated/*
	rm -rf ./src/protos/streaming_context/generated/*
	rm -rf ./src/protos/listening_history_context/generated/*