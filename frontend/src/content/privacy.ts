import type { LegalDocument } from '@/types/legal'

import { antiGouminService, editorDetailsList, legalEntity } from './legal-entity'

export const privacyDocument: LegalDocument = {
  title: 'Politique de confidentialité',
  subtitle:
    'Protection des données personnelles conformément à la Loi n° 2013-450 du 19 juin 2013 et aux exigences de l’ARTCI.',
  lastUpdated: '21 août 2026',
  preamble:
    `La présente Politique de confidentialité décrit la manière dont ${legalEntity.denominationLongue}, éditeur de l’application ${antiGouminService.nom}, collecte, utilise, conserve et protège vos données à caractère personnel. En utilisant ${antiGouminService.nom}, vous reconnaissez avoir pris connaissance de cette politique.`,
  sections: [
    {
      id: 'responsable',
      title: '1. Responsable du traitement',
      paragraphs: [
        `Le responsable du traitement des données personnelles collectées via ${antiGouminService.nom} est ${legalEntity.denominationLongue} (${legalEntity.denomination}), ${legalEntity.formeJuridique}, immatriculée au RCCM sous le numéro ${legalEntity.rccm}.`,
        `Siège social : ${legalEntity.siegeSocial}.`,
        `Pour toute question relative à vos données personnelles : ${antiGouminService.privacyEmail}.`,
        `Conformément à la Loi n° 2013-450, ${legalEntity.denomination} s’engage à accomplir les formalités requises auprès de l’Autorité de protection des données personnelles et, le cas échéant, à désigner un Correspondant à la protection des données personnelles (DPO).`,
      ],
      list: editorDetailsList(),
    },
    {
      id: 'donnees-collectees',
      title: '2. Données collectées',
      paragraphs: [
        'AntiGoumin collecte uniquement les données strictement nécessaires au fonctionnement du registre de confiance et à la sécurisation des déclarations de relation.',
      ],
      list: [
        'Identité : prénom, nom, adresse email.',
        'Authentification : mot de passe chiffré, identifiant Google (OAuth), jeton de session JWT.',
        'Contact : numéro de téléphone (lorsque renseigné ou requis pour OTP).',
        'Déclarations : numéro du partenaire, nom du partenaire, photographie uploadée, statut de validation.',
        'Consentements : choix entre relation privée et certification publique, consentements d’affichage du profil de couple, consentements d’Alliance, oppositions et blocages.',
        'Demandes de Transparence : identité de l’auteur communiquée au destinataire, statut de la demande (acceptée, refusée, expirée, bloquée, signalée).',
        'Transactions : références de paiement Mobile Money, montant, statut (sans stockage des données bancaires sensibles).',
        'Techniques : adresse IP, logs de connexion, identifiants d’appareil, horodatages — à des fins de sécurité et de lutte contre la fraude.',
      ],
    },
    {
      id: 'finalites',
      title: '3. Finalités et bases légales',
      paragraphs: [
        'Vos données sont traitées pour les finalités suivantes, sur les bases légales indiquées :',
      ],
      list: [
        'Création et gestion de votre compte utilisateur (exécution du contrat).',
        'Authentification sécurisée et prévention des accès non autorisés (intérêt légitime / obligation de sécurité).',
        'Envoi de codes OTP par SMS ou email pour validation des déclarations (consentement et exécution du service).',
        'Gestion des déclarations de relation et double validation partenaire (exécution du contrat et consentement).',
        'Vérification d’un statut certifié uniquement si les parties ont accepté le mode « certification publique » lors de la validation de relation (consentement).',
        'Envoi de Demandes de Transparence identifiables (exécution du contrat et consentement de l’auteur ; le destinataire n’est pas obligé de répondre).',
        'Gestion de l’Alliance Digitale VIP et notifications minimales en cas de retrait de la consultabilité publique ou de fin d’Alliance (consentement de chaque partie).',
        'Traitement des paiements via agrégateur Mobile Money (exécution du contrat).',
        'Respect des obligations légales et réponse aux autorités compétentes (obligation légale).',
        'Amélioration de la sécurité, détection des abus et rate-limiting (intérêt légitime).',
      ],
    },
    {
      id: 'information-artci',
      title: '4. Information lors de la collecte (ARTCI)',
      paragraphs: [
        'Conformément aux exigences de l’Autorité de Régulation des Télécommunications/TIC de Côte d’Ivoire (ARTCI) et de la Loi n° 2013-450, nous vous informons au moment de la collecte de :',
      ],
      list: [
        `L’identité du responsable du traitement (${legalEntity.denomination} / ${antiGouminService.nom}).`,
        'Les catégories de données concernées.',
        'Les finalités du traitement.',
        'Les destinataires ou catégories de destinataires.',
        'La possibilité de refuser de figurer sur le fichier, lorsque applicable.',
        'L’existence d’un droit d’accès, de rectification et d’opposition.',
        'La durée de conservation des données.',
        'L’éventualité de tout transfert de données vers un pays tiers.',
      ],
    },
    {
      id: 'destinataires',
      title: '5. Destinataires et sous-traitants',
      paragraphs: [
        'Vos données peuvent être communiquées aux destinataires suivants, dans la stricte limite de leurs missions :',
      ],
      list: [
        'Le partenaire déclaré, uniquement dans le cadre de la validation OTP (lien sécurisé).',
        'Le destinataire d’une Demande de Transparence, uniquement pour lui communiquer l’identité de l’auteur et le lien de réponse.',
        'Les utilisateurs tiers, uniquement pour consulter un statut certifié binaire si une certification publique active a été acceptée. Aucun nom, photo, compteur de relations ni historique n’est communiqué.',
        'Prestataires d’hébergement (VPS, Docker, bases PostgreSQL).',
        'Prestataires SMS OTP pour l’envoi des codes de validation.',
        'Agrégateurs de paiement Mobile Money (Fedapay, CinetPay ou équivalent).',
        'Google LLC, en cas de connexion via Google OAuth (identité vérifiée).',
        'Autorités judiciaires ou administratives, sur réquisition légale.',
      ],
      subsections: [
        {
          id: 'sous-traitants',
          title: '5.1. Rôle des sous-traitants',
          paragraphs: [
            `Le responsable du traitement peut déléguer certaines activités à des sous-traitants distincts, qui exécutent leurs tâches uniquement sur instruction et sous la responsabilité de ${legalEntity.denomination}.`,
          ],
          list: [
            'Le sous-traitant ne peut effectuer aucun traitement non expressément autorisé.',
            `${legalEntity.denomination} choisit des sous-traitants apportant des garanties suffisantes en matière de sécurité technique et organisationnelle.`,
            'Des clauses contractuelles encadrent la confidentialité, la durée et la finalité du traitement.',
          ],
        },
      ],
    },
    {
      id: 'conservation',
      title: '6. Durée de conservation',
      list: [
        'Compte utilisateur : conservé tant que le compte est actif, puis 3 ans après la dernière connexion (sauf obligation légale contraire).',
        'Déclarations PENDING non validées : supprimées automatiquement après expiration du délai OTP (15 minutes) ou au maximum 30 jours.',
        'Déclarations VERIFIED : conservées tant que la relation est active, puis archivées ou supprimées sur demande des parties.',
        'Demandes de Transparence non abouties : conservées le temps du délai de réponse, puis archivées de manière limitée à des fins de lutte contre les abus, ou supprimées selon le paramétrage en vigueur.',
        'Consentement à la certification publique : conservé tant que la certification est active, puis journalisé lors du retrait ou du passage au mode privé.',
        'Données de paiement : conservées 5 ans conformément aux obligations comptables.',
        'Logs de sécurité : 12 mois maximum.',
        'Données OTP en cache Redis : TTL de 15 minutes, puis effacement automatique.',
      ],
    },
    {
      id: 'transferts',
      title: '7. Transferts internationaux',
      paragraphs: [
        'Certains sous-traitants (hébergement cloud, Google OAuth, agrégateur de paiement) peuvent être situés en dehors de la Côte d’Ivoire.',
        `Dans ce cas, ${legalEntity.denomination} s’assure que des garanties appropriées sont mises en place (clauses contractuelles types, pays reconnus comme offrant un niveau de protection adéquat, ou consentement explicite lorsque requis).`,
        'Vous serez informé préalablement de tout transfert significatif vers un pays tiers.',
      ],
    },
    {
      id: 'securite',
      title: '8. Mesures de sécurité',
      paragraphs: [
        `Conformément aux obligations ARTCI et à la Loi n° 2013-450, ${legalEntity.denomination} met en œuvre les mesures suivantes :`,
      ],
      list: [
        'Contrôle d’accès : seules les personnes autorisées accèdent aux installations de traitement.',
        'Authentification forte : mots de passe hashés, JWT signés, OAuth Google.',
        'Chiffrement des communications : HTTPS/TLS obligatoire en production.',
        'Isolation réseau : conteneurs Docker, pare-feu, accès restreint aux bases de données.',
        'Journalisation : traçabilité des accès, modifications et suppressions de données.',
        'Rate-limiting Redis : protection contre les abus d’envoi SMS OTP.',
        'Sauvegardes régulières : copies de sécurité protégées contre la perte ou l’altération.',
        'Principe du moindre privilège : accès limité aux seules données nécessaires à chaque rôle.',
        'Prévention du blanchiment : aucun usage des systèmes à des fins illicites.',
      ],
    },
    {
      id: 'droits',
      title: '9. Vos droits',
      paragraphs: [
        'Conformément à la Loi n° 2013-450, vous disposez des droits suivants sur vos données personnelles :',
      ],
      subsections: [
        {
          id: 'droit-information',
          title: '9.1. Droit à l’information et d’accès',
          list: [
            'Être informé du traitement de vos données et de ses finalités.',
            'Être informé avant la première communication de vos données à des tiers.',
            'Accéder à vos données à caractère personnel à tout moment.',
            'Obtenir la communication de vos données, leur origine et les finalités du traitement.',
            'Exercer ce droit moyennant la production d’une photocopie d’une pièce d’identité en vigueur.',
          ],
        },
        {
          id: 'droit-rectification',
          title: '9.2. Droit de rectification et d’opposition',
          list: [
            'Exiger la rectification, la mise à jour ou le verrouillage de données inexactes ou périmées.',
            'Vous opposer, pour motifs légitimes, au traitement de vos données.',
            'Vous opposer gratuitement à la prospection commerciale.',
          ],
        },
        {
          id: 'droit-suppression',
          title: '9.3. Droit à l’effacement et retrait du consentement',
          list: [
            'Exiger la suppression de données dont le traitement est interdit.',
            'Obtenir l’effacement si les données ne sont plus nécessaires aux finalités collectées.',
            'Retirer votre consentement à tout moment, y compris la certification publique, l’affichage du profil de couple et l’Alliance Digitale, sans que ce retrait puisse être conditionné à l’accord d’un tiers.',
          ],
        },
        {
          id: 'droit-portabilite',
          title: '9.4. Droit à la portabilité',
          list: [
            'Obtenir une copie de vos données dans un format structuré, couramment utilisé et lisible par machine.',
            'Transmettre ces données à un autre responsable de traitement, lorsque le traitement est fondé sur le consentement ou un contrat.',
          ],
        },
      ],
    },
    {
      id: 'exercice-droits',
      title: '10. Exercer vos droits',
      paragraphs: [
        `Pour exercer vos droits, adressez votre demande à ${antiGouminService.privacyEmail} ou par courrier au siège social (${legalEntity.siegeSocial}), en joignant une photocopie d’une pièce d’identité en vigueur.`,
        `Nous répondrons dans un délai raisonnable, conformément à la réglementation ivoirienne. ${legalEntity.denomination} se réserve le droit de refuser les demandes manifestement abusives, répétitives ou infondées.`,
        'En cas de litige non résolu, vous pouvez saisir l’Autorité de protection des données personnelles de Côte d’Ivoire.',
      ],
    },
    {
      id: 'cookies',
      title: '11. Cookies et traceurs',
      paragraphs: [
        'AntiGoumin utilise des cookies et stockages locaux strictement nécessaires au fonctionnement :',
        'Aucun cookie publicitaire ou de profilage n’est déployé sans votre consentement explicite.',
      ],
      list: [
        'Jeton d’authentification (localStorage) : maintien de votre session.',
        'Cookies techniques de session Django (administration).',
        'Service Worker PWA : mise en cache des ressources pour un accès hors-ligne limité.',
      ],
    },
    {
      id: 'sanctions',
      title: '12. Sanctions en cas de non-respect',
      paragraphs: [
        'Le non-respect de la Loi n° 2013-450 peut entraîner des sanctions administratives, pécuniaires et pénales à l’encontre du responsable du traitement.',
        `${legalEntity.denomination} s’engage à mettre en œuvre toutes les mesures utiles pour garantir l’exploitabilité des données quel que soit le support technique utilisé.`,
      ],
    },
    {
      id: 'modifications',
      title: '13. Modifications de la politique',
      paragraphs: [
        'Cette politique peut être mise à jour pour refléter l’évolution du service ou de la réglementation. La date de dernière mise à jour est indiquée en tête de document.',
        'En cas de modification substantielle, les utilisateurs seront informés par notification in-app ou par email.',
      ],
    },
  ],
}
