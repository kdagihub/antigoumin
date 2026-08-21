<script setup lang="ts">
import { RouterLink } from 'vue-router'

import BrandMark from '@/components/BrandMark.vue'
import { legalEntity } from '@/content/legal-entity'
</script>

<template>
  <div class="legal-shell min-h-dvh bg-white">
    <header
      class="sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur-md"
    >
      <div class="legal-container flex items-center py-5">
        <RouterLink to="/" class="flex items-center gap-3" aria-label="AntiGoumin — Accueil">
          <BrandMark size="sm" />
          <span class="font-display text-xl font-bold text-blue-950">AntiGoumin</span>
        </RouterLink>
      </div>
    </header>

    <main class="legal-container legal-container--main">
      <slot />
    </main>

    <footer class="border-t border-slate-200 bg-slate-50">
      <div class="legal-container py-10 text-center">
        <nav class="flex justify-center gap-6 text-sm font-semibold" aria-label="Liens légaux">
          <RouterLink to="/cgu" class="text-slate-600 hover:text-[#ED147D]">CGU</RouterLink>
          <RouterLink to="/confidentialite" class="text-slate-600 hover:text-[#ED147D]"
            >Confidentialité</RouterLink
          >
          <RouterLink to="/contact" class="text-slate-600 hover:text-[#ED147D]">Contact</RouterLink>
          <RouterLink to="/" class="text-slate-600 hover:text-[#ED147D]">Accueil</RouterLink>
        </nav>
        <p class="mt-4 text-sm text-slate-500">
          {{ legalEntity.denomination }} — {{ legalEntity.siegeSocial }}
        </p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.font-display {
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}

.legal-container {
  width: 100%;
  max-width: 64rem;
  margin-left: auto;
  margin-right: auto;
  padding-left: 2rem;
  padding-right: 2rem;
}

.legal-container--main {
  padding-top: 2rem;
  padding-bottom: 3rem;
}

@media (min-width: 1024px) {
  .legal-container {
    max-width: 80rem;
    padding-left: 3rem;
    padding-right: 3rem;
  }

  .legal-container--main {
    padding-top: 3rem;
    padding-bottom: 4rem;
  }
}
</style>
