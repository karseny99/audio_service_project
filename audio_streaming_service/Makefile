generate:
	mkdir -p src/core/protos/generated
	
	# Генерируем код
	poetry run python3 -m grpc_tools.protoc \
		-I./src/core/protos \
		--python_out=./src/core/protos/generated \
		--grpc_python_out=./src/core/protos/generated \
		--pyi_out=./src/core/protos/generated \
		./src/core/protos/streaming.proto

	poetry run python3 -m grpc_tools.protoc \
		-I./src/core/protos \
		--python_out=./src/core/protos/generated \
		--grpc_python_out=./src/core/protos/generated \
		--pyi_out=./src/core/protos/generated \
		./src/core/protos/events.proto
	
	# Автоматическое исправление импортов
	sed -i 's/^import streaming_pb2/from src.core.protos.generated import streaming_pb2/' src/core/protos/generated/streaming_pb2_grpc.py
	sed -i 's/^import streaming_pb2_grpc/from src.core.protos.generated import streaming_pb2_grpc/' src/core/protos/generated/streaming_pb2.py
	
	# Создаем пустой __init__.py
	touch src/core/protos/generated/__init__.py
	
install:
	poetry add grpcio grpcio-tools

run:
	poetry run python3 main.py

clean:
	rm -rf src/core/protos/generated/*