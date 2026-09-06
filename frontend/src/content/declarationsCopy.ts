export const declarationsPageCopy = {
  eyebrow: 'Votre histoire à deux',
  title: 'Déclarations amoureuses',
  subtitle:
    'Officialisez votre lien avec la personne que vous aimez. Invitez-la par SMS à confirmer — même si elle n’est pas encore sur AntiGoumin, elle recevra votre demande avec tendresse et clarté.',
  priceTag: '300 FCFA / invitation',
  payTitle: 'Prêt à déclarer votre amour ?',
  payBody:
    'L’envoi de votre invitation amoureuse nécessite des frais de traitement à seulement 300 FCFA. Votre partenaire recevra un SMS pour accepter ou refuser, en toute liberté.',
  payCta: 'PAYER LES FRAIS',
  formTitle: 'Nouvelle déclaration amoureuse',
  formHint: 'Paiement validé — il ne reste plus qu’à personnaliser votre invitation.',
  partnerPhoneLabel: 'Son numéro mobile',
  partnerNameLabel: 'Son prénom ou surnom',
  partnerNamePlaceholder: 'Le prénom qui apparaîtra dans l’invitation',
  partnerPhotoLabel: 'Une photo de votre moitié',
  partnerPhotoHint: 'JPEG, PNG ou WebP — pour personnaliser l’invitation.',
  relationLabel: 'Quel est votre lien ?',
  visibilityLabel: 'Comment souhaitez-vous vivre cette relation ?',
  submitLabel: 'Envoyer l’invitation amoureuse',
  historyTitle: 'Vos relations',
  historyEmpty:
    'Aucune relation déclarée pour le moment. Quand vous serez prêt·e, votre histoire commencera ici.',
  paymentSuccess: 'C’est noté ! Complétez votre déclaration amoureuse ci-dessous.',
  vipFormHint: 'Forfait Premium — 1 déclaration incluse ce mois. Personnalisez votre invitation.',
  vipQuotaExhausted:
    'Votre déclaration incluse ce mois est utilisée. Payez 300 FCFA pour en envoyer une autre.',
  sendSuccess:
    'Invitation envoyée avec tendresse. Votre partenaire recevra un SMS pour accepter ou refuser.',
  endConfirm:
    'Souhaitez-vous mettre fin à cette relation sur AntiGoumin ? Cette action est définitive.',
} as const

export const declarationVisibilityCopy = {
  PUBLIC_CERTIFIED: {
    label: 'Visible pour les autres',
    hint: 'Votre statut « En couple » pourra être consulté après l’accord de votre partenaire.',
    icon: 'public',
  },
  PRIVATE: {
    label: 'Juste entre vous deux',
    hint: 'Relation confirmée en privé, sans statut public.',
    icon: 'private',
  },
} as const

export const declarationRelationCopy: Record<
  'AMOUR' | 'FLIRT' | 'FIANCE' | 'MARIAGE',
  { label: string; emoji: string }
> = {
  AMOUR: { label: 'Amour', emoji: '💕' },
  FLIRT: { label: 'Flirt', emoji: '✨' },
  FIANCE: { label: 'Fiançailles', emoji: '💍' },
  MARIAGE: { label: 'Mariage', emoji: '💒' },
}

export const declarationStatusCopy: Record<
  'PENDING' | 'VERIFIED' | 'REJECTED' | 'ENDED',
  { label: string; severity: 'success' | 'warn' | 'danger' | 'secondary' }
> = {
  PENDING: { label: 'En attente de sa réponse', severity: 'warn' },
  VERIFIED: { label: 'Relation confirmée', severity: 'success' },
  REJECTED: { label: 'Invitation déclinée', severity: 'danger' },
  ENDED: { label: 'Relation terminée', severity: 'secondary' },
}

export const declarationsServiceCopy = {
  title: 'Déclarations amoureuses',
  description:
    'Dites au monde — ou gardez pour vous — la personne qui compte. Invitez votre partenaire à confirmer votre lien par SMS, en toute douceur et avec son consentement.',
  ctaLabel: 'Déclarer mon amour',
} as const

export const declarationsPricingCopy = {
  title: 'Déclaration amoureuse',
  price: '300 FCFA',
  priceSuffix: '/ invitation',
  tagline: 'Officialisez votre lien et invitez votre moitié',
  features: [
    'Invitation personnalisée par SMS',
    'Votre partenaire accepte ou refuse librement',
    'Relation privée ou statut « En couple » visible',
    'Double validation pour protéger chacun',
  ],
  buttonLabel: 'Déclarer mon amour',
} as const
