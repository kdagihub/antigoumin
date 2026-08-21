import type { LegalDocument } from '@/types/legal'

import {
  antiGouminService,
  editorDetailsList,
  editorParagraphs,
  legalEntity,
} from './legal-entity'

export const cguDocument: LegalDocument = {
  title: 'Conditions Générales d’Utilisation',
  subtitle:
    'Règles d’utilisation de la plateforme AntiGoumin — registre de confiance pour les couples.',
  lastUpdated: '21 août 2026',
  preamble:
    `Les présentes Conditions Générales d’Utilisation (CGU) régissent l’accès et l’utilisation de l’application ${antiGouminService.nom}, éditée par ${legalEntity.denominationLongue}. En créant un compte ou en utilisant le service, vous acceptez sans réserve l’intégralité des présentes CGU ainsi que la Politique de confidentialité.`,
  sections: [
    {
      id: 'editeur',
      title: '1. Éditeur et objet du service',
      paragraphs: editorParagraphs(),
      list: editorDetailsList(),
    },
    {
      id: 'objet',
      title: '2. Objet et acceptation',
      paragraphs: [
        'AntiGoumin est une application web mobile (PWA) de registre de confiance mutuelle. Elle permet de déclarer une relation amoureuse, d’obtenir le consentement explicite du partenaire, de consulter un statut certifié uniquement lorsque le titulaire du numéro l’a autorisé, et d’envoyer une demande de transparence identifiable.',
        'L’acceptation des CGU est obligatoire avant toute inscription ou déclaration de relation. Cette acceptation est matérialisée par le cochage de la case prévue à cet effet lors de l’inscription.',
        'Si vous n’acceptez pas ces conditions, vous ne devez pas utiliser AntiGoumin.',
      ],
    },
    {
      id: 'definitions',
      title: '3. Définitions',
      list: [
        'Application / Plateforme : le service AntiGoumin accessible via le site web et la PWA.',
        'Utilisateur : toute personne disposant d’un compte AntiGoumin.',
        'Déclarant (User A) : l’utilisateur qui initie une déclaration de relation.',
        'Partenaire déclaré (User B) : la personne désignée dans une déclaration, identifiée notamment par son numéro de téléphone.',
        'Utilisateur tiers (User C) : toute personne effectuant une recherche sur un numéro de téléphone.',
        'Déclaration privée : relation mutuellement validée par OTP, conservée hors des résultats de recherche.',
        'Certification publique : relation mutuellement validée dont les deux parties acceptent que le statut binaire « En couple » soit consultable par leur numéro, sans affichage automatique de leur identité.',
        'Vérification : consultation payante du statut certifié d’un numéro inscrit sur AntiGoumin et ayant accepté une certification publique active.',
        'Demande de Transparence : invitation officielle, identifiable et non trompeuse, invitant une personne à clarifier ou certifier volontairement son statut relationnel.',
        'Alliance Digital VIP : abonnement mensuel premium fondé sur un consentement mutuel, donnant accès à un badge optionnel, à des notifications de fin d’Alliance et à un forfait d’actions.',
      ],
    },
    {
      id: 'service',
      title: '4. Description du service',
      paragraphs: [
        'AntiGoumin propose les fonctionnalités suivantes :',
        'AntiGoumin ne garantit pas l’exactitude des déclarations. Elle garantit uniquement que : (i) aucune relation n’est certifiée sans validation OTP du partenaire ; (ii) la consultabilité publique est annoncée avant acceptation et peut être retirée ; (iii) aucune demande de transparence n’est anonyme ni trompeuse.',
      ],
      list: [
        'Inscription et authentification (email/mot de passe, Google OAuth, OTP SMS à venir).',
        'Vérification d’un statut certifié (200 FCFA par recherche), uniquement si le titulaire a autorisé la consultabilité publique.',
        'Déclaration d’une relation avec validation OTP du partenaire (300 FCFA), en mode privé ou en mode certification publique clairement annoncé.',
        'Demande de Transparence identifiable (550 FCFA par demande).',
        'Alliance Digital VIP : abonnement mensuel (1 200 FCFA/mois) avec consentement des deux parties.',
        'Validation par le partenaire via lien OTP sécurisé (SMS ou email).',
        'Paiement Mobile Money à la demande ou par abonnement (Wave, Orange Money, MTN Mobile Money, Moov via agrégateur).',
      ],
    },
    {
      id: 'inscription',
      title: '5. Inscription et compte utilisateur',
      list: [
        'L’inscription est réservée aux personnes majeures (18 ans et plus) ou disposant de l’autorisation parentale.',
        'Vous vous engagez à fournir des informations exactes, complètes et à jour.',
        'Vous êtes seul responsable de la confidentialité de vos identifiants de connexion.',
        'Toute activité réalisée depuis votre compte est réputée effectuée par vous.',
        `${legalEntity.denomination} se réserve le droit de suspendre ou supprimer tout compte en cas de violation des CGU ou de comportement frauduleux.`,
      ],
    },
    {
      id: 'double-validation',
      title: '6. Mécanisme de double validation',
      paragraphs: [
        'Le cœur du service repose sur un principe de consentement mutuel et de double vérification.',
      ],
      list: [
        'Toute déclaration initiée par l’Utilisateur A concernant l’Utilisateur B reste strictement confidentielle, floutée et masquée du public tant que l’Utilisateur B n’a pas explicitement validé cette déclaration via un code OTP.',
        'L’Utilisateur B reçoit un lien unique (ex. antigoumin.live/v/xyz) par SMS ou email.',
        'En l’absence de validation dans le délai imparti, la déclaration est automatiquement supprimée ou archivée selon les règles techniques en vigueur.',
        'L’Utilisateur B peut également refuser explicitement une déclaration (statut REJECTED).',
        'Aucune déclaration non validée ne peut être consultée par un tiers.',
        'Chaque invitation indique avant validation si elle concerne une relation privée ou une certification publique. Pour une certification publique, le bouton d’acceptation mentionne explicitement que le statut binaire « En couple » deviendra consultable.',
        'Le consentement à la consultabilité peut être retiré à tout moment depuis le profil. Ce retrait met fin à la certification publique ou la ramène au mode privé ; il ne nécessite pas l’accord de l’autre partie. Si une Alliance Digitale est active, le partenaire reçoit une notification neutre du retrait, sans motif ni autre information relationnelle.',
        'En l’absence de certification publique active, une recherche externe ne peut pas distinguer un numéro introuvable d’un numéro non consultable.',
      ],
    },
    {
      id: 'tarification',
      title: '7. Tarification et services payants',
      paragraphs: [
        'AntiGoumin fonctionne selon un modèle hybride : la plupart des actions sont facturées à l’unité (pay-per-action), et l’Alliance Digital VIP est proposée sous forme d’abonnement mensuel.',
        'Les tarifs applicables sont ceux affichés sur la plateforme au moment de l’action ; en cas de divergence, les tarifs indiqués sur la plateforme prévalent.',
      ],
      subsections: [
        {
          id: 'verification',
          title: '7.1. Vérification du statut certifié',
          list: [
            'Tarif : 200 FCFA par recherche de numéro, payable via Mobile Money.',
            'La recherche ne porte que sur les numéros associés à un compte AntiGoumin et disposant d’une certification publique active, acceptée explicitement lors de la double validation OTP.',
            'Résultat possible : « Statut certifié : engagé », « Statut certifié : disponible », ou « Numéro non répertorié ou non consultable ».',
            'AntiGoumin n’affiche ni le nombre de relations, ni leur ancienneté, ni l’identité, ni une photographie, ni un historique.',
            'Le résultat « non répertorié ou non consultable » ne permet pas de savoir si le numéro existe dans la base, s’il a refusé la consultabilité, ou s’il n’a jamais utilisé le service.',
            'Chaque titulaire peut retirer la consultabilité à tout moment. Le retrait est immédiat et sans frais. Dans une Alliance active, le partenaire est seulement informé que la consultabilité a été retirée.',
          ],
        },
        {
          id: 'declaration',
          title: '7.2. Déclaration',
          list: [
            'Tarif : 300 FCFA par déclaration, payable via Mobile Money.',
            'Le déclarant choisit entre « relation privée » et « certification publique ». Ce choix est affiché au partenaire avant sa décision.',
            'La relation privée est soumise à la double validation OTP mais reste absente des recherches.',
            'La certification publique est soumise à la double validation OTP et rend uniquement le statut binaire « En couple » consultable par les numéros des deux parties.',
            'L’affichage des prénoms, photographies, profil public de couple ou participation à un classement exige des consentements supplémentaires, distincts et révocables.',
            'Avant validation, aucune information sur d’éventuelles autres relations du destinataire n’est communiquée au déclarant, sauf si le destinataire a lui-même rendu un statut certifié consultable selon l’article 7.1.',
            'Le destinataire peut accepter, refuser ou laisser expirer la déclaration. Un refus ou une expiration n’est pas publié.',
          ],
        },
        {
          id: 'transparence',
          title: '7.3. Demande de Transparence',
          list: [
            'Tarif : 550 FCFA par demande, payable via Mobile Money.',
            'Ce service permet à un utilisateur identifié d’inviter une personne à clarifier ou certifier volontairement son statut relationnel.',
            'La demande n’est ni anonyme, ni trompeuse, ni présentée comme une obligation. Le destinataire est informé de l’identité de l’auteur (prénom ou identifiant public choisi) et peut accepter, refuser, ignorer, bloquer l’auteur ou signaler un abus.',
            'La réponse reste privée entre les parties et ne peut être publiée sans un consentement distinct.',
            'L’absence de réponse signifie uniquement que la demande a expiré ; elle ne constitue aucune preuve concernant le comportement, la fidélité ou le statut du destinataire.',
            'Les sollicitations sont limitées (une demande active par paire, délai avant nouvelle sollicitation, opposition et blocage possibles). Aucune relance n’est envoyée après opposition.',
            'Les frais couvrent l’émission et le traitement technique de la demande. Les conditions de remboursement sont présentées avant paiement.',
          ],
        },
        {
          id: 'alliance-vip',
          title: '7.4. Alliance Digital VIP',
          list: [
            'Tarif : 1 200 FCFA par mois, payable via Mobile Money.',
            'L’Alliance n’est activée qu’après consentement distinct de chacune des deux parties.',
            'Avantages : badge certifié optionnel, forfait mensuel (5 vérifications, 1 déclaration, 1 demande de transparence), support prioritaire, historique des actions.',
            'Notifications : chaque partie peut être informée, de manière neutre, que l’autre a retiré sa consultabilité publique ou que l’Alliance a pris fin. Aucun motif, aucune autre relation et aucun détail de statut ne sont communiqués à cette occasion.',
            'Chacun peut mettre fin à l’Alliance ou supprimer son compte à tout moment. Le retrait du consentement désactive immédiatement la publication du badge et les notifications autres que l’information minimale de fin d’Alliance.',
            'L’abonnement est renouvelé automatiquement sauf résiliation depuis le profil. Aucun remboursement n’est dû pour une période déjà entamée, sauf disposition légale contraire.',
          ],
        },
        {
          id: 'paiement',
          title: '7.5. Modalités de paiement',
          list: [
            'Paiements acceptés via Mobile Money (Wave, Orange Money, MTN Mobile Money, Moov) par l’intermédiaire d’un agrégateur sécurisé.',
            'Chaque action payante est déclenchée et facturée à la demande de l’utilisateur, après confirmation du montant affiché.',
            'Les actions unitaires ne sont pas remboursables une fois exécutées, sauf erreur technique avérée imputable à la plateforme.',
            `${legalEntity.denomination} se réserve le droit de modifier les tarifs ; les utilisateurs seront informés de toute modification substantielle.`,
          ],
        },
      ],
    },
    {
      id: 'obligations',
      title: '8. Obligations de l’utilisateur',
      paragraphs: [
        'En utilisant AntiGoumin, vous vous engagez à :',
      ],
      list: [
        'Ne pas créer de fausses déclarations ou usurper l’identité d’un tiers.',
        'Ne pas harceler, diffamer, menacer ou porter atteinte à la réputation d’autrui, y compris via des Demandes de Transparence répétées.',
        'Ne pas tenter de contourner les mécanismes de consentement, de choix privé/public, de validation OTP, d’opposition ou de paiement.',
        'Ne pas utiliser des robots, scripts ou outils automatisés pour extraire des données.',
        'Ne pas publier de contenus illicites, pornographiques, haineux ou contraires à l’ordre public ivoirien.',
        'Respecter la vie privée et le consentement du partenaire déclaré.',
        `Signaler tout abus ou comportement suspect à ${antiGouminService.contactEmail}.`,
      ],
    },
    {
      id: 'responsabilite',
      title: '9. Limitation de responsabilité',
      paragraphs: [
        'AntiGoumin est un outil de registre de confiance, et non un tribunal, un service de détective privé ou une garantie de fidélité.',
        `${legalEntity.denomination} ne saurait être tenue responsable des conséquences relationnelles, sociales ou juridiques découlant de l’utilisation ou de la consultation du registre.`,
        `Le service est fourni « en l’état ». ${legalEntity.denomination} s’efforce d’assurer une disponibilité maximale, sans garantie d’absence d’interruption.`,
        `${legalEntity.denomination} ne pourra être tenue responsable en cas de force majeure, de défaillance des opérateurs télécoms, des agrégateurs de paiement ou des prestataires SMS.`,
      ],
    },
    {
      id: 'propriete',
      title: '10. Propriété intellectuelle',
      paragraphs: [
        `L’ensemble des éléments composant ${antiGouminService.nom} (marque, logo, code source, design, textes) est la propriété exclusive de ${legalEntity.denominationLongue} ou de ses partenaires.`,
        'Toute reproduction, représentation ou exploitation non autorisée est interdite.',
        `Les photographies uploadées par les utilisateurs restent leur propriété ; l’utilisateur accorde à ${legalEntity.denomination} une licence non exclusive d’hébergement et d’affichage dans le cadre du service.`,
      ],
    },
    {
      id: 'suspension',
      title: '11. Suspension et résiliation',
      list: [
        'Vous pouvez supprimer votre compte, retirer la consultabilité publique, ramener une certification au mode privé et mettre fin à une Alliance à tout moment depuis votre profil ou par demande écrite. La suppression n’est pas subordonnée à l’accord de l’autre partie.',
        `${legalEntity.denomination} peut suspendre ou résilier un compte en cas de violation grave ou répétée des CGU.`,
        'En cas de résiliation, vos données seront traitées conformément à la Politique de confidentialité.',
        'Les abonnements Alliance Digital VIP en cours ne sont pas remboursables au prorata, sauf obligation légale.',
      ],
    },
    {
      id: 'abus',
      title: '12. Limitation des demandes abusives',
      paragraphs: [
        `Conformément à la réglementation sur la protection des données, ${legalEntity.denomination} se réserve le droit de s’opposer aux demandes manifestement abusives d’une même personne.`,
        'Le caractère abusif peut être justifié par le nombre, le caractère répétitif ou systématique des demandes d’accès, de rectification ou de suppression.',
      ],
    },
    {
      id: 'modifications-cgu',
      title: '13. Modification des CGU',
      paragraphs: [
        `${legalEntity.denomination} se réserve le droit de modifier les présentes CGU à tout moment.`,
        'Les utilisateurs seront informés de toute modification substantielle. La poursuite de l’utilisation du service après notification vaut acceptation des nouvelles CGU.',
      ],
    },
    {
      id: 'droit-applicable',
      title: '14. Droit applicable et litiges',
      paragraphs: [
        'Les présentes CGU sont régies par le droit ivoirien, notamment la Loi n° 2013-450 relative à la protection des données à caractère personnel.',
        'En cas de litige, les parties s’efforceront de trouver une solution amiable. À défaut, compétence est attribuée aux tribunaux d’Abidjan, Côte d’Ivoire.',
      ],
    },
    {
      id: 'contact',
      title: '15. Contact',
      paragraphs: ['Pour toute question relative aux présentes CGU :'],
      list: [
        `Email : ${antiGouminService.contactEmail}`,
        `Protection des données : ${antiGouminService.privacyEmail}`,
        `Téléphone : ${antiGouminService.telephone}`,
        `Éditeur : ${legalEntity.denominationLongue}`,
        `Siège social : ${legalEntity.siegeSocial}`,
        `RCCM : ${legalEntity.rccm} — NCC : ${legalEntity.numeroContribuable}`,
      ],
    },
  ],
}
