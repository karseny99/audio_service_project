generate:
	mkdir -p src/core/protos/generated
	
	# Генерируем код для TrackService
	poetry run python3 -m grpc_tools.protoc \
		-I./src/core/protos \
		--python_out=./src/core/protos/generated \
		--grpc_python_out=./src/core/protos/generated \
		--pyi_out=./src/core/protos/generated \
		./src/core/protos/TrackCommands.proto
	
	# Генерируем код для PlaylistService
	poetry run python3 -m grpc_tools.protoc \
		-I./src/core/protos \
		--python_out=./src/core/protos/generated \
		--grpc_python_out=./src/core/protos/generated \
		--pyi_out=./src/core/protos/generated \
		./src/core/protos/PlaylistCommands.proto
	
	# Исправляем импорты для TrackService
	sed -i 's/^import TrackCommands_pb2/from src.core.protos.generated import TrackCommands_pb2/' src/core/protos/generated/TrackCommands_pb2_grpc.py
	sed -i 's/^import TrackCommands_pb2/from src.core.protos.generated import TrackCommands_pb2/' src/core/protos/generated/TrackCommands_pb2.py
	
	# Исправляем импорты для PlaylistService
	sed -i 's/^import PlaylistCommands_pb2/from src.core.protos.generated import PlaylistCommands_pb2/' src/core/protos/generated/PlaylistCommands_pb2_grpc.py
	sed -i 's/^import PlaylistCommands_pb2/from src.core.protos.generated import PlaylistCommands_pb2/' src/core/protos/generated/PlaylistCommands_pb2.py
	
	# Создаем пустой __init__.py
	touch src/core/protos/generated/__init__.py

install:
	poetry add grpcio grpcio-tools

run:
	poetry run python3 main.py

clean:
	rm -rf src/core/protos/generated/*