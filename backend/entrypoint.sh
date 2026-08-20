#!/bin/bash
set -e

if [ "$#" -gt 0 ]; then
  exec "$@"
fi

echo "En attente de PostgreSQL..."
until python - <<'EOF'
import os
from urllib.parse import unquote, urlparse

import psycopg2


def get_conn_params():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        parsed = urlparse(database_url)
        return {
            "host": parsed.hostname,
            "port": parsed.port or 5432,
            "user": unquote(parsed.username or ""),
            "password": unquote(parsed.password or ""),
            "dbname": parsed.path.lstrip("/"),
        }

    return {
        "host": os.environ["POSTGRES_HOST"],
        "port": int(os.environ.get("POSTGRES_PORT", "5432")),
        "user": os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"],
        "dbname": os.environ["POSTGRES_DB"],
    }


psycopg2.connect(**get_conn_params())
EOF
do
  sleep 1
done
echo "PostgreSQL est prêt."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

PORT="${BACKEND_PORT:-8000}"

if [ "${DJANGO_DEBUG:-False}" = "True" ]; then
  exec python manage.py runserver "0.0.0.0:${PORT}"
else
  exec daphne -b 0.0.0.0 -p "${PORT}" config.asgi:application
fi
