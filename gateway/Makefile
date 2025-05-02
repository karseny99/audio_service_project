generate:
	python -m grpc_tools.protoc \
		-Iuser_context/protos \
		--python_out=. \
		--grpc_python_out=. \
		user_context/protos/commands.proto
	
	# Автоматическое исправление импортов
	sed -i 's/^import commands_pb2/from user_context.generated import commands_pb2/' user_context/generated/*.py
	sed -i 's/^import commands_pb2_grpc/from user_context.generated import commands_pb2_grpc/' user_context/generated/*.py
	
	# Создаем пустой __init__.py
	touch user_context/generated/__init__.py

install:
	pip3 install grpcio grpcio-tools