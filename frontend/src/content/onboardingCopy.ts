export const onboardingWizardCopy = {
  skip: 'Passer l’introduction',
  back: 'Retour',
  next: 'Continuer',
  finish: 'C’est parti',
  progress: (current: number, total: number) => `${current} / ${total}`,
  steps: [
    {
      id: 'welcome',
      emoji: '💍',
      title: 'Bienvenue sur AntiGoumin',
      body:
        'Votre espace privé pour vérifier un statut, officialiser une relation et, si vous le souhaitez, activer les alertes Alliance Premium.',
    },
    {
      id: 'verify',
      emoji: '🔍',
      title: 'Vérifier un numéro',
      body:
        'Consultez discrètement si un numéro ivoirien possède un statut certifié. La personne consultée n’est jamais alertée.',
    },
    {
      id: 'declare',
      emoji: '💕',
      title: 'Déclarer votre relation',
      body:
        'Invitez votre moitié par SMS à confirmer votre lien. Chacun reste libre d’accepter ou de refuser.',
    },
    {
      id: 'alliance',
      emoji: '🔔',
      title: 'Alliance Premium',
      body:
        'Scellez votre couple pour recevoir une alerte si votre partenaire est sollicité ou déclaré par un tiers — sans révéler qui.',
    },
    {
      id: 'ready',
      emoji: '✨',
      title: 'Vous êtes prêt·e',
      body:
        'Commencez par vérifier votre compte, puis explorez vos modules. Un court tutoriel vous guidera dans l’interface.',
    },
  ],
} as const

export const dashboardTutorialCopy = {
  skip: 'Passer le tutoriel',
  next: 'Suivant',
  finish: 'Terminer',
  progress: (current: number, total: number) => `${current} / ${total}`,
  steps: [
    {
      id: 'nav',
      title: 'Vos modules',
      body: 'Accédez ici à la vérification, aux déclarations, au test de fidélité et à vos alliances.',
      target: 'dashboard-nav',
    },
    {
      id: 'premium',
      title: 'Service Premium',
      body: 'Activez ou renouvelez votre Alliance Premium et consultez votre forfait mensuel inclus.',
      target: 'dashboard-premium',
    },
    {
      id: 'actions',
      title: 'Actions rapides',
      body: 'Les parcours les plus utiles sont à portée de tap depuis votre accueil.',
      target: 'dashboard-quick-actions',
    },
    {
      id: 'next',
      title: 'Prochaine étape',
      body: 'AntiGoumin vous suggère la meilleure action selon votre progression.',
      target: 'dashboard-next-action',
    },
    {
      id: 'stats',
      title: 'Vos statistiques',
      body: 'Compteurs personnels : uniquement votre activité, jamais celle des autres membres.',
      target: 'dashboard-stats',
    },
    {
      id: 'activity',
      title: 'Activité récente',
      body: 'Retrouvez ici l’historique de vos vérifications, déclarations et demandes.',
      target: 'dashboard-activity',
    },
  ],
} as const
