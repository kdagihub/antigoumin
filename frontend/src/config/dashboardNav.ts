export type DashboardNavItem = {
  label: string
  to: string
  icon: string
  shortLabel?: string
}

export const dashboardModuleNavItems: DashboardNavItem[] = [
  { label: 'Accueil', shortLabel: 'Accueil', to: '/app', icon: 'pi pi-home' },
  {
    label: 'Vérifier un numéro',
    shortLabel: 'Vérifier',
    to: '/app/verification',
    icon: 'pi pi-phone',
  },
  {
    label: 'Mes déclarations',
    shortLabel: 'Déclarations',
    to: '/app/declarations',
    icon: 'pi pi-heart',
  },
  {
    label: 'Tests de fidélité',
    shortLabel: 'Transparence',
    to: '/app/transparence',
    icon: 'pi pi-search',
  },
  {
    label: 'Mes alliances',
    shortLabel: 'Alliances',
    to: '/app/alliances',
    icon: 'pi pi-users',
  },
]

export const dashboardAccountLinks = [
  { label: 'Profil', to: '/app/profil', icon: 'pi pi-user' },
  { label: 'Abonnements', to: '/app/abonnement', icon: 'pi pi-credit-card' },
] as const
