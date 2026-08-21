<script setup lang="ts">
import { RouterLink } from 'vue-router'

interface ServiceCard {
  id: string
  title: string
  description: string
  icon: string
  iconBg: string
  iconColor: string
}

const services: ServiceCard[] = [
  {
    id: 'verification',
    title: 'Vérification du statut certifié',
    description:
      'Consultez le statut certifié d’un numéro inscrit uniquement si une certification publique a été acceptée. Résultat binaire : engagé, disponible, ou non répertorié / non consultable — sans nom, sans compteur, sans historique.',
    icon: 'M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z',
    iconBg: 'bg-blue-50',
    iconColor: 'text-blue-600',
  },
  {
    id: 'declaration',
    title: 'Déclarer votre relation amoureuse',
    description:
      'Choisissez une relation privée ou une certification publique. Votre partenaire voit clairement ce choix avant la double validation OTP. Seule la certification publique rend le statut binaire « En couple » consultable.',
    icon: 'M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z',
    iconBg: 'bg-rose-50',
    iconColor: 'text-[#ED147D]',
  },
  {
    id: 'transparence',
    title: 'Demande de Transparence (Test de fidélité)',
    description:
      'Le test de fidélité responsable d’AntiGoumin : invitez officiellement une personne à clarifier ou certifier son statut. La demande est identifiable, volontaire et sans piège : le destinataire peut accepter, refuser, ignorer ou signaler un abus. L’absence de réponse ne prouve rien.',
    icon: 'M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5',
    iconBg: 'bg-amber-50',
    iconColor: 'text-amber-600',
  },
]

/** Fonctionnement de l'Alliance Digitale en 3 temps */
const allianceSteps = [
  {
    number: '01',
    title: 'Vous scellez',
    text: 'Après la double validation OTP, vous et votre partenaire transformez votre déclaration en Alliance Digitale.',
  },
  {
    number: '02',
    title: 'Le registre certifie',
    text: 'Votre couple reçoit un badge certifié et apparaît comme relation vérifiée dans le registre de confiance.',
  },
  {
    number: '03',
    title: 'Vous êtes informés',
    text: 'Si l’Alliance prend fin, chaque partie reçoit une notification neutre. Aucun motif ni autre statut relationnel n’est communiqué.',
  },
]

const allianceBenefits = [
  'Badge d’Alliance certifié, affichable uniquement avec l’accord des deux parties',
  'Notification neutre si l’Alliance prend fin',
  'Chacun peut retirer son consentement et supprimer son compte à tout moment',
  '5 vérifications, 1 déclaration et 1 Demande de Transparence incluses chaque mois',
  'Présence optionnelle parmi les couples certifiés',
  'Support prioritaire et historique de vos actions',
]
</script>

<template>
  <section id="services" class="scroll-mt-24 bg-white px-5 py-20 md:px-8 lg:px-10">
    <div class="mx-auto max-w-7xl">
      <div class="text-center">
        <h2 class="font-display text-3xl font-extrabold text-blue-950 md:text-4xl">
          Une protection complète pour votre cœur
        </h2>
        <p class="mx-auto mt-4 max-w-2xl text-lg text-slate-600">
          Trois piliers pour sécuriser votre relation, et une Alliance pour la sceller.
        </p>
      </div>

      <div class="mt-14 grid grid-cols-1 gap-8 md:grid-cols-3">
        <article
          v-for="service in services"
          :id="`service-${service.id}`"
          :key="service.id"
          class="scroll-mt-28 flex flex-col rounded-2xl border border-slate-200 bg-white p-8 shadow-md transition-all duration-300 hover:-translate-y-1 hover:shadow-xl"
        >
          <div
            class="flex h-16 w-16 items-center justify-center rounded-full"
            :class="service.iconBg"
          >
            <svg
              class="h-8 w-8"
              :class="service.iconColor"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="1.75"
              aria-hidden="true"
            >
              <path stroke-linecap="round" stroke-linejoin="round" :d="service.icon" />
            </svg>
          </div>

          <h3 class="mt-4 font-display text-xl font-bold text-blue-950">
            {{ service.title }}
          </h3>

          <p class="mt-2 flex-1 text-sm leading-relaxed text-slate-600">
            {{ service.description }}
          </p>
        </article>
      </div>

      <!-- Carte détaillée Alliance Digitale VIP -->
      <article
        id="service-alliance"
        class="mt-8 scroll-mt-28 overflow-hidden rounded-2xl border-2 border-[#ED147D]/30 bg-blue-950 shadow-xl transition-all duration-300 hover:shadow-2xl"
      >
        <div class="grid gap-10 p-8 lg:grid-cols-[1.15fr_1fr] lg:gap-14 lg:p-12">
          <!-- Explication -->
          <div>
            <span
              class="inline-flex items-center gap-2 rounded-full bg-[#ED147D]/15 px-4 py-1.5 text-xs font-bold uppercase tracking-wider text-[#ED147D]"
            >
              Le sceau de confiance ultime
            </span>

            <h3 class="mt-5 font-display text-2xl font-extrabold text-white md:text-3xl">
              Alliance Digitale VIP
            </h3>

            <p class="mt-4 text-base leading-relaxed text-slate-300">
              L’Alliance Digitale est un engagement mutuel certifié. Elle n’est active qu’après
              le consentement distinct de chaque partenaire. Chacun peut y mettre fin à tout
              moment : le badge cesse d’être affiché, et l’autre partie est seulement informée
              que l’Alliance a pris fin.
            </p>

            <!-- Fonctionnement en 3 temps -->
            <div class="mt-8 space-y-5">
              <div v-for="step in allianceSteps" :key="step.number" class="flex gap-4">
                <span
                  class="font-display shrink-0 text-lg font-extrabold text-[#ED147D]"
                  aria-hidden="true"
                >
                  {{ step.number }}
                </span>
                <div>
                  <p class="font-display text-base font-bold text-white">{{ step.title }}</p>
                  <p class="mt-1 text-sm leading-relaxed text-slate-400">{{ step.text }}</p>
                </div>
              </div>
            </div>

            <RouterLink
              to="/#alliance-vip"
              class="mt-9 inline-flex items-center justify-center gap-2 rounded-xl bg-[#ED147D] px-6 py-3.5 text-sm font-bold text-white shadow-lg shadow-rose-900/30 transition hover:bg-[#d4126f]"
            >
              Obtenir une Alliance Digitale
              <svg class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path
                  fill-rule="evenodd"
                  d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z"
                  clip-rule="evenodd"
                />
              </svg>
            </RouterLink>
          </div>

          <!-- Visuel alliances + avantages -->
          <div class="flex flex-col">
            <div
              class="flex items-center justify-center rounded-2xl border border-white/10 bg-white/5 py-8 backdrop-blur-sm"
            >
              <svg
                class="h-24 w-40"
                viewBox="0 0 160 96"
                fill="none"
                stroke-width="4"
                aria-hidden="true"
              >
                <ellipse cx="62" cy="56" rx="30" ry="32" stroke="#ED147D" />
                <ellipse cx="98" cy="56" rx="30" ry="32" stroke="#fbbf24" />
                <path
                  d="M62 24l-7-9h14l-7 9z"
                  fill="#ED147D"
                  stroke="#ED147D"
                  stroke-width="2"
                />
                <path d="M98 24l-7-9h14l-7 9z" fill="#fbbf24" stroke="#fbbf24" stroke-width="2" />
              </svg>
            </div>

            <p class="mt-6 text-xs font-bold uppercase tracking-widest text-amber-200/80">
              Vos avantages
            </p>

            <ul class="mt-4 space-y-3">
              <li
                v-for="benefit in allianceBenefits"
                :key="benefit"
                class="flex items-start gap-3 text-sm leading-relaxed text-slate-300"
              >
                <span
                  class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400"
                >
                  <svg class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
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
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.font-display {
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}
</style>
