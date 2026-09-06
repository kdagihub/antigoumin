/** Informations légales de l’éditeur — CIACEMS (source : statuts / VendeursEnLive, adapté AntiGoumin). */
export const legalEntity = {
  denomination: 'CIACEMS',
  denominationLongue:
    'Cabinet d’Ingénierie Avancée et de Conception d’Environnements Multiservices Sécurisés (CIACEMS)',
  formeJuridique: 'SARL pluripersonnelle',
  capitalSocial: '1 000 000 FCFA',
  rccm: 'CI-ABJ-03-2024-M-44362',
  numeroContribuable: '2304005 U',
  siegeSocial:
    'Abidjan, Cocody, Angré 8e Tranche, Cité EVE, lot 664, îlot 43 — 09 BP 3815 Abidjan 09, Côte d’Ivoire',
  directionTechnique: 'M. KOFFI DJÈCLAY Alexandre',
} as const

export const antiGouminService = {
  nom: 'AntiGoumin',
  description:
    'Application web mobile (PWA) de registre de confiance mutuelle pour les couples, permettant la déclaration et la validation consensuelle d’une relation.',
  urls: ['https://antigoumin.live', 'https://www.antigoumin.live'],
  urlPrincipale: 'https://antigoumin.live',
  contactEmail: 'contact@antigoumin.live',
  privacyEmail: 'privacy@antigoumin.live',
} as const

export function editorParagraphs(): string[] {
  return [
    `La plateforme ${antiGouminService.nom}, accessible notamment à l’adresse ${antiGouminService.urlPrincipale}, est éditée et exploitée par ${legalEntity.denominationLongue} (${legalEntity.denomination}).`,
    `${antiGouminService.nom} est ${antiGouminService.description}`,
  ]
}

export function editorDetailsList(): string[] {
  return [
    `Forme juridique : ${legalEntity.formeJuridique}`,
    `Capital social : ${legalEntity.capitalSocial}`,
    `RCCM : ${legalEntity.rccm}`,
    `Numéro de compte contribuable : ${legalEntity.numeroContribuable}`,
    `Siège social : ${legalEntity.siegeSocial}`,
    `Direction technique de ${antiGouminService.nom} : ${legalEntity.directionTechnique}`,
    `Contact ${antiGouminService.nom} : ${antiGouminService.contactEmail}`,
    `Protection des données : ${antiGouminService.privacyEmail}`,
  ]
}
