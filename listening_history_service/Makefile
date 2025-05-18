generate:
	mkdir -p src/core/protos/generated
	
	# Генерируем код для TrackCommands
	poetry run python3 -m grpc_tools.protoc \
		-I./src/core/protos \
		--python_out=./src/core/protos/generated \
		--grpc_python_out=./src/core/protos/generated \
		--pyi_out=./src/core/protos/generated \
		./src/core/protos/TrackCommands.proto
	
	# Генерируем код для LikeCommands
	poetry run python3 -m grpc_tools.protoc \
		-I./src/core/protos \
		--python_out=./src/core/protos/generated \
		--grpc_python_out=./src/core/protos/generated \
		--pyi_out=./src/core/protos/generated \
		./src/core/protos/LikeCommands.proto
	
	# Генерируем код для TrackEvents (без grpc, т.к. это события)
	poetry run python3 -m grpc_tools.protoc \
		-I./src/core/protos \
		--python_out=./src/core/protos/generated \
		--pyi_out=./src/core/protos/generated \
		./src/core/protos/TrackEvents.proto

	# Генерируем код для UserEvents
	poetry run python3 -m grpc_tools.protoc \
		-I./src/core/protos \
		--python_out=./src/core/protos/generated \
		--pyi_out=./src/core/protos/generated \
		./src/core/protos/UserEvents.proto
	
	# Исправляем импорты для TrackCommands
	sed -i 's/^import TrackCommands_pb2/from src.core.protos.generated import TrackCommands_pb2/' src/core/protos/generated/TrackCommands_pb2_grpc.py
	sed -i 's/^import TrackCommands_pb2/from src.core.protos.generated import TrackCommands_pb2/' src/core/protos/generated/TrackCommands_pb2.py
	
	# Исправляем импорты для LikeCommands
	sed -i 's/^import LikeCommands_pb2/from src.core.protos.generated import LikeCommands_pb2/' src/core/protos/generated/LikeCommands_pb2_grpc.py
	sed -i 's/^import LikeCommands_pb2/from src.core.protos.generated import LikeCommands_pb2/' src/core/protos/generated/LikeCommands_pb2.py
	
	# Исправляем импорты для TrackEvents (если будут в других файлах)
	sed -i 's/^import TrackEvents_pb2/from src.core.protos.generated import TrackEvents_pb2/' src/core/protos/generated/*.py
	
	# Исправляем импорты для UserEvents
	sed -i 's/^import UserEvents_pb2/from src.core.protos.generated import UserEvents_pb2/' src/core/protos/generated/*.py

	# Создаем пустой __init__.py
	touch src/core/protos/generated/__init__.py

install:
	poetry add grpcio grpcio-tools

run:
	poetry run python3 main.py

clean:
	rm -rf src/core/protos/generated/*