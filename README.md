# AntiGoumin

Backend Django + Django Ninja, PostgreSQL et Redis, entièrement dockerisé.

## Structure

```
antigoumin/
├── docker-compose.yml           # Dev local (db, redis, backend)
├── docker-compose.buildprod.yml # Build prod → Docker Hub
├── Deploy_build.prod.md         # Commandes buildx (local / cloud)
├── backend/
│   ├── Dockerfile               # Dev local
│   ├── Dockerfile.prod          # Image prod (ciacems/agm)
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/
│   └── core/
└── frontend/
    ├── Dockerfile.prod          # Image prod (ciacems/agm:frontend-latest)
    └── nginx.conf
```

## Démarrage local

```bash
cd antigoumin
docker compose up --build
```

- API : http://localhost:8000/api/
- Swagger : http://localhost:8000/api/docs
- Healthcheck : http://localhost:8000/api/health
- Admin Django : http://localhost:8000/admin/

## Build & push Docker Hub (production)

Images attendues par Dokploy :

```text
ciacems/agm:backend-latest
ciacems/agm:frontend-latest
```

Build local + push (voir `Deploy_build.prod.md` pour le détail) :

```bash
docker buildx create --name agm-local --driver docker-container --use \
  --driver-opt network=host 2>/dev/null || docker buildx use agm-local

docker login

set -a && source .env && set +a

docker buildx bake -f docker-compose.buildprod.yml \
  --builder agm-local --push
```

Build cloud (si quota disponible) :

```bash
docker buildx bake -f docker-compose.buildprod.yml \
  --builder cloud-ciacems-ciacems-builder --push
```

Build backend seul :

```bash
docker buildx bake -f docker-compose.buildprod.yml backend \
  --builder agm-local --push
```

Variables d'environnement à configurer sur Dokploy :

| Variable | Description |
|---|---|
| `DJANGO_DEBUG` | `False` en production |
| `DJANGO_SECRET_KEY` | Clé secrète Django |
| `DJANGO_ALLOWED_HOSTS` | `antigoumin-api.ciacems.site,api.antigoumin.net` |
| `POSTGRES_*` | Connexion PostgreSQL |
| `REDIS_URL` | URL Redis (ex: `redis://redis:6379/1`) |
| `JWT_SECRET_KEY` | Secret de signature JWT |
| `GOOGLE_OAUTH_CLIENT_ID` | Client ID Google OAuth |
| `GUNICORN_WORKERS` | Nombre de workers (défaut: 2) |
