<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { redirectToGeniusPay } from '@/api/checkout'
import { ApiError } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const payingId = ref('')
const checkoutError = ref('')
const servicePath = computed(() =>
  auth.isAuthenticated ? '/app' : '/connexion',
)

const checkoutServices: Record<string, 'DECLARATION' | 'TRANSPARENCY_REQUEST'> = {
  declare: 'DECLARATION',
  transparence: 'TRANSPARENCY_REQUEST',
}

async function handleCardAction(cardId: string) {
  checkoutError.value = ''
  if (!auth.isAuthenticated) {
    await router.push('/connexion')
    return
  }
  if (!auth.isFullyVerified) {
    await router.push('/app/profil')
    return
  }
  const service = checkoutServices[cardId]
  if (!service) {
    await router.push('/app/profil')
    return
  }
  payingId.value = cardId
  try {
    await redirectToGeniusPay({ service_type: service })
  } catch (err) {
    checkoutError.value =
      err instanceof ApiError ? err.message : 'Paiement impossible pour le moment.'
    payingId.value = ''
  }
}

interface PricingCard {
  id: string
  title: string
  price: string
  priceSuffix: string
  tagline: string
  features: string[]
  buttonLabel: string
  buttonTo: string
  icon: string
  cardBorder: string
  iconBg: string
  iconColor: string
  priceColor: string
  buttonClass: string
}

const actionCards: PricingCard[] = [
  {
    id: 'verify',
    title: 'Vérification',
    price: '200 FCFA',
    priceSuffix: '/ acte',
    tagline: 'Statut certifié avec consentement public',
    features: [
      'Uniquement pour les numéros inscrits et certifiés',
      'Résultat : engagé, disponible, ou non consultable',
      'Aucun nom, photo ni compteur de relations',
      'Consultabilité révocable à tout moment',
    ],
    buttonLabel: 'Vérifier un numéro',
    buttonTo: '/connexion',
    icon: 'M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z',
    cardBorder: 'border-blue-300',
    iconBg: 'bg-blue-50',
    iconColor: 'text-blue-600',
    priceColor: 'text-blue-700',
    buttonClass: 'border-blue-600 text-blue-700 hover:bg-blue-600 hover:text-white',
  },
  {
    id: 'declare',
    title: 'Déclaration',
    price: '300 FCFA',
    priceSuffix: '/ acte',
    tagline: 'Officialiser votre relation',
    features: [
      'Double validation par OTP',
      'Choix relation privée ou certification publique',
      'Refus et expiration possibles',
      'Mode public annoncé avant acceptation',
    ],
    buttonLabel: 'Déclarer ma relation',
    buttonTo: '/inscription',
    icon: 'M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z',
    cardBorder: 'border-[#ED147D]/40',
    iconBg: 'bg-rose-50',
    iconColor: 'text-[#ED147D]',
    priceColor: 'text-[#ED147D]',
    buttonClass: 'border-[#ED147D] text-[#ED147D] hover:bg-[#ED147D] hover:text-white',
  },
  {
    id: 'transparence',
    title: 'Demande de Transparence (Test de fidélité)',
    price: '550 FCFA',
    priceSuffix: '/ demande',
    tagline: 'Le test de fidélité responsable, officiel et identifiable',
    features: [
      'L’auteur est identifié auprès du destinataire',
      'Acceptation, refus, ignore ou signalement',
      'Réponse privée, jamais publiée d’office',
      'Le silence n’est pas une preuve',
    ],
    buttonLabel: 'Envoyer une demande',
    buttonTo: '/connexion',
    icon: 'M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5',
    cardBorder: 'border-amber-300',
    iconBg: 'bg-amber-50',
    iconColor: 'text-amber-600',
    priceColor: 'text-amber-600',
    buttonClass: 'border-amber-500 text-amber-700 hover:bg-amber-500 hover:text-white',
  },
]

const vipBenefits = [
  '5 Vérifications incluses',
  '1 Déclaration incluse',
  '1 Demande de Transparence incluse',
  'Badge VIP optionnel',
  'Notification neutre de fin d’Alliance',
]
</script>

<template>
  <section id="tarifs" class="scroll-mt-24 bg-slate-50 px-5 py-20 md:px-8 lg:px-10">
    <div class="mx-auto max-w-7xl">
      <div class="text-center">
        <h2 class="font-display text-3xl font-extrabold text-blue-950 md:text-4xl">Tarifs</h2>
        <p class="mx-auto mt-4 max-w-2xl text-lg text-slate-600">
          Choisissez le service dont vous avez besoin, ou optez pour l'Alliance Digitale VIP.
        </p>
        <p v-if="checkoutError" class="mt-3 text-sm font-semibold text-[#ED147D]">
          {{ checkoutError }}
        </p>
      </div>

      <div class="mt-14 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        <!-- Cartes à l'acte -->
        <article
          v-for="card in actionCards"
          :key="card.id"
          class="pricing-card rounded-2xl border bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-lg"
          :class="card.cardBorder"
        >
          <div
            class="flex h-12 w-12 items-center justify-center rounded-xl"
            :class="card.iconBg"
          >
            <svg
              class="h-6 w-6"
              :class="card.iconColor"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="1.75"
              aria-hidden="true"
            >
              <path stroke-linecap="round" stroke-linejoin="round" :d="card.icon" />
            </svg>
          </div>

          <div>
            <h3 class="font-display text-lg font-bold text-blue-950">{{ card.title }}</h3>
            <p class="mt-1 text-sm text-slate-500">{{ card.tagline }}</p>
          </div>

          <p class="pricing-card__price font-display text-3xl font-extrabold" :class="card.priceColor">
            {{ card.price }}
            <span class="text-base font-semibold text-slate-400">{{ card.priceSuffix }}</span>
          </p>

          <ul class="pricing-card__features space-y-2.5">
            <li
              v-for="feature in card.features"
              :key="feature"
              class="flex items-start gap-2 text-sm leading-snug text-slate-600"
            >
              <span
                class="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-slate-100 text-slate-500"
              >
                <svg class="h-2.5 w-2.5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path
                    fill-rule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clip-rule="evenodd"
                  />
                </svg>
              </span>
              {{ feature }}
            </li>
          </ul>

          <button
            v-if="checkoutServices[card.id]"
            type="button"
            class="inline-flex w-full items-center justify-center self-end rounded-xl border-2 px-4 py-3 text-sm font-bold transition"
            :class="card.buttonClass"
            :disabled="payingId === card.id"
            @click="handleCardAction(card.id)"
          >
            {{ payingId === card.id ? 'Redirection…' : card.buttonLabel }}
          </button>
          <RouterLink
            v-else
            :to="servicePath"
            class="inline-flex w-full items-center justify-center self-end rounded-xl border-2 px-4 py-3 text-sm font-bold transition"
            :class="card.buttonClass"
          >
            {{ card.buttonLabel }}
          </RouterLink>
        </article>

        <!-- Carte Alliance Digitale VIP -->
        <article
          id="alliance-vip"
          class="pricing-card relative scroll-mt-28 rounded-2xl border border-[#ED147D] bg-white p-6 shadow-xl shadow-rose-100/80 transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl"
        >
          <span
            class="absolute -top-3 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-full bg-[#ED147D] px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-white"
          >
            Recommandé
          </span>

          <div class="flex h-12 w-16 items-center justify-center rounded-xl bg-rose-50">
            <svg
              class="h-8 w-12"
              viewBox="0 0 160 96"
              fill="none"
              stroke-width="6"
              aria-hidden="true"
            >
              <ellipse cx="62" cy="56" rx="30" ry="32" stroke="#ED147D" />
              <ellipse cx="98" cy="56" rx="30" ry="32" stroke="#fbbf24" />
              <path d="M62 24l-7-9h14l-7 9z" fill="#ED147D" stroke="#ED147D" stroke-width="3" />
              <path d="M98 24l-7-9h14l-7 9z" fill="#fbbf24" stroke="#fbbf24" stroke-width="3" />
            </svg>
          </div>

          <div>
            <h3 class="font-display text-lg font-bold text-blue-950">Alliance Digitale VIP</h3>
            <p class="mt-1 text-sm text-slate-500">Le sceau de confiance ultime</p>
          </div>

          <p class="pricing-card__price font-display text-3xl font-extrabold text-[#ED147D]">
            1200 FCFA
            <span class="text-base font-semibold text-slate-400">/ mois</span>
          </p>

          <ul class="pricing-card__features space-y-2.5">
            <li
              v-for="benefit in vipBenefits"
              :key="benefit"
              class="flex items-start gap-2 text-sm leading-snug text-slate-700"
            >
              <span
                class="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-600"
              >
                <svg class="h-2.5 w-2.5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path
                    fill-rule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clip-rule="evenodd"
                  />
                </svg>
              </span>
              {{ benefit }}
            </li>
          </ul>

          <RouterLink
            :to="servicePath"
            class="inline-flex w-full items-center justify-center self-end rounded-xl bg-[#ED147D] px-4 py-3.5 text-sm font-bold text-white shadow-lg shadow-rose-200/60 transition hover:bg-[#d4126f] hover:shadow-xl"
          >
            Obtenir une Alliance Digitale
          </RouterLink>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.font-display {
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}

.pricing-card {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.pricing-card__features {
  flex: 1 1 auto;
}

/* Les quatre cartes partagent les mêmes lignes que la grille parente : icône,
   titre, prix, avantages et bouton restent alignés quelle que soit la longueur
   des textes. */
@supports (grid-template-rows: subgrid) {
  .pricing-card {
    display: grid;
    grid-row: span 5;
    grid-template-rows: subgrid;
  }
}
</style>
