<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { antiGouminService } from '@/content/legal-entity'

type CategoryId = 'all' | 'confidentialite' | 'services' | 'paiement' | 'legal'

interface FaqItem {
  id: string
  category: Exclude<CategoryId, 'all'>
  question: string
  answer: string
}

const categories: { id: CategoryId; label: string }[] = [
  { id: 'all', label: 'Toutes' },
  { id: 'confidentialite', label: 'Confidentialité' },
  { id: 'services', label: 'Services' },
  { id: 'paiement', label: 'Paiement' },
  { id: 'legal', label: 'Légal' },
]

const faqs: FaqItem[] = [
  {
    id: 'anon',
    category: 'confidentialite',
    question: "L'application est-elle vraiment anonyme ?",
    answer:
      'La recherche publique ne révèle ni nom, ni photo, ni historique. Un numéro n’apparaît que si une certification publique a été mutuellement acceptée. Sinon, le résultat est simplement « non répertorié ou non consultable ». Les Demandes de Transparence, elles, identifient volontairement l’auteur auprès du destinataire.',
  },
  {
    id: 'partenaire-sait',
    category: 'confidentialite',
    question: 'Mon partenaire saura-t-il que je l’ai vérifié ?',
    answer:
      'Non. Consulter un statut certifié ne génère aucune notification. En revanche, une déclaration ou une Demande de Transparence contacte la personne concernée, car ces actions nécessitent son consentement ou une invitation identifiable.',
  },
  {
    id: 'donnees',
    category: 'confidentialite',
    question: 'Que devient ma photo et mes données personnelles ?',
    answer:
      'Vos données sont hébergées de manière sécurisée et ne sont jamais revendues. Votre photo reste votre propriété : vous accordez uniquement une licence d’affichage dans le cadre du service. Vous pouvez demander la suppression de votre compte et de vos données à tout moment.',
  },
  {
    id: 'double-validation',
    category: 'services',
    question: 'Comment fonctionne la double validation OTP ?',
    answer:
      'Vous choisissez d’abord entre relation privée et certification publique. Votre partenaire reçoit un lien indiquant clairement ce choix. En cas de certification publique, le bouton précise que le statut binaire « En couple » deviendra consultable. Sans validation OTP, rien n’est publié.',
  },
  {
    id: 'plusieurs-relations',
    category: 'services',
    question: 'Peut-on déclarer plusieurs relations sur un même numéro ?',
    answer:
      'Oui, plusieurs déclarations mutuellement validées peuvent exister. En revanche, AntiGoumin n’affiche jamais leur nombre. Une recherche externe ne voit qu’un statut certifié binaire, et uniquement lorsqu’une certification publique active a été acceptée.',
  },
  {
    id: 'transparence',
    category: 'services',
    question: 'Qu’est-ce qu’une Demande de Transparence ?',
    answer:
      'C’est une invitation officielle, identifiable et non trompeuse. Le destinataire voit qui formule la demande et peut accepter, refuser, ignorer, bloquer ou signaler. La réponse reste privée. L’absence de réponse signifie uniquement que la demande a expiré : ce n’est pas une preuve de fidélité ou d’infidélité.',
  },
  {
    id: 'alliance',
    category: 'services',
    question: 'Qu’apporte l’Alliance Digitale VIP de plus ?',
    answer:
      'L’Alliance est un engagement mutuel : badge optionnel, forfait mensuel (5 vérifications, 1 déclaration, 1 Demande de Transparence) et notifications neutres. Le partenaire est notamment informé si la consultabilité publique est retirée ou si l’Alliance prend fin, sans motif ni information sur une autre relation. Chacun conserve son droit de retrait.',
  },
  {
    id: 'payment',
    category: 'paiement',
    question: 'Comment fonctionne le paiement ?',
    answer:
      'Via Mobile Money (Wave, Orange Money, MTN Mobile Money, Moov), par un agrégateur agréé. Chaque action (vérification, déclaration, Demande de Transparence) est facturée à la demande. L’Alliance Digitale VIP est un abonnement mensuel.',
  },
  {
    id: 'abonnement-resiliation',
    category: 'paiement',
    question: 'Puis-je résilier mon Alliance Digitale à tout moment ?',
    answer:
      'Oui, la résiliation se fait en un clic depuis votre profil et prend effet à la fin de la période en cours. Aucun engagement de durée n’est exigé. Les périodes déjà entamées ne sont pas remboursées au prorata.',
  },
  {
    id: 'remboursement',
    category: 'paiement',
    question: 'Que se passe-t-il si un paiement échoue ?',
    answer:
      'Si le débit a eu lieu sans que le service soit rendu, contactez-nous : le montant est recrédité ou l’action relancée. Les actions déjà exécutées ne sont pas remboursables, sauf erreur technique avérée de notre part.',
  },
  {
    id: 'artci',
    category: 'legal',
    question: "Est-ce légal vis-à-vis de l'ARTCI ?",
    answer:
      'Le cœur du service est le consentement : choix privé/public annoncé avant la double validation OTP, recherche binaire limitée aux certifications publiques, et Demande de Transparence identifiable. AntiGoumin s’inscrit dans la Loi n° 2013-450.',
  },
  {
    id: 'fausse-declaration',
    category: 'legal',
    question: 'Et si quelqu’un fait une fausse déclaration sur moi ?',
    answer:
      'C’est impossible sans votre accord : une déclaration ne devient publique qu’après votre validation par code OTP. Vous pouvez également refuser explicitement une déclaration, et signaler tout abus à notre équipe pour suspension du compte fautif.',
  },
]

const activeCategory = ref<CategoryId>('all')
const openId = ref<string | null>(faqs[0]?.id ?? null)

const visibleFaqs = computed(() =>
  activeCategory.value === 'all'
    ? faqs
    : faqs.filter((item) => item.category === activeCategory.value),
)

function toggle(id: string) {
  openId.value = openId.value === id ? null : id
}

function selectCategory(id: CategoryId) {
  activeCategory.value = id
  openId.value = null
}
</script>

<template>
  <section id="faq" class="scroll-mt-24 bg-white px-5 py-20 md:px-8 lg:px-10">
    <div class="mx-auto max-w-7xl">
      <div class="grid gap-12 lg:grid-cols-[1fr_1.6fr] lg:gap-16">
        <!-- Colonne intro -->
        <div class="lg:sticky lg:top-28 lg:self-start">
          <span
            class="inline-flex rounded-full bg-rose-50 px-4 py-1.5 text-xs font-bold uppercase tracking-wider text-[#ED147D]"
          >
            Foire aux questions
          </span>

          <h2 class="mt-5 font-display text-3xl font-extrabold text-blue-950 md:text-4xl">
            Des questions ? On vous dit tout.
          </h2>

          <p class="mt-4 text-lg leading-relaxed text-slate-600">
            Anonymat, paiement, cadre légal : voici les réponses aux questions que se posent le plus
            souvent nos utilisateurs avant de se lancer.
          </p>

          <!-- Bloc contact -->
          <div class="mt-8 rounded-2xl border border-slate-200 bg-slate-50 p-6">
            <p class="font-display text-base font-bold text-blue-950">
              Vous ne trouvez pas votre réponse ?
            </p>
            <p class="mt-2 text-sm leading-relaxed text-slate-600">
              Notre équipe répond sous 24 h ouvrées, en toute confidentialité.
            </p>

            <div class="mt-5 flex flex-col gap-3">
            <RouterLink
              to="/contact"
              class="inline-flex items-center gap-2 text-sm font-bold text-blue-950 transition hover:text-[#ED147D]"
            >
                <svg
                  class="h-4 w-4 shrink-0 text-[#ED147D]"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="1.75"
                  aria-hidden="true"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.917V6.75"
                  />
                </svg>
                {{ antiGouminService.contactEmail }}
              </RouterLink>

              <a
                :href="`tel:${antiGouminService.telephone.replace(/\s/g, '')}`"
                class="inline-flex items-center gap-2 text-sm font-bold text-blue-950 transition hover:text-[#ED147D]"
              >
                <svg
                  class="h-4 w-4 shrink-0 text-[#ED147D]"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="1.75"
                  aria-hidden="true"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 002.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 01-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 00-1.091-.852H4.5A2.25 2.25 0 002.25 4.5v2.25z"
                  />
                </svg>
                {{ antiGouminService.telephone }}
              </a>
            </div>

            <RouterLink
              to="/cgu"
              class="mt-5 inline-flex items-center gap-1 text-xs font-bold text-slate-500 transition hover:text-[#ED147D]"
            >
              Consulter les conditions générales
              <svg class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path
                  fill-rule="evenodd"
                  d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z"
                  clip-rule="evenodd"
                />
              </svg>
            </RouterLink>
          </div>
        </div>

        <!-- Colonne questions -->
        <div>
          <!-- Filtres par catégorie -->
          <div class="flex flex-wrap gap-2" role="tablist" aria-label="Filtrer les questions">
            <button
              v-for="category in categories"
              :key="category.id"
              type="button"
              role="tab"
              :aria-selected="activeCategory === category.id"
              class="rounded-full px-4 py-2 text-sm font-bold transition-all duration-200"
              :class="
                activeCategory === category.id
                  ? 'bg-[#ED147D] text-white shadow-md shadow-rose-200/60'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              "
              @click="selectCategory(category.id)"
            >
              {{ category.label }}
            </button>
          </div>

          <div class="mt-8 space-y-3">
            <div
              v-for="item in visibleFaqs"
              :key="item.id"
              class="overflow-hidden rounded-2xl border bg-white transition-all duration-300"
              :class="
                openId === item.id
                  ? 'border-[#ED147D]/40 shadow-lg shadow-rose-100/60'
                  : 'border-slate-200 shadow-sm hover:border-slate-300 hover:shadow-md'
              "
            >
              <button
                type="button"
                class="flex w-full items-center justify-between gap-4 px-6 py-5 text-left"
                :aria-expanded="openId === item.id"
                @click="toggle(item.id)"
              >
                <span
                  class="font-display text-base font-bold transition-colors duration-200 sm:text-lg"
                  :class="openId === item.id ? 'text-[#ED147D]' : 'text-blue-950'"
                >
                  {{ item.question }}
                </span>
                <span
                  class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full transition-all duration-300"
                  :class="
                    openId === item.id
                      ? 'rotate-180 bg-[#ED147D] text-white'
                      : 'bg-slate-100 text-slate-600'
                  "
                  aria-hidden="true"
                >
                  <svg class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path
                      fill-rule="evenodd"
                      d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.94a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
                      clip-rule="evenodd"
                    />
                  </svg>
                </span>
              </button>

              <div
                class="grid transition-all duration-300 ease-in-out"
                :class="
                  openId === item.id ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
                "
              >
                <div class="overflow-hidden">
                  <p
                    class="border-t border-slate-100 px-6 pb-5 pt-4 text-base leading-relaxed text-slate-600"
                  >
                    {{ item.answer }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.font-display {
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}
</style>
