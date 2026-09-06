export const dashboardStatCopy = {
  declarations: {
    label: 'Relations déclarées',
    icon: 'pi pi-heart',
    tone: 'rose',
  },
  verifications: {
    label: 'Recherches effectuées',
    icon: 'pi pi-search',
    tone: 'sky',
  },
  active_alliances: {
    label: 'Alliances actives',
    icon: 'pi pi-users',
    tone: 'violet',
  },
  transparency_requests: {
    label: 'Tests de fidélité',
    icon: 'pi pi-shield',
    tone: 'teal',
  },
} as const

export const dashboardHomeCopy = {
  activityTitle: 'Activité récente',
  activityEmpty:
    'Aucune activité pour le moment. Votre historique apparaîtra ici dès votre première action.',
  nextStepTitle: 'Prochaine étape',
  loading: 'Chargement de votre espace…',
} as const

export type DashboardStatKey = keyof typeof dashboardStatCopy

export const dashboardStatOrder: DashboardStatKey[] = [
  'declarations',
  'verifications',
  'active_alliances',
  'transparency_requests',
]
