#!/usr/bin/env bash
set -euo pipefail

if [ ! -f alembic.ini ]; then
  echo "=== Initializing Alembic migrations ==="
  alembic init alembic
  # сюда нужно автоматически подставить правильный sqlalchemy.url в alembic.ini,
  # либо держать уже готовый шаблон alembic.ini в репо
fi

export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://user:1@localhost:5432/audio_db}"

if [ -z "$(ls alembic/versions/*.py 2>/dev/null)" ]; then
  echo "=== Generating initial revision ==="
  alembic revision --autogenerate -m "Initial schemas for all contexts"
fi

echo "=== Applying migrations (upgrade head) ==="
alembic upgrade head

echo "=== DB is up to date ==="
