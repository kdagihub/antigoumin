<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { redirectToGeniusPay } from '@/api/checkout'
import { ApiError } from '@/api/client'
import heroImage from '@/assets/img/heroe1.jpeg'
import heroFallback from '@/assets/img/hero-bg.jpg'
import { useAuthStore } from '@/stores/auth'

const heroSrc = ref(heroImage)

const router = useRouter()
const auth = useAuthStore()

function onHeroError() {
  heroSrc.value = heroFallback
}
const phoneQuery = ref('')
const checkoutError = ref('')
const paying = ref(false)

const vipAlliances = [
  { id: '1', sealedAgo: 'Il y a 2 min' },
  { id: '2', sealedAgo: 'Il y a 8 min' },
  { id: '3', sealedAgo: 'Il y a 14 min' },
]

const marqueeCards = [...vipAlliances, ...vipAlliances]

const trustValues = [
  {
    id: 'security',
    label: 'Sécurité',
    icon: 'M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z',
  },
  {
    id: 'reliability',
    label: 'Fiabilité',
    icon: 'M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z',
  },
  {
    id: 'transparency',
    label: 'Transparence',
    icon: 'M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
  },
  {
    id: 'privacy',
    label: 'Confidentialité des données',
    icon: 'M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z',
  },
]

const heroServiceActions = [
  {
    id: 'declaration',
    label: 'Déclarer / officialiser ma relation',
    price: '300 FCFA',
    icon: 'M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z',
    accent: 'border-rose-400/30 hover:border-[#ED147D]/60 hover:bg-[#ED147D]/10',
    route: '/app/declarations',
  },
  {
    id: 'transparency',
    label: 'Faire un test de Transparence / de fidélité',
    price: '550 FCFA',
    icon: 'M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5',
    accent: 'border-amber-400/30 hover:border-amber-300/60 hover:bg-amber-400/10',
    route: '/app/transparence',
  },
  {
    id: 'alliance',
    label: 'Obtenir mon Alliance Digitale',
    price: '990 FCFA/mois',
    icon: 'M12 2l2.4 4.8L20 8l-3.6 3.5L17.5 18 12 15.2 6.5 18l1.1-6.5L4 8l5.6-1.2L12 2z',
    iconFill: true,
    accent: 'border-amber-300/40 hover:border-amber-200/70 hover:bg-amber-400/10',
    hash: '#alliance-vip',
    route: '/app/abonnement',
  },
]

async function handleVerify() {
  const q = phoneQuery.value.trim()
  checkoutError.value = ''
  if (!auth.isAuthenticated) {
    await router.push({
      name: 'login',
      query: q ? { redirect: '/', phone: q } : {},
    })
    return
  }
  if (!auth.isFullyVerified) {
    await router.push('/app')
    return
  }
  if (!q) {
    checkoutError.value = 'Saisissez un numéro à vérifier.'
    return
  }
  paying.value = true
  try {
    await redirectToGeniusPay({ service_type: 'VERIFICATION', phone: q })
  } catch (err) {
    checkoutError.value =
      err instanceof ApiError ? err.message : 'Paiement impossible pour le moment.'
    paying.value = false
  }
}

async function handleServiceAction(action: (typeof heroServiceActions)[number]) {
  if (!auth.isAuthenticated) {
    if (action.hash) {
      await router.push({ path: '/', hash: action.hash })
      return
    }
    await router.push({
      name: 'login',
      query: { redirect: action.route },
    })
    return
  }

  if (!auth.isFullyVerified) {
    await router.push('/app/profil')
    return
  }

  await router.push(action.route)
}
</script>

<template>
  <section id="top" class="relative flex min-h-screen flex-col overflow-hidden">
    <!-- Image de fond pleine largeur (locale — l'URL Unsplash fournie renvoie 404) -->
    <img
      :src="heroSrc"
      alt=""
      class="absolute inset-0 z-0 h-full w-full object-cover object-[71%_center] lg:object-center"
      width="1920"
      height="1280"
      loading="eager"
      fetchpriority="high"
      @error="onHeroError"
    />

    <!-- Calque assombrissant : lisibilité à gauche, image visible à droite -->
    <div
      class="absolute inset-0 z-10 bg-gradient-to-r from-slate-950/95 via-slate-900/70 to-slate-900/20"
      aria-hidden="true"
    />

    <!-- Contenu : centré verticalement + barre réassurance ancrée en bas -->
    <div class="relative z-20 flex flex-1 flex-col">
      <div class="flex flex-1 items-center px-5 pt-24 lg:px-10 lg:pt-28">
        <div
          class="mx-auto grid w-full max-w-7xl grid-cols-1 items-center gap-12 lg:grid-cols-2 lg:gap-16"
        >
          <!-- Colonne gauche -->
          <div>
        <p
          class="animate-fade-up mb-5 inline-block rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-sm font-bold text-white backdrop-blur-md"
        >
          Le 1<sup class="ordinal">er</sup> registre de confiance mutuel en Côte d'Ivoire
        </p>

        <h1
          class="animate-fade-up font-display text-4xl font-extrabold leading-[1.06] tracking-tight text-white sm:text-5xl lg:text-6xl"
          style="animation-delay: 80ms"
        >
          Sécurise ta relation amoureuse et
          <span class="text-[#ED147D]">protège ton cœur&nbsp;!</span>
        </h1>

        <p
          class="animate-fade-up mt-6 max-w-xl text-lg leading-relaxed text-slate-300 lg:text-xl"
          style="animation-delay: 160ms"
        >
          Vérifie un statut certifié, déclare ton partenaire ou envoie une demande de transparence.
        </p>

        <!-- Barre de recherche glassmorphism -->
        <form
          class="animate-fade-up mt-10"
          style="animation-delay: 240ms"
          @submit.prevent="handleVerify"
        >
          <label for="hero-phone" class="sr-only">Numéro de téléphone à vérifier</label>
          <div
            class="flex flex-col gap-3 rounded-2xl border border-white/20 bg-white/10 p-2 backdrop-blur-md sm:flex-row sm:items-center"
          >
            <input
              id="hero-phone"
              v-model="phoneQuery"
              type="tel"
              inputmode="tel"
              autocomplete="tel"
              placeholder="Ex: 07 XX XX XX XX..."
              class="min-w-0 flex-1 rounded-xl border-0 bg-transparent px-4 py-4 text-base font-medium text-white placeholder:text-slate-400 focus:outline-none focus:ring-0"
            />
            <button
              type="submit"
              class="cta-verify shrink-0 rounded-xl bg-[#ED147D] px-6 py-4 text-base font-bold text-white shadow-lg shadow-rose-900/40 transition hover:scale-[1.02] hover:bg-[#d4126f] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#ED147D] sm:px-8"
              :disabled="paying"
            >
              {{ paying ? 'Redirection…' : 'Vérifier (200 FCFA)' }}
            </button>
          </div>
          <p v-if="checkoutError" class="mt-3 text-sm text-rose-200">{{ checkoutError }}</p>
          <p class="mt-3 text-xs text-slate-400">
            Paiement sécurisé via Mobile Money · Résultat instantané
          </p>
        </form>
      </div>

      <!-- Colonne droite : Mur des Alliances VIP -->
      <div class="animate-fade-up" style="animation-delay: 120ms">
        <div class="mx-auto max-w-md lg:max-w-none">
          <h2
            class="mb-5 flex items-center gap-2 text-sm font-bold uppercase tracking-wide text-amber-200/90"
          >
            <svg
              class="h-5 w-5 shrink-0 text-amber-300"
              viewBox="0 0 24 24"
              fill="currentColor"
              aria-hidden="true"
            >
              <path
                d="M12 2l2.4 4.8L20 8l-3.6 3.5L17.5 18 12 15.2 6.5 18l1.1-6.5L4 8l5.6-1.2L12 2z"
              />
            </svg>
            Ils ont scellé leur Alliance
            <span class="font-normal normal-case text-slate-400">(Vue restreinte)</span>
          </h2>

          <div
            class="relative h-[22rem] overflow-hidden rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm sm:h-[26rem]"
          >
            <!-- Masques haut / bas -->
            <div
              class="pointer-events-none absolute inset-x-0 top-0 z-10 h-16 bg-gradient-to-b from-slate-950/80 to-transparent"
              aria-hidden="true"
            />
            <div
              class="pointer-events-none absolute inset-x-0 bottom-0 z-10 h-16 bg-gradient-to-t from-slate-950/80 to-transparent"
              aria-hidden="true"
            />

            <div class="hero-marquee flex flex-col gap-4 px-4 py-6">
              <article
                v-for="(card, index) in marqueeCards"
                :key="`${card.id}-${index}`"
                class="vip-card group relative shrink-0 cursor-not-allowed rounded-xl border border-amber-400/40 bg-white/10 p-5 backdrop-blur-md transition duration-300 hover:border-[#ED147D]/60 hover:bg-white/15"
                :title="'Abonnez-vous pour débloquer'"
              >
                <!-- Info-bulle au survol -->
                <div
                  class="pointer-events-none absolute -top-2 left-1/2 z-20 -translate-x-1/2 -translate-y-full whitespace-nowrap rounded-lg bg-slate-950/95 px-3 py-1.5 text-xs font-semibold text-white opacity-0 shadow-lg ring-1 ring-white/10 transition-opacity duration-200 group-hover:opacity-100"
                  role="tooltip"
                >
                  Abonnez-vous pour débloquer
                  <span
                    class="absolute -bottom-1 left-1/2 h-2 w-2 -translate-x-1/2 rotate-45 bg-slate-950/95 ring-1 ring-white/10"
                    aria-hidden="true"
                  />
                </div>

                <div class="flex items-start gap-4">
                  <!-- Icône cadenas -->
                  <div
                    class="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl border border-amber-400/30 bg-amber-400/10"
                  >
                    <svg
                      class="h-7 w-7 text-amber-300"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.75"
                      aria-hidden="true"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"
                      />
                    </svg>
                  </div>

                  <div class="min-w-0 flex-1">
                    <p class="font-display text-base font-bold text-white">
                      Alliance scellée récemment
                    </p>
                    <p class="mt-1 text-xs text-slate-400">{{ card.sealedAgo }}</p>
                    <span
                      class="mt-3 inline-flex items-center gap-1.5 rounded-full border border-[#ED147D]/40 bg-[#ED147D]/15 px-3 py-1 text-[11px] font-bold uppercase tracking-wide text-[#ED147D]"
                    >
                      <svg class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path
                          fill-rule="evenodd"
                          d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
                          clip-rule="evenodd"
                        />
                      </svg>
                      Réservé aux membres VIP
                    </span>
                  </div>
                </div>
              </article>
            </div>
          </div>

          <RouterLink
            to="/#alliance-vip"
            class="mt-5 inline-flex items-center gap-2 text-sm font-bold text-amber-200 transition hover:text-[#ED147D]"
          >
            Découvrir l'Alliance Digital VIP — 1200 FCFA/mois
            <svg class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path
                fill-rule="evenodd"
                d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z"
                clip-rule="evenodd"
              />
            </svg>
          </RouterLink>
        </div>
      </div>
        </div>
      </div>

      <!-- Actions services (CTA secondaires) -->
      <div class="relative z-20 w-full px-5 pt-6 lg:px-10">
        <div class="mx-auto grid max-w-7xl gap-3 sm:grid-cols-2 lg:grid-cols-3 lg:gap-4">
          <button
            v-for="action in heroServiceActions"
            :key="action.id"
            type="button"
            class="group flex items-center gap-4 rounded-2xl border bg-white/5 p-4 text-left backdrop-blur-md transition duration-300 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-black/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#ED147D]"
            :class="action.accent"
            @click="handleServiceAction(action)"
          >
            <span
              class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-white/10 text-[#ED147D] transition group-hover:scale-105 group-hover:bg-[#ED147D]/15"
            >
              <svg
                v-if="action.iconFill"
                class="h-6 w-6 text-amber-300"
                viewBox="0 0 24 24"
                fill="currentColor"
                aria-hidden="true"
              >
                <path :d="action.icon" />
              </svg>
              <svg
                v-else
                class="h-6 w-6"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.75"
                aria-hidden="true"
              >
                <path stroke-linecap="round" stroke-linejoin="round" :d="action.icon" />
              </svg>
            </span>
            <span class="min-w-0 flex-1">
              <span class="block font-display text-sm font-bold leading-snug text-white sm:text-base">
                {{ action.label }}
              </span>
              <span
                class="mt-1 inline-flex rounded-full bg-white/10 px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-wide text-slate-300"
              >
                {{ action.price }}
              </span>
            </span>
            <svg
              class="h-5 w-5 shrink-0 text-slate-500 transition group-hover:translate-x-0.5 group-hover:text-white"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path
                fill-rule="evenodd"
                d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z"
                clip-rule="evenodd"
              />
            </svg>
          </button>
        </div>
      </div>

      <!-- Barre Valeurs et Confiance (ancrée en bas) -->
      <div class="relative z-20 mt-auto w-full px-5 pb-8 pt-4 lg:px-10">
        <p class="mb-4 text-center text-xs uppercase tracking-widest text-white/60">
          Nos engagements de confiance
        </p>
        <div class="flex flex-wrap items-center justify-center gap-4 md:gap-8">
          <span
            v-for="value in trustValues"
            :key="value.id"
            class="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-5 py-2 text-sm font-medium text-white backdrop-blur-sm"
          >
            <svg
              class="h-4 w-4 shrink-0 text-[#ED147D]"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.75"
              aria-hidden="true"
            >
              <path stroke-linecap="round" stroke-linejoin="round" :d="value.icon" />
            </svg>
            {{ value.label }}
          </span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.font-display {
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}

@keyframes fade-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-up {
  animation: fade-up 0.7s ease-out both;
}

.ordinal {
  font-size: 0.65em;
  line-height: 0;
  vertical-align: super;
}

@keyframes marquee-vertical {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-50%);
  }
}

.hero-marquee {
  animation: marquee-vertical 20s linear infinite;
}

.hero-marquee:hover {
  animation-play-state: paused;
}

.vip-card {
  cursor: not-allowed;
}

.cta-verify {
  animation: pulse-soft 2.5s ease-in-out infinite;
}

@keyframes pulse-soft {
  0%,
  100% {
    box-shadow: 0 10px 25px -5px rgba(237, 20, 125, 0.35);
  }
  50% {
    box-shadow: 0 14px 32px -4px rgba(237, 20, 125, 0.55);
  }
}
</style>
