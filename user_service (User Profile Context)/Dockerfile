# ---------------- Stage 1: Builder ----------------
FROM python:3.10-slim AS builder

# рабочая директория
WORKDIR /app

# Установим нужные системные зависимости для asyncpg и grpc
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы Poetry
COPY pyproject.toml poetry.lock ./

# Устанавливаем Poetry и зависимости без создания venv
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && export PATH="/root/.local/bin:$PATH" \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Копируем исходники
COPY . .

# ---------------- Stage 2: Runtime ----------------
FROM python:3.10-slim

WORKDIR /app

# Копируем Poetry (CLI) из билдера
COPY --from=builder /root/.local /root/.local
ENV PATH="/root/.local/bin:$PATH"

# Копируем установленную среду из билдера
COPY --from=builder /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем ваш код
COPY --from=builder /app /app

# Открываем порт gRPC
EXPOSE 50051

# По умолчанию запускаем вашу точку входа
# Предполагаем, что в main.py у вас вызывается serve_grpc()
CMD ["poetry", "run", "python3", "-u", "src/main.py"]
