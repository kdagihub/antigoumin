# Frontend AntiGoumin

Application PWA Vue 3 + PrimeVue pour le registre de confiance AntiGoumin.

## Stack

- Vue 3 (Composition API) + TypeScript
- Vue Router + Pinia
- PrimeVue + PrimeIcons
- Axios (client API)
- Tailwind CSS v4
- Vite PWA

## Charte visuelle

- **Couleurs** : bleu turquoise (`#0E7490`) + rose corail (`#E11D48`) sur fond menthe clair (`#F0FDFA`)
- **Typographie** : Plus Jakarta Sans (titres) + Figtree (corps)
- **Icônes** : PrimeIcons uniquement (pas d'émoticônes)
- **Accessibilité** : contrastes WCAG AA, focus visible, labels explicites

## Démarrage local

Prérequis : Node.js 22+, backend Django sur le port 8000.

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

- App : http://localhost:5173
- API : http://localhost:8000/api/

Variables dans `.env` :

| Variable | Description |
|---|---|
| `VITE_API_BASE_URL` | URL du backend (ex. `http://localhost:8000`) |
| `VITE_GOOGLE_CLIENT_ID` | Client ID Google OAuth (connexion Google) |

## Scripts

```bash
npm run dev          # Serveur de développement
npm run build        # Build production
npm run preview      # Prévisualiser le build
npm run test:unit    # Tests Vitest
npm run lint         # ESLint + Oxlint
```

## Pages

| Route | Description |
|---|---|
| `/` | Accueil public |
| `/connexion` | Connexion email / Google |
| `/inscription` | Création de compte |
| `/profil` | Profil utilisateur (authentifié) |
| `/v/:token` | Placeholder validation partenaire (SMS) |

## Build Docker (production)

L'image est construite via `Dockerfile.prod` et publiée sur Docker Hub (`ciacems/agm:frontend-latest`).

```bash
docker buildx bake -f ../docker-compose.buildprod.yml frontend --push
```
