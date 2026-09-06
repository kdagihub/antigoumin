export const fidelityPageCopy = {
  eyebrow: 'Clarification amoureuse',
  title: 'Test de fidélité',
  subtitle:
    'Invitez une personne à clarifier son statut amoureux — identifiable, volontaire et sans piège. Elle reçoit votre demande par SMS et choisit librement de répondre, refuser ou ignorer.',
  priceTag: '550 FCFA / test',
  payTitle: 'Prêt à lancer le test ?',
  payBody:
    'L’envoi de votre test de fidélité nécessite des frais de traitement à seulement 550 FCFA. La personne verra qui vous êtes et pourra répondre en toute liberté.',
  payCta: 'PAYER LES FRAIS',
  formTitle: 'Nouveau test de fidélité',
  formHint: 'Paiement validé — saisissez le numéro à inviter.',
  vipFormHint: 'Forfait Premium — 1 test inclus ce mois. Saisissez le numéro à inviter.',
  vipQuotaExhausted:
    'Votre test inclus ce mois est utilisé. Payez 550 FCFA pour en envoyer un autre.',
  targetPhoneLabel: 'Numéro à tester',
  targetPhoneHint: 'Numéros ivoiriens (+225) uniquement.',
  formNotice:
    'La personne verra votre identité AntiGoumin. Son silence ne signifie ni oui ni non — seulement qu’elle n’a pas répondu.',
  submitLabel: 'Envoyer le test de fidélité',
  historyTitle: 'Vos tests',
  historyEmpty:
    'Aucun test lancé pour le moment. Quand vous serez prêt·e, votre première demande apparaîtra ici.',
  paymentSuccess: 'Paiement confirmé. Lancez votre test ci-dessous.',
  sendSuccess:
    'Test envoyé. La personne recevra un SMS identifiable avec un lien de réponse volontaire.',
} as const

export const fidelityStatusCopy: Record<
  'PENDING' | 'ACCEPTED' | 'REFUSED' | 'EXPIRED' | 'BLOCKED' | 'REPORTED',
  { label: string; severity: 'success' | 'warn' | 'danger' | 'secondary' | 'info' }
> = {
  PENDING: { label: 'En attente de réponse', severity: 'warn' },
  ACCEPTED: { label: 'Réponse reçue', severity: 'success' },
  REFUSED: { label: 'Invitation déclinée', severity: 'secondary' },
  EXPIRED: { label: 'Délai expiré', severity: 'secondary' },
  BLOCKED: { label: 'Bloquée', severity: 'danger' },
  REPORTED: { label: 'Signalée', severity: 'danger' },
}

export const fidelityDeclaredStatusLabels: Record<string, string> = {
  ENGAGED: 'En couple',
  AVAILABLE: 'Disponible',
  PREFER_NOT_TO_ANSWER: 'Préfère ne pas répondre',
}

export const fidelityServiceCopy = {
  title: 'Test de fidélité',
  description:
    'Besoin de clarté ? Envoyez une invitation officielle et identifiable pour que la personne clarifie son statut amoureux — sans ambiguïté, sans anonymat, sans pression.',
  ctaLabel: 'Lancer un test',
} as const

export const fidelityPricingCopy = {
  title: 'Demande de Transparence (Test de fidélité)',
  price: '550 FCFA',
  priceSuffix: '/ demande',
  tagline: 'Le test de fidélité responsable, officiel et identifiable',
  features: [
    'L’auteur est identifié auprès du destinataire',
    'Acceptation, refus, ignore ou signalement',
    'Réponse privée, jamais publiée d’office',
    'Le silence n’est pas une preuve',
  ],
  buttonLabel: 'Envoyer une demande',
} as const
