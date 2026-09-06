export type DashboardNavItem = {
  label: string
  to: string
  icon: string
  shortLabel?: string
  /** Bouton central surélevé dans la barre mobile (style TikTok +). */
  mobileFab?: boolean
  customIcon?: 'alliance-rings'
}

export const dashboardModuleNavItems: DashboardNavItem[] = [
  { label: 'Accueil', shortLabel: 'Accueil', to: '/app', icon: 'pi pi-home' },
  {
    label: 'Vérifier un numéro',
    shortLabel: 'Vérifier',
    to: '/app/verification',
    icon: 'pi pi-search',
  },
  {
    label: 'Déclarations amoureuses',
    shortLabel: 'Relations',
    to: '/app/declarations',
    icon: 'pi pi-heart-fill',
    mobileFab: true,
  },
  {
    label: 'Test de fidélité',
    shortLabel: 'Test de fidélité',
    to: '/app/transparence',
    icon: 'pi pi-shield',
  },
  {
    label: 'Mes alliances',
    shortLabel: 'Alliances',
    to: '/app/alliances',
    icon: 'pi pi-users',
    customIcon: 'alliance-rings',
  },
]

export type DashboardQuickAction = {
  label: string
  description: string
  to: string
  icon: string
  tone: 'sky' | 'rose' | 'amber' | 'violet'
  featured?: boolean
}

export const dashboardQuickActions: DashboardQuickAction[] = [
  {
    label: 'Vérifier un numéro',
    description: 'Statut relationnel discret',
    to: '/app/verification',
    icon: 'pi pi-search',
    tone: 'sky',
  },
  {
    label: 'Déclarer mon amour',
    description: 'Invitez votre moitié par SMS',
    to: '/app/declarations',
    icon: 'pi pi-heart-fill',
    tone: 'rose',
    featured: true,
  },
  {
    label: 'Test de fidélité',
    description: 'Clarifiez un doute — invitation identifiable et volontaire',
    to: '/app/transparence',
    icon: 'pi pi-shield',
    tone: 'amber',
  },
  {
    label: 'Mes alliances',
    description: 'Votre sceau de confiance à deux',
    to: '/app/alliances',
    icon: 'pi pi-users',
    tone: 'violet',
  },
]

export const dashboardAccountLinks = [
  { label: 'Profil', to: '/app/profil', icon: 'pi pi-user' },
  { label: 'Service Premium', to: '/app/abonnement', icon: 'pi pi-star-fill' },
] as const
