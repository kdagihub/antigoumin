# Build production AntiGoumin → Docker Hub → Dokploy

Registre Docker Hub cible :

```text
ciacems/agm:backend-latest
ciacems/agm:frontend-latest
```

Builder cloud Docker Hub (usage habituel) :

```text
cloud-ciacems-ciacems-builder
```

## Option A : build cloud (recommandé)

À utiliser en priorité tant que le quota du builder cloud est disponible.

S'authentifier sur Docker Hub :

```sh
docker login
```

### Backend + frontend

```sh
VITE_API_BASE_URL=https://api.antigoumin.live \
VITE_GOOGLE_CLIENT_ID=819138748962-i19mae2hh44dqbeg7d4ds9bt1m6bm9jm.apps.googleusercontent.com \
VITE_PRIMEVUE_LICENSE_KEY=eyJpZCI6IjdiYWJiN2JiLWRjMjEtNGExOC05NjNiLTI2YTNmM2YzNTM4YSIsInByb2R1Y3QiOiJwcmltZXVpIiwidGllciI6ImNvbW11bml0eSIsInR5cGUiOiJkZXYiLCJpYXQiOjE3ODcyODcxNjEsImV4cCI6MTgxODgyMzE2MX0 \
docker buildx bake -f docker-compose.buildprod.yml \
  --builder cloud-ciacems-ciacems-builder --push
```

### Frontend seul

```sh
VITE_API_BASE_URL=https://api.antigoumin.live \
VITE_GOOGLE_CLIENT_ID=<votre-client-id>.apps.googleusercontent.com \
VITE_PRIMEVUE_LICENSE_KEY=<votre-clé-primeui> \
docker buildx bake -f docker-compose.buildprod.yml frontend \
  --builder cloud-ciacems-ciacems-builder --push
```

### Backend seul

```sh
docker buildx bake -f docker-compose.buildprod.yml backend \
  --builder cloud-ciacems-ciacems-builder --push
```

### Staging (domaine CIACEMS, phase 1)

```sh
VITE_API_BASE_URL=https://antigoumin-api.ciacems.site \
VITE_GOOGLE_CLIENT_ID=<votre-client-id>.apps.googleusercontent.com \
VITE_PRIMEVUE_LICENSE_KEY=<votre-clé-primeui> \
docker buildx bake -f docker-compose.buildprod.yml frontend \
  --builder cloud-ciacems-ciacems-builder --push
```

### Tags datés (optionnel)

```sh
BACKEND_IMAGE=ciacems/agm:backend-2026-08-27 \
FRONTEND_IMAGE=ciacems/agm:frontend-2026-08-27 \
VITE_API_BASE_URL=https://api.antigoumin.live \
VITE_GOOGLE_CLIENT_ID=<votre-client-id>.apps.googleusercontent.com \
VITE_PRIMEVUE_LICENSE_KEY=<votre-clé-primeui> \
docker buildx bake -f docker-compose.buildprod.yml \
  --builder cloud-ciacems-ciacems-builder --push
```

## Option B : build local + push Docker Hub

À utiliser uniquement quand le quota du builder cloud est atteint.

Créer une seule fois un builder local multi-plateforme :

```sh
docker buildx create --name agm-local --driver docker-container --use \
  --driver-opt network=host 2>/dev/null || docker buildx use agm-local
```

Si la machine n'est pas `amd64`, activer QEMU pour cross-compiler vers `linux/amd64` :

```sh
docker run --privileged --rm tonistiigi/binfmt --install amd64
```

Mêmes variables `VITE_*` qu'en cloud, en remplaçant le builder :

```sh
VITE_API_BASE_URL=https://api.antigoumin.live \
VITE_GOOGLE_CLIENT_ID=<votre-client-id>.apps.googleusercontent.com \
VITE_PRIMEVUE_LICENSE_KEY=<votre-clé-primeui> \
docker buildx bake -f docker-compose.buildprod.yml \
  --builder agm-local --push
```

Sans cache :

```sh
docker buildx bake -f docker-compose.buildprod.yml \
  --builder agm-local --no-cache --push
```

## Variables de build `VITE_*` (frontend)

Les variables `VITE_*` sont **figées dans le JavaScript** au moment du `npm run build`.
Elles ne se configurent **pas** sur Dokploy au runtime : seulement sur la ligne de commande de build.

| Variable | Valeur prod | Valeur staging |
|----------|-------------|----------------|
| `VITE_API_BASE_URL` | `https://api.antigoumin.live` | `https://antigoumin-api.ciacems.site` |
| `VITE_GOOGLE_CLIENT_ID` | = `GOOGLE_OAUTH_CLIENT_ID` backend | idem |
| `VITE_PRIMEVUE_LICENSE_KEY` | clé [primeui.dev](https://primeui.dev) | idem |

**Attention** : ne pas faire `source .env` avant le bake si ce fichier contient
`VITE_API_BASE_URL=http://localhost:8000` — cette valeur écrase le défaut du compose file
et part dans l'image. Passez les `VITE_*` **explicitement** sur la commande (comme ci-dessus).

Le `frontend/.env` local est ignoré par Docker (`.dockerignore`) ; seules comptent les variables
passées en préfixe de commande ou exportées dans le shell **avant** le bake.

Si `VITE_API_BASE_URL` est omise, le défaut du `docker-compose.buildprod.yml` est
`https://api.antigoumin.live` — mais `VITE_GOOGLE_CLIENT_ID` et `VITE_PRIMEVUE_LICENSE_KEY`
doivent toujours être fournis pour Google Sign-In et la licence PrimeVue.

### Dépannage « Invalid PrimeUI License »

1. **Dokploy ne sert à rien pour cette variable** : le frontend est du HTML/JS statique.
   Mettre `VITE_PRIMEVUE_LICENSE_KEY` dans les variables Dokploy du service frontend **n'a aucun effet**.

2. **La clé doit être sur la commande de build cloud**, entre guillemets si besoin :
   ```sh
   VITE_PRIMEVUE_LICENSE_KEY='eyJ...votre.jwt' \
   docker buildx bake -f docker-compose.buildprod.yml frontend \
     --builder cloud-ciacems-ciacems-builder --push
   ```

3. **Vérifier que la clé est dans le bundle** (après build local) :
   ```sh
   rg "eyJ" frontend/dist/assets/index-*.js
   ```
   Si rien ne sort → la clé n'a pas été injectée.

4. **Console navigateur** (F12) : chercher `[PrimeUI]` — le message indique
   `missing`, `expired`, `tampered`, etc.

5. **Renouveler la clé** sur [primeui.dev](https://primeui.dev) si expirée
   (licence Community = validité 12 mois, renouvellement gratuit).

6. **Redéployer** le service frontend Dokploy après le push de la nouvelle image
   (`ciacems/agm:frontend-latest`).

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
DJANGO_ALLOWED_HOSTS=antigoumin-api.ciacems.site,api.antigoumin.live
CORS_ALLOWED_ORIGINS=https://antigoumin.ciacems.site,https://antigoumin.live,https://www.antigoumin.live
CSRF_TRUSTED_ORIGINS=https://antigoumin.ciacems.site,https://antigoumin.live,https://www.antigoumin.live,https://antigoumin-api.ciacems.site,https://api.antigoumin.live
FRONTEND_BASE_URL=https://antigoumin.live
DATABASE_URL=postgres://<user>:<password>@<host>:5432/<db>
REDIS_URL=redis://<host-redis>:6379/1
JWT_SECRET_KEY=<secret>
GOOGLE_OAUTH_CLIENT_ID=<client-id>.apps.googleusercontent.com
D7_TOKEN=<token>
D7_CLIENT_ID=<client-id>
D7_CLIENT_SECRET=<client-secret>
D7_ORIGINATOR=AntiGoumin
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=465
EMAIL_USER=contact@antigoumin.live
EMAIL_PASSWORD=<mot-de-passe>
EMAIL_USE_SSL=True
DEFAULT_FROM_EMAIL=AntiGoumin <contact@antigoumin.live>
```

Volumes Dokploy (Advanced) :

```text
agm-media   → /app/media
agm-static  → /app/staticfiles
```
