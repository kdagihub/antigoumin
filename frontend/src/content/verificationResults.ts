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
    title: 'Pas encore sur AntiGoumin',
    body:
      'Ce numéro n’est pas inscrit sur la plateforme pour le moment. Cela ne veut pas dire que la personne est célibataire dans la vie réelle — simplement qu’AntiGoumin ne dispose d’aucune information certifiée pour ce contact. Vous pouvez l’inviter à rejoindre la plateforme.',
    tone: 'neutral',
    ctaLabel: 'Inviter en déclaration amoureuse',
    ctaRoute: '/app/declarations',
  },
  REGISTERED_NO_DECLARATION: {
    title: 'Inscrit, sans relation déclarée',
    body:
      'Bonne nouvelle côté registre : ce numéro est bien membre d’AntiGoumin, mais aucune relation n’a encore été déclarée et certifiée pour lui sur la plateforme.',
    tone: 'success',
  },
  ENGAGED: {
    title: 'Relation déjà déclarée',
    body:
      'Ce numéro est engagé dans une relation déclarée et certifiée sur AntiGoumin. L’identité du partenaire reste confidentielle — seul le statut relationnel est confirmé. Si vous avez des questions, le mieux reste d’en parler directement avec la personne.',
    tone: 'warn',
  },
  STATUS_NOT_PUBLIC: {
    title: 'Statut protégé',
    body:
      'Ce numéro appartient à un membre Alliance Digitale VIP qui a choisi de garder son statut privé. AntiGoumin respecte ce choix et ne peut pas afficher de statut certifié pour ce contact.',
    tone: 'info',
  },
}
