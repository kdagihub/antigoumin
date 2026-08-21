<script setup lang="ts">
import { RouterLink } from 'vue-router'

import BrandMark from '@/components/BrandMark.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>

<template>
  <div class="app-shell">
    <header class="app-shell__header">
      <div class="app-shell__header-inner">
        <RouterLink to="/" class="app-shell__brand" aria-label="AntiGoumin — Accueil">
          <BrandMark size="sm" />
          <span class="app-shell__title font-display">AntiGoumin</span>
        </RouterLink>

        <nav class="app-shell__nav" aria-label="Navigation principale">
          <RouterLink v-if="auth.isAuthenticated" to="/profil" class="app-shell__nav-link">
            <i class="pi pi-user" aria-hidden="true" />
            <span>Profil</span>
          </RouterLink>
          <RouterLink v-else to="/connexion" class="app-shell__nav-link">
            <i class="pi pi-sign-in" aria-hidden="true" />
            <span>Connexion</span>
          </RouterLink>
        </nav>
      </div>
    </header>

    <main class="app-shell__main">
      <div class="app-shell__content">
        <slot />
      </div>
    </main>

    <footer class="app-shell__footer">
      <nav class="app-shell__legal" aria-label="Informations légales">
        <RouterLink to="/cgu">CGU</RouterLink>
        <RouterLink to="/confidentialite">Confidentialité</RouterLink>
        <RouterLink to="/contact">Contact</RouterLink>
      </nav>
      <p>Le vaccin contre les surprises amoureuses.</p>
    </footer>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  background-color: #f8fafc;
}

.app-shell__header {
  padding: 0.875rem 1.25rem;
  background-color: var(--color-surface-raised);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 10;
}

.app-shell__header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  width: 100%;
  max-width: 64rem;
  margin: 0 auto;
}

.app-shell__brand {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  text-decoration: none;
  color: var(--color-ink);
}

.app-shell__title {
  font-size: 1.125rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.app-shell__nav-link {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  text-decoration: none;
  color: var(--color-primary);
  font-size: 0.875rem;
  font-weight: 600;
  border: 1px solid transparent;
}

.app-shell__nav-link:hover,
.app-shell__nav-link.router-link-active {
  background-color: var(--color-accent-soft);
  border-color: #fbcfe8;
}

.app-shell__main {
  flex: 1;
  padding: 1.5rem 1.25rem 2.5rem;
}

.app-shell__content {
  width: 100%;
  max-width: 40rem;
  margin: 0 auto;
}

@media (min-width: 768px) {
  .app-shell__main {
    padding: 2.5rem 2rem 3rem;
  }
}

.app-shell__footer {
  padding: 1rem 1.25rem 1.5rem;
  text-align: center;
  font-size: 0.8125rem;
  color: var(--color-muted);
  border-top: 1px solid var(--color-border);
  background-color: var(--color-surface-raised);
}

.app-shell__legal {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.app-shell__legal a {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.8125rem;
}

.app-shell__legal a:hover {
  text-decoration: underline;
}
</style>
