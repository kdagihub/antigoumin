# 📘 AntiGoumin - Documentation Projet (CDC, DCT, Specs)

Ce document centralise le Cahier des Charges (CDC), les Spécifications (Specs), et le Document de Conception Technique (DCT) pour le projet **AntiGoumin**. Il est conçu pour être directement utilisable comme contexte pour un IDE assisté par IA tel que Cursor ou Windsurf.

---

## 1. Cahier des Charges (CDC)

### 1.1. Contexte et Concept
**AntiGoumin** est une PWA de registre de confiance mutuelle. Elle permet de conserver une relation privée ou de certifier publiquement un statut binaire après double validation OTP. La recherche ne concerne que les numéros inscrits ayant accepté une certification publique active. La plateforme ne publie ni compteur de relations, ni identité, ni historique.

### 1.2. Public Cible & Marché
*   **Marché principal** : Côte d'Ivoire (et extension Afrique de l'Ouest).
*   **Cible** : Jeunes adultes, utilisateurs de réseaux sociaux, habitués aux paiements Mobile Money.

### 1.3. Modèle Économique (Hybride — Pay-per-action + Abonnement)

Quatre sources de revenus complémentaires :

| Service | Prix | Modèle |
|---|---|---|
| **Vérification** | 200 FCFA | Statut binaire pour un numéro inscrit avec certification publique active |
| **Déclaration** | 300 FCFA | Relation privée ou certification publique, toujours avec double validation OTP |
| **Demande de Transparence** | 550 FCFA | Invitation identifiable, volontaire, privée et non trompeuse |
| **Alliance Digitale VIP** | 1 200 FCFA/mois | Forfait d’actions, badge optionnel et notification neutre de fin |

*   **Confidentialité de la vérification** : avant paiement, aucune information ne révèle si le numéro existe ou refuse la consultabilité.
*   **Résultat** : `ENGAGED`, `AVAILABLE` ou `NOT_LISTED_OR_NOT_SEARCHABLE`.
*   **Alliance VIP** : aucune alerte ne révèle une autre relation ; chaque partie reçoit seulement une notification neutre si l’Alliance prend fin.

### 1.4. User Flow Principal
1.  **Inscription** : L'auteur (User A) s'inscrit avec son numéro de téléphone.
2.  **Déclaration** : User A choisit `PRIVATE` ou `PUBLIC_CERTIFIED`. La demande reste `PENDING` et invisible.
3.  **Validation** : User B voit le mode choisi et son effet avant d’accepter par OTP. Une certification publique rend uniquement le statut binaire « En couple » consultable.
4.  **Recherche Tierce** : User C paie **200 FCFA**. L’API ne retourne un statut que pour un numéro inscrit, consultable et certifié ; aucune identité ni donnée relationnelle détaillée n’est exposée.
5.  **Demande de Transparence** : l’auteur est identifié. Le destinataire peut répondre, refuser, ignorer, bloquer ou signaler. Le silence n’est pas une preuve.

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
    email = EmailField(unique=True)
    phone_number = CharField(blank=True)
    subscription_end_date = DateTimeField(null=True)  # Alliance Digitale VIP
    alliance_badge_enabled = BooleanField(default=False)
    is_status_searchable = BooleanField(default=False)

# Declaration
class Declaration(Model):
    author = ForeignKey(User)
    partner_phone = CharField(max_length=15)
    partner_name = CharField(max_length=100)
    partner_photo = ImageField(upload_to='declarations/')
    relation_type = CharField(choices=[AMOUR, FLIRT, FIANCE, MARIAGE])
    status = CharField(choices=[PENDING, VERIFIED, REJECTED, ENDED])
    visibility = CharField(choices=[PRIVATE, PUBLIC_CERTIFIED])
    accepted_by = ForeignKey(User, null=True)
    payment = ForeignKey(Payment, null=True)

# Paiement (multi-services)
class Payment(Model):
    service_type = CharField(choices=[VERIFICATION, DECLARATION, TRANSPARENCY_REQUEST, ALLIANCE_VIP])
    amount = IntegerField()
    reference = CharField(unique=True)
    status = CharField(choices=[SUCCESS, FAILED])
    consumed = BooleanField(default=False)
    metadata = JSONField(default=dict)

# Accès vérification débloquée (24h par numéro)
class PhoneVerificationAccess(Model):
    user = ForeignKey(User)
    phone = CharField(max_length=15)
    payment = ForeignKey(Payment)
    expires_at = DateTimeField()

# Demande de Transparence
class TransparencyRequest(Model):
    requester = ForeignKey(User)
    target_phone = CharField(max_length=15)
    token = CharField(unique=True)
    status = CharField(choices=[PENDING, ACCEPTED, REFUSED, EXPIRED, BLOCKED, REPORTED])
    declared_status = CharField(choices=[ENGAGED, AVAILABLE, PREFER_NOT_TO_ANSWER])
    expires_at = DateTimeField()
```

### 3.2. Architecture Docker (docker-compose)
L'environnement local aura 3 services :
1.  `db`: `postgres:15-alpine`
2.  `redis`: `redis:7-alpine`
3.  `backend`: Django Ninja tournant sur Daphne (ASGI).
(Le frontend Vue.js peut tourner en local sur Vite `npm run dev`, et en prod, il sera buildé et servi par Nginx dans un conteneur séparé ou par Django).

### 3.3. Endpoints de l'API (Django Ninja)
*   `GET /api/catalog/` : Tarifs et catalogue des 4 services.
*   `POST /api/auth/register`, `/login`, `/google` : Authentification JWT.
*   `GET /api/me` : Profil utilisateur (+ statut Alliance VIP).
*   `POST /api/declarations/` : Créer une déclaration (300 FCFA, multipart + `payment_id`).
*   `GET /api/declarations/partner-preview?phone=` : Prix et information de consentement, sans révéler d’autres relations.
*   `GET /api/declarations/verify/{token}` : Aperçu du mode privé/public avant décision.
*   `GET /api/search/?phone=` : Statut binaire après paiement (200 FCFA).
*   `POST /api/transparency-requests/` : Envoyer une invitation identifiable (550 FCFA).
*   `POST /api/transparency-requests/{token}/respond` : Répondre, refuser, bloquer ou signaler.
*   `POST /api/payments/webhook/` : Webhook agrégateur (`service_type`, `metadata`).

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
