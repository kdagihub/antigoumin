Voici où en est le projet AntiGoumin et ce qu’il reste à faire.

---

## Où nous en sommes

### Backend — opérationnel
| Domaine | État |
|---------|------|
| Auth (email, Google OAuth, JWT) | ✅ |
| Vérification compte (email **ou** téléphone suffit) | ✅ |
| Mot de passe oublié par email | ✅ *(code fait, pas encore commité)* |
| Notifications SMS (D7) + email (Hostinger) | ✅ |
| Formulaire contact public | ✅ |
| Paiements GeniusPay (checkout + webhooks) | ✅ sandbox |
| Recherche statut matrimonial par numéro | ✅ API avec 4 résultats distincts |
| Déclarations, transparence, alliances | ✅ API backend |
| Règle VIP : seuls les abonnés peuvent masquer leur statut | ✅ |

### Frontend — partiellement branché
| Écran | État |
|-------|------|
| Landing (hero, tarifs, FAQ, contact) | ✅ |
| Inscription / connexion / mot de passe oublié | ✅ |
| Espace `/app` (sidebar PC + menu mobile) | ✅ |
| **Vérifier un numéro** (`/app/verification`) | ✅ workflow complet |
| Profil + banderole de vérification | ✅ |
| Accueil dashboard (stats simulées) | ⚠️ placeholder |
| **Mes déclarations** | ❌ placeholder |
| **Tests de fidélité / transparence** | ❌ placeholder |
| **Mes alliances** | ❌ placeholder |
| Abonnement | ⚠️ affichage basique |

### Infra & déploiement
- Docker local : ✅
- Images prod Docker Hub : ✅
- GeniusPay **live** + webhook en prod : ❌ à configurer
- Variables prod (`FRONTEND_BASE_URL`, clés live) : ❌
- Commit des derniers travaux (vérif + reset password) : ❌ en attente

---

## Prochaines étapes (ordre recommandé)

### 1. Committer le travail en cours
Tout ce qui est fait depuis le dernier commit (`fe7538e`) : workflow vérification, reset password, règles VIP/search.

### 2. Module **Mes déclarations** *(priorité métier)*
- Formulaire de déclaration après paiement (300 FCFA)
- Invitation d’un non-membre (cas « pas encore sur AntiGoumin » depuis la vérification)
- Acceptation/refus partenaire (`/v/:token` existe déjà)
- Liste des déclarations dans le dashboard

### 3. Module **Tests de fidélité / transparence**
- Envoi de demande identifiable après paiement (550 FCFA)
- Page de réponse (`/transparence/:token`)
- Historique dans le dashboard

### 4. Module **Alliances digitales**
- Souscription VIP (990 FCFA/mois) après relation certifiée
- Acceptation bilatérale, badge, gestion visibilité
- Écran dashboard alliances

### 5. Dashboard accueil — données réelles
- Remplacer les stats simulées par les vrais compteurs API
- Fil d’activité réel (déclarations, recherches, etc.)

### 6. Mise en production
- Clés GeniusPay **live** + secret webhook `whsec_…`
- URL webhook enregistrée chez GeniusPay
- Variables prod (domaines, CORS, SMTP)
- Déploiement Dokploy / Docker Hub
- Boîtes mail `contact@` et `privacy@` finalisées

### 7. Finitions produit
- PWA installable (manifest / service worker)
- Tests E2E des parcours paiement
- Mise à jour CGU / specs si besoin

---

## En résumé

Le **cœur technique** est solide : auth, paiements, recherche par numéro, notifications.  
Ce qui manque surtout, c’est le **branchement des écrans métier** dans le dashboard (déclarations → transparence → alliances) et la **mise en prod**.

Tu veux qu’on enchaîne par le **commit** puis le module **Mes déclarations** ?