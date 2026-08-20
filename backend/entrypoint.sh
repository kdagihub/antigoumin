#!/bin/bash
set -e

if [ "$#" -gt 0 ]; then
  exec "$@"
fi

echo "En attente de PostgreSQL..."
until python - <<'EOF'
import os
import psycopg2

psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    port=os.environ.get("POSTGRES_PORT", "5432"),
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    dbname=os.environ["POSTGRES_DB"],
)
EOF
do
  sleep 1
done
echo "PostgreSQL est prêt."

python manage.py migrate --noinput

if [ "${DJANGO_DEBUG:-False}" = "True" ]; then
  exec uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --reload
else
  exec gunicorn config.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-2}"
fi
