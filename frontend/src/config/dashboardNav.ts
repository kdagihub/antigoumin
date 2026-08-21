export type DashboardNavItem = {
  label: string
  to: string
  icon: string
  shortLabel?: string
}

export const dashboardNavItems: DashboardNavItem[] = [
  { label: 'Accueil', shortLabel: 'Accueil', to: '/app', icon: 'pi pi-home' },
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
  { label: 'Mon profil', shortLabel: 'Profil', to: '/app/profil', icon: 'pi pi-user' },
  {
    label: 'Abonnement',
    shortLabel: 'Abonnement',
    to: '/app/abonnement',
    icon: 'pi pi-credit-card',
  },
]
