<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import logoAgm from '@/assets/img/logo_agm_sf.png'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()

const mobileMenuOpen = ref(false)
const servicesOpen = ref(false)

const serviceDropdownLinks = [
  { label: 'Vérification', to: '/#service-verification' },
  { label: 'Déclaration', to: '/#service-declaration' },
  {
    label: 'Demande de Transparence (Test de fidélité)',
    to: '/#service-transparence',
  },
]

const navLinks = [
  { label: 'Alliance Digitale VIP', to: '/#service-alliance' },
  { label: 'Tarifs', to: '/#tarifs' },
  { label: 'FAQ', to: '/#faq' },
  { label: 'Contact', to: '/contact' },
]

function isActive(to: string): boolean {
  const hash = to.includes('#') ? to.split('#')[1] : ''
  return route.path === '/' && hash !== '' && route.hash === `#${hash}`
}

function isServicesActive(): boolean {
  if (route.path !== '/') return false
  return (
    route.hash === '#services' ||
    serviceDropdownLinks.some((link) => route.hash === `#${link.to.split('#')[1]}`)
  )
}

function closeMobileMenu() {
  mobileMenuOpen.value = false
  servicesOpen.value = false
}

function toggleServices() {
  servicesOpen.value = !servicesOpen.value
}

function handleEscape(event: KeyboardEvent) {
  if (event.key === 'Escape') closeMobileMenu()
}

watch(mobileMenuOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
  if (open) {
    servicesOpen.value = isServicesActive()
    document.addEventListener('keydown', handleEscape)
  } else {
    servicesOpen.value = false
    document.removeEventListener('keydown', handleEscape)
  }
})

watch(() => route.fullPath, closeMobileMenu)

onBeforeUnmount(() => {
  document.body.style.overflow = ''
  document.removeEventListener('keydown', handleEscape)
})
</script>

<template>
  <header
    class="fixed inset-x-0 top-0 z-50 border-b border-slate-200/70 bg-white/90 backdrop-blur-lg"
  >
    <div class="relative mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-10">
      <RouterLink
        to="/#top"
        class="relative z-10 flex shrink-0 items-center gap-3"
        aria-label="AntiGoumin — Accueil"
      >
        <img
          :src="logoAgm"
          alt=""
          class="h-14 w-14 object-contain lg:h-16 lg:w-16"
          width="64"
          height="64"
        />
        <span class="font-display text-xl font-bold tracking-tight text-blue-950 lg:text-2xl">
          AntiGoumin
        </span>
      </RouterLink>

      <nav
        class="absolute left-1/2 hidden -translate-x-1/2 items-center gap-8 lg:flex"
        aria-label="Navigation principale"
      >
        <RouterLink
          to="/#top"
          class="text-sm font-semibold transition-colors duration-200"
          :class="isActive('/#top') ? 'text-[#ED147D]' : 'text-slate-600 hover:text-[#ED147D]'"
        >
          Accueil
        </RouterLink>

        <!-- Menu déroulant Nos Services -->
        <div class="group relative">
          <RouterLink
            to="/#services"
            class="inline-flex items-center gap-1 text-sm font-semibold transition-colors duration-200"
            :class="isServicesActive() ? 'text-[#ED147D]' : 'text-slate-600 hover:text-[#ED147D]'"
          >
            Nos Services
            <svg
              class="h-4 w-4 transition-transform duration-200 group-hover:rotate-180"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path
                fill-rule="evenodd"
                d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.94a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
                clip-rule="evenodd"
              />
            </svg>
          </RouterLink>

          <div
            class="invisible absolute left-1/2 top-full z-50 mt-2 w-52 -translate-x-1/2 rounded-xl border border-slate-200 bg-white py-2 opacity-0 shadow-xl transition-all duration-200 group-hover:visible group-hover:opacity-100"
          >
            <RouterLink
              v-for="item in serviceDropdownLinks"
              :key="item.label"
              :to="item.to"
              class="block px-4 py-2.5 text-sm font-semibold text-slate-600 transition hover:bg-rose-50 hover:text-[#ED147D]"
            >
              {{ item.label }}
            </RouterLink>
          </div>
        </div>

        <RouterLink
          v-for="link in navLinks"
          :key="link.label"
          :to="link.to"
          class="text-sm font-semibold transition-colors duration-200"
          :class="isActive(link.to) ? 'text-[#ED147D]' : 'text-slate-600 hover:text-[#ED147D]'"
        >
          {{ link.label }}
        </RouterLink>
      </nav>

      <div class="relative z-10 flex shrink-0 items-center gap-3">
        <!-- Actions bureau -->
        <div class="hidden items-center gap-3 lg:flex">
          <RouterLink
            v-if="auth.isAuthenticated"
            to="/profil"
            class="rounded-xl border border-transparent px-4 py-2.5 text-sm font-bold text-blue-950 transition hover:bg-slate-100"
          >
            Mon profil
          </RouterLink>
          <template v-else>
            <RouterLink
              to="/connexion"
              class="rounded-xl border border-transparent px-4 py-2.5 text-sm font-bold text-blue-950 transition hover:bg-slate-100"
            >
              Connexion
            </RouterLink>
            <RouterLink
              to="/inscription"
              class="inline-flex items-center justify-center rounded-xl bg-[#ED147D] px-5 py-2.5 text-sm font-bold text-white shadow-md shadow-rose-200/60 transition hover:bg-[#d4126f] hover:shadow-lg"
            >
              S'inscrire
            </RouterLink>
          </template>
        </div>

        <!-- Bouton burger -->
        <button
          type="button"
          class="inline-flex h-11 w-11 items-center justify-center rounded-xl border border-slate-200 bg-white text-blue-950 transition hover:bg-slate-50 lg:hidden"
          :aria-expanded="mobileMenuOpen"
          aria-controls="mobile-menu"
          :aria-label="mobileMenuOpen ? 'Fermer le menu' : 'Ouvrir le menu'"
          @click="mobileMenuOpen = !mobileMenuOpen"
        >
          <svg
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
            aria-hidden="true"
          >
            <path
              v-if="mobileMenuOpen"
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M6 18L18 6M6 6l12 12"
            />
            <path v-else stroke-linecap="round" stroke-linejoin="round" d="M4 7h16M4 12h16M4 17h16" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Menu mobile -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="-translate-y-2 opacity-0"
      leave-active-class="transition duration-150 ease-in"
      leave-to-class="-translate-y-2 opacity-0"
    >
      <div
        v-if="mobileMenuOpen"
        id="mobile-menu"
        class="max-h-[calc(100dvh-5.5rem)] overflow-y-auto border-t border-slate-200 bg-white px-5 pb-8 pt-4 lg:hidden"
      >
        <nav class="flex flex-col" aria-label="Navigation mobile">
          <RouterLink
            to="/#top"
            class="rounded-xl px-3 py-3 text-base font-semibold transition"
            :class="isActive('/#top') ? 'bg-rose-50 text-[#ED147D]' : 'text-slate-700 hover:bg-slate-50'"
            @click="closeMobileMenu"
          >
            Accueil
          </RouterLink>

          <button
            type="button"
            class="flex w-full items-center justify-between rounded-xl px-3 py-3 text-left text-base font-semibold transition"
            :class="
              isServicesActive() || servicesOpen
                ? 'bg-rose-50 text-[#ED147D]'
                : 'text-slate-700 hover:bg-slate-50'
            "
            :aria-expanded="servicesOpen"
            aria-controls="mobile-services"
            @click="toggleServices"
          >
            Nos Services
            <svg
              class="h-5 w-5 shrink-0 transition-transform duration-200"
              :class="servicesOpen ? 'rotate-180' : ''"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path
                fill-rule="evenodd"
                d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.94a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
                clip-rule="evenodd"
              />
            </svg>
          </button>
          <div v-show="servicesOpen" id="mobile-services" class="ml-3 flex flex-col border-l border-slate-200 pl-3">
            <RouterLink
              to="/#services"
              class="rounded-lg px-3 py-2.5 text-sm font-medium transition"
              :class="isActive('/#services') ? 'text-[#ED147D]' : 'text-slate-600 hover:bg-slate-50'"
              @click="closeMobileMenu"
            >
              Vue d’ensemble
            </RouterLink>
            <RouterLink
              v-for="item in serviceDropdownLinks"
              :key="item.label"
              :to="item.to"
              class="rounded-lg px-3 py-2.5 text-sm font-medium transition"
              :class="isActive(item.to) ? 'text-[#ED147D]' : 'text-slate-600 hover:bg-slate-50'"
              @click="closeMobileMenu"
            >
              {{ item.label }}
            </RouterLink>
          </div>

          <RouterLink
            v-for="link in navLinks"
            :key="link.label"
            :to="link.to"
            class="rounded-xl px-3 py-3 text-base font-semibold transition"
            :class="isActive(link.to) ? 'bg-rose-50 text-[#ED147D]' : 'text-slate-700 hover:bg-slate-50'"
            @click="closeMobileMenu"
          >
            {{ link.label }}
          </RouterLink>
        </nav>

        <div class="mt-5 flex flex-col gap-3 border-t border-slate-200 pt-5">
          <RouterLink
            v-if="auth.isAuthenticated"
            to="/profil"
            class="inline-flex w-full items-center justify-center rounded-xl bg-[#ED147D] px-5 py-3.5 text-base font-bold text-white shadow-md shadow-rose-200/60 transition hover:bg-[#d4126f]"
            @click="closeMobileMenu"
          >
            Mon profil
          </RouterLink>
          <template v-else>
            <RouterLink
              to="/inscription"
              class="inline-flex w-full items-center justify-center rounded-xl bg-[#ED147D] px-5 py-3.5 text-base font-bold text-white shadow-md shadow-rose-200/60 transition hover:bg-[#d4126f]"
              @click="closeMobileMenu"
            >
              S'inscrire
            </RouterLink>
            <RouterLink
              to="/connexion"
              class="inline-flex w-full items-center justify-center rounded-xl border-2 border-slate-200 px-5 py-3.5 text-base font-bold text-blue-950 transition hover:border-slate-300 hover:bg-slate-50"
              @click="closeMobileMenu"
            >
              Connexion
            </RouterLink>
          </template>
        </div>
      </div>
    </Transition>
  </header>

  <!-- Fond assombri derrière le menu mobile -->
  <Transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0"
    leave-active-class="transition duration-150 ease-in"
    leave-to-class="opacity-0"
  >
    <div
      v-if="mobileMenuOpen"
      class="fixed inset-0 z-40 bg-slate-950/40 lg:hidden"
      aria-hidden="true"
      @click="closeMobileMenu"
    />
  </Transition>
</template>

<style scoped>
.font-display {
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}
</style>
