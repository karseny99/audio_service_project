generate:
	mkdir -p src/core/protos/generated
	
	# Генерируем код
	python -m grpc_tools.protoc \
		-I./src/core/protos \
		--python_out=./src/core/protos/generated \
		--grpc_python_out=./src/core/protos/generated \
		./src/core/protos/commands.proto
		
	# Автоматическое исправление импортов
	sed -i 's/^import commands_pb2/from src.core.protos.generated import commands_pb2/' src/core/protos/generated/commands_pb2_grpc.py
	sed -i 's/^import commands_pb2_grpc/from src.core.protos.generated import commands_pb2_grpc/' src/core/protos/generated/commands_pb2.py
	
	# Создаем пустой __init__.py
	touch src/core/protos/generated/__init__.py
	
install:
	pip3 install grpcio grpcio-tools