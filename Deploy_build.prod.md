# Build production AntiGoumin → Docker Hub → Dokploy

Registre Docker Hub cible :

```text
ciacems/agm:backend-latest
ciacems/agm:frontend-latest
```

## Option A : build local + push Docker Hub

À utiliser quand le quota du builder cloud est atteint.

Créer une seule fois un builder local multi-plateforme :

```sh
docker buildx create --name agm-local --driver docker-container --use \
  --driver-opt network=host 2>/dev/null || docker buildx use agm-local
```

S'authentifier sur Docker Hub :

```sh
docker login
```

Si la machine n'est pas `amd64`, activer QEMU pour cross-compiler vers `linux/amd64` :

```sh
docker run --privileged --rm tonistiigi/binfmt --install amd64
```

Charger les variables de build (depuis la racine du projet) :

```sh
set -a && source .env && set +a
```

Build des deux images en local sans cache, puis push :

```sh
docker buildx bake -f docker-compose.buildprod.yml \
  --builder agm-local --no-cache --push
```

Build des deux images en local avec cache, puis push :

```sh
docker buildx bake -f docker-compose.buildprod.yml \
  --builder agm-local --push
```

## Option B : build cloud

À utiliser quand le quota du builder cloud est disponible.

```sh
set -a && source .env && set +a

docker buildx bake -f docker-compose.buildprod.yml \
  --builder cloud-ciacems-ciacems-builder --push
```

Build uniquement le frontend :

```sh
docker buildx bake -f docker-compose.buildprod.yml frontend \
  --builder cloud-ciacems-ciacems-builder --push
```

Build uniquement le backend :

```sh
docker buildx bake -f docker-compose.buildprod.yml backend \
  --builder cloud-ciacems-ciacems-builder --push
```

## Variables de build utiles

API de production (phase 1) :

```sh
VITE_API_BASE_URL=https://antigoumin-api.ciacems.site
```

API de production (phase 2 — domaines finaux) :

```sh
VITE_API_BASE_URL=https://api.antigoumin.net
```

Google OAuth (même Client ID que le backend) :

```sh
VITE_GOOGLE_CLIENT_ID=<votre-client-id>.apps.googleusercontent.com
```

Changer les tags au moment du build :

```sh
BACKEND_IMAGE=ciacems/agm:backend-2026-08-20 \
FRONTEND_IMAGE=ciacems/agm:frontend-2026-08-20 \
docker buildx bake -f docker-compose.buildprod.yml \
  --builder cloud-ciacems-ciacems-builder --push
```

## Déploiement Dokploy

Créer deux services depuis les images Docker Hub :

| Service  | Image |
|----------|-------|
| Backend  | `ciacems/agm:backend-latest` |
| Frontend | `ciacems/agm:frontend-latest` |

Variables backend Dokploy (minimum) :

```sh
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<secret>
DJANGO_ALLOWED_HOSTS=antigoumin-api.ciacems.site,api.antigoumin.net
CORS_ALLOWED_ORIGINS=https://antigoumin.ciacems.site,https://antigoumin.net
CSRF_TRUSTED_ORIGINS=https://antigoumin.ciacems.site,https://antigoumin.net,https://antigoumin-api.ciacems.site,https://api.antigoumin.net
DATABASE_URL=postgres://<user>:<password>@<host>:5432/<db>
REDIS_URL=redis://<host-redis>:6379/1
JWT_SECRET_KEY=<secret>
GOOGLE_OAUTH_CLIENT_ID=<client-id>.apps.googleusercontent.com
```

Volumes Dokploy (Advanced) :

```text
agm-media   → /app/media
agm-static  → /app/staticfiles
```
