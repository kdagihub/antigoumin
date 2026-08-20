# 📘 AntiGoumin - Documentation Projet (CDC, DCT, Specs)

Ce document centralise le Cahier des Charges (CDC), les Spécifications (Specs), et le Document de Conception Technique (DCT) pour le projet **AntiGoumin**. Il est conçu pour être directement utilisable comme contexte pour un IDE assisté par IA tel que Cursor ou Windsurf.

---

## 1. Cahier des Charges (CDC)

### 1.1. Contexte et Concept
**AntiGoumin** est une application web mobile (PWA) de "registre de confiance" pour les couples. Elle permet de déclarer une relation et de la faire valider par le partenaire via une double vérification (OTP SMS/Email). L'objectif est de lutter contre les fausses déclarations unilatérales et de fournir un espace où la fidélité et le sérieux d'une relation peuvent être "vérifiés" par un tiers.

### 1.2. Public Cible & Marché
*   **Marché principal** : Côte d'Ivoire (et extension Afrique de l'Ouest).
*   **Cible** : Jeunes adultes, utilisateurs de réseaux sociaux, habitués aux paiements Mobile Money.

### 1.3. Modèle Économique (Monétisation)
*   **Paywall / Abonnement** : 200 FCFA / mois (via Mobile Money : Wave, Orange, MTN, via agrégateur type Fedapay ou CinetPay).
*   **Droits de l'abonnement** : Permet 3 déclarations maximum par mois et un accès illimité à la levée du floutage sur les recherches.
*   **Hors abonnement** : La recherche fonctionne, mais les résultats (Photo et Nom du partenaire) sont floutés. L'utilisateur doit payer pour voir.

### 1.4. User Flow Principal
1.  **Inscription** : L'auteur (User A) s'inscrit avec son numéro de téléphone.
2.  **Déclaration** : User A déclare User B (Numéro obligatoire, Email facultatif, Nom/Prénom, Photo). Le statut est `PENDING` (invisible publiquement).
3.  **Validation (Le Pivot)** : User B reçoit un SMS avec un lien unique (ex: `antigoumin.ci/v/xyz`). User B clique et valide ("Oui, j'accepte"). Le statut passe à `VERIFIED`.
4.  **Recherche Tierce** : User C cherche le numéro de User B. Le profil de User A apparaît (flouté). User C paie 200 FCFA pour déflouter.

---

## 2. Spécifications Techniques (Specs)

### 2.1. Stack Technologique
*   **Backend** : Python, Django, Django Ninja (pour des APIs asynchrones, rapides et auto-documentées avec Swagger/OpenAPI).
*   **Base de données principale** : PostgreSQL.
*   **Mise en cache & OTP** : **Redis (OUI)**.
    *   *Justification* : Redis est extrêmement léger et indispensable ici pour deux choses vitales : 
        1.  Stocker les codes/liens OTP avec un *Time-To-Live* (TTL) de 15 minutes.
        2.  Faire du **Rate-Limiting** sur les routes d'envoi de SMS pour éviter qu'un bot ne vide le solde de l'API SMS.
*   **Gestion des tâches asynchrones** : **PAS DE CELERY** (dans un premier temps).
    *   *Justification* : Pour garder l'infrastructure légère, les envois d'emails et de SMS seront gérés par les `BackgroundTasks` natives (si migration vers FastAPI/Starlette) ou via des threads/async natif de Django Ninja, sans nécessiter un worker séparé lourd.
*   **Frontend** : Vue.js 3 (Composition API), intégré en tant que PWA. CSS via TailwindCSS.

### 2.2. Infrastructure et DevOps
*   **Conteneurisation** : Dockerisation complète (Local et Production).
*   **CI/CD & Déploiement** :
    1.  Build de l'image (Backend + Frontend via multi-stage ou séparés).
    2.  Push vers **Docker Hub**.
    3.  Pull et déploiement sur serveur (VPS) via **Dokploy**.
    4.  Gestion des domaines et certificats SSL via le Traefik de Dokploy.

---

## 3. Document de Conception Technique (DCT)

### 3.1. Modèles de Données (PostgreSQL)

```python
# Utilisateur
class User(AbstractBaseUser):
    phone_number = CharField(unique=True)
    is_active = BooleanField(default=True)
    subscription_end_date = DateTimeField(null=True) # Gère l'accès au défloutage

# Declaration
class Declaration(Model):
    author = ForeignKey(User, on_delete=CASCADE, related_name='declarations_made')
    partner_phone = CharField(max_length=15) # Le numéro cherché par les tiers
    partner_name = CharField(max_length=100)
    partner_photo = ImageField(upload_to='declarations/')
    status = CharField(choices=[('PENDING', 'Pending'), ('VERIFIED', 'Verified'), ('REJECTED', 'Rejected')])
    created_at = DateTimeField(auto_now_add=True)

# Transaction / Paiement
class Payment(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    amount = IntegerField(default=200)
    reference = CharField(unique=True) # Ref de l'agrégateur (Wave, CinetPay)
    status = CharField(choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed')])
    created_at = DateTimeField(auto_now_add=True)
```

### 3.2. Architecture Docker (docker-compose)
L'environnement local aura 3 services :
1.  `db`: `postgres:15-alpine`
2.  `redis`: `redis:7-alpine`
3.  `backend`: Django Ninja tournant sur Daphne (ASGI).
(Le frontend Vue.js peut tourner en local sur Vite `npm run dev`, et en prod, il sera buildé et servi par Nginx dans un conteneur séparé ou par Django).

### 3.3. Endpoints de l'API (Django Ninja)
*   `POST /api/auth/register-login` : Connexion/Inscription via OTP.
*   `POST /api/declarations/` : Créer une déclaration (upload photo + envoie OTP en background).
*   `GET /api/declarations/verify/{token}` : Route accédée par le partenaire pour valider.
*   `GET /api/search/?phone={num}` : Recherche. Renvoie les infos avec un flag `is_blurred: true` si l'utilisateur requérant n'a pas d'abonnement actif.
*   `POST /api/payments/webhook/` : Route sécurisée recevant la confirmation de paiement de l'agrégateur.

---

## 4. Prompt Cursor / Windsurf (À copier-coller)

Copiez le prompt ci-dessous dans le *Composer* (Ctrl+I / Cmd+I) de votre IDE pour générer la structure initiale du projet :

```text
Je veux initialiser un nouveau projet nommé "AntiGoumin". C'est un projet Dockerisé avec un backend Django + Django Ninja et une base de données PostgreSQL. Nous utiliserons également Redis pour le cache/rate-limiting, sans Celery.

Agis en tant qu'Expert DevOps et Python Backend Developer. Effectue les tâches suivantes :

1. Crée un fichier `docker-compose.yml` pour le développement local comprenant :
   - Un service `db` (postgres:15-alpine) avec un volume.
   - Un service `redis` (redis:7-alpine).
   - Un service `backend` (Python 3.11, basé sur un Dockerfile local) qui expose le port 8000, dépend de db et redis, et monte le dossier courant en volume.

2. Crée le `Dockerfile` pour le backend (installation de requirements.txt, copie du code, exposition port 8000).

3. Génère le fichier `requirements.txt` contenant au minimum : django, django-ninja, psycopg2-binary, redis, pillow, daphne.

4. Initie un script `entrypoint.sh` pour le backend qui attend que la BDD soit prête, exécute les migrations (`python manage.py migrate`), et lance le serveur avec Daphne.

5. Enfin, crée le dossier racine du projet Django (`backend/`) avec une application `core`. Dans `core/models.py`, définis les modèles suivants : 
   - Un modèle Custom User basé sur AbstractBaseUser (identifiant principal: phone_number, inclure subscription_end_date).
   - Un modèle Declaration (author: FK vers User, partner_phone, partner_name, partner_photo, status: PENDING/VERIFIED/REJECTED).
   - Un modèle Payment (user: FK, amount, reference, status).

6. Configure `settings.py` pour utiliser PostgreSQL et Redis en tant que cache par défaut.

Structure bien les dossiers pour que je puisse facilement builder l'image, la push sur Docker Hub, et la déployer sur Dokploy par la suite.
```
