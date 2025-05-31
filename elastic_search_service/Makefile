generate:
	mkdir -p src/core/protos/generated

	# Генерируем код для track_search
	poetry run python3 -m grpc_tools.protoc \
		-I./src/core/protos \
		--python_out=./src/core/protos/generated \
		--pyi_out=./src/core/protos/generated \
		./src/core/protos/track_search.proto
	
	# Исправляем импорты для track_search
	sed -i 's/^import track_search_pb2/from src.core.protos.generated import track_search_pb2/' src/core/protos/generated/*.py

	# Создаем пустой __init__.py
	touch src/core/protos/generated/__init__.py

install:
	poetry install

run:
	poetry run python3 main.py

clean:
	rm -rf src/core/protos/generated/*