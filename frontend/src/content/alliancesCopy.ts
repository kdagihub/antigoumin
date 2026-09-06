export const alliancesPageCopy = {
  eyebrow: 'Alertes & confiance',
  title: 'Mes Alliances digitales',
  subtitle:
    'Scellez votre lien après une relation certifiée. Soyez alerté si votre partenaire engage ou sollicite une autre relation — sans révéler l’identité du tiers.',
  priceTag: '1200 FCFA / mois',
  payTitle: 'Sceller une Alliance Premium',
  payBody:
    'Choisissez une relation certifiée, puis activez l’abonnement à 1200 FCFA/mois. Votre partenaire devra accepter pour sceller l’Alliance.',
  payCta: 'PAYER ET INVITER',
  formHint: 'Sélectionnez la relation sur laquelle bâtir votre Alliance.',
  relationLabel: 'Relation certifiée',
  historyTitle: 'Historique des Alliances',
  historyEmpty: 'Aucune Alliance pour le moment. Votre sceau apparaîtra ici une fois scellé.',
  alertsTitle: 'Alertes Alliance',
  alertsEmpty:
    'Aucune alerte pour le moment. Vous serez informé si votre partenaire est déclaré ou sollicité par un tiers, sans révéler l’identité du déclarant.',
  activeTitle: 'Alliance scellée',
  badgeLabel: 'Afficher mon badge Alliance',
  badgeHint: 'Le badge est optionnel et indépendant pour chaque partie.',
  visibilityTitle: 'Ma visibilité publique',
} as const

export const subscriptionPageCopy = {
  title: 'Service Premium',
  heroLine: 'Alertes Alliance — 1200 FCFA / mois',
  intro:
    'Soyez alerté si votre partenaire engage ou sollicite une autre relation. Notification discrète, sans révéler qui a agi.',
  benefits: [
    'Alerte si votre partenaire est déclaré par un tiers',
    'Alerte si une nouvelle relation lui est proposée',
    '5 vérifications · 1 déclaration · 1 test / mois',
    'Badge Alliance optionnel',
    'Visibilité de votre statut (masquer ou afficher)',
  ],
  subscribeCta: 'SCeller MON ALLIANCE — 1200 FCFA',
  declareCta: 'DÉCLARER MON AMOUR',
  declareHint: 'Étape 1 sur 2 — relation certifiée requise.',
  activeTitle: 'Premium actif',
  activeUntil: 'Jusqu’au',
  renewCta: 'RENOUVELER — 1200 FCFA',
  expiredTag: 'Premium expiré',
  expiringTag: (days: number) =>
    days === 1 ? 'Expire demain' : `Expire dans ${days} jours`,
  stepDeclare: 'Déclarer',
  stepAlliance: 'Sceller l’Alliance',
  quotaTitle: 'Forfait mensuel inclus',
  quotaVerification: 'Vérifications',
  quotaDeclaration: 'Déclarations',
  quotaTransparency: 'Tests de fidélité',
} as const
