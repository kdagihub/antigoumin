<script setup lang="ts">
import { RouterLink } from 'vue-router'

import logoAgm from '@/assets/img/logo_agm_sf.png'
</script>

<template>
  <footer id="contact" class="scroll-mt-24 border-t border-slate-200 bg-white px-5 py-12 md:px-8 lg:px-10">
    <div
      class="mx-auto flex max-w-7xl flex-col items-start justify-between gap-8 md:flex-row md:items-center"
    >
      <div class="flex items-center gap-3">
        <img :src="logoAgm" alt="" class="h-10 w-10 object-contain" width="40" height="40" />
        <div>
          <p class="font-display text-lg font-bold text-blue-950">AntiGoumin</p>
          <p class="text-sm text-slate-500">© 2026 AntiGoumin. Tous droits réservés.</p>
        </div>
      </div>

      <nav
        class="flex flex-col gap-3 text-sm font-semibold sm:flex-row sm:items-center sm:gap-8"
        aria-label="Liens légaux"
      >
        <RouterLink to="/cgu" class="text-slate-600 transition hover:text-[#ED147D]">
          Conditions Générales d'Utilisation
        </RouterLink>
        <RouterLink to="/confidentialite" class="text-slate-600 transition hover:text-[#ED147D]">
          Politique de Confidentialité
        </RouterLink>
        <RouterLink to="/contact" class="text-slate-600 transition hover:text-[#ED147D]">
          Contact
        </RouterLink>
      </nav>
    </div>
  </footer>
</template>

<style scoped>
.font-display {
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}
</style>
