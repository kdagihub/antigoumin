import type { CertifiedStatus } from '@/api/search'

export type VerificationResultCopy = {
  title: string
  body: string
  tone: 'info' | 'success' | 'warn' | 'neutral'
  ctaLabel?: string
  ctaRoute?: string
}

export const verificationResultCopy: Record<
  Exclude<CertifiedStatus, 'PAYMENT_REQUIRED'>,
  VerificationResultCopy
> = {
  NOT_A_MEMBER: {
    title: 'Pas encore membre d’AntiGoumin',
    body:
      'Ce numéro n’est pas enregistré sur la plateforme. Cela ne signifie pas que la personne est célibataire dans la vie réelle — seulement qu’AntiGoumin ne dispose d’aucune donnée pour ce contact.',
    tone: 'neutral',
    ctaLabel: 'Inviter via une déclaration',
    ctaRoute: '/app/declarations',
  },
  REGISTERED_NO_DECLARATION: {
    title: 'Membre sans relation déclarée',
    body:
      'Ce numéro est inscrit sur AntiGoumin, mais n’est associé à aucune relation déclarée et certifiée sur la plateforme pour le moment.',
    tone: 'success',
  },
  ENGAGED: {
    title: 'Relation déclarée sur AntiGoumin',
    body:
      'Ce numéro est engagé dans une relation déclarée et certifiée sur la plateforme. L’identité du partenaire n’est jamais révélée. Vous pouvez contacter directement la personne pour en discuter.',
    tone: 'warn',
  },
  STATUS_NOT_PUBLIC: {
    title: 'Statut non consultable',
    body:
      'Ce numéro appartient à un membre Alliance Digitale VIP qui a choisi de ne pas rendre son statut consultable publiquement. AntiGoumin ne peut pas afficher de statut certifié pour ce contact.',
    tone: 'info',
  },
}
