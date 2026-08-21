<script setup lang="ts">
import { RouterLink } from 'vue-router'

import BrandMark from '@/components/BrandMark.vue'

withDefaults(
  defineProps<{
    title: string
    subtitle: string
    highlights?: string[]
  }>(),
  {
    highlights: () => [
      'Aucune relation certifiée sans double validation OTP',
      'Statut consultable uniquement avec votre accord',
      'Consentement révocable à tout moment',
    ],
  },
)
</script>

<template>
  <div class="auth-layout">
    <aside class="auth-layout__aside">
      <RouterLink to="/" class="auth-layout__brand">
        <BrandMark size="md" />
        <span class="font-display">AntiGoumin</span>
      </RouterLink>

      <div class="auth-layout__pitch">
        <h2 class="font-display">Le registre de confiance mutuelle</h2>
        <p>
          Sécurisez votre relation amoureuse avec un service fondé sur le consentement, en Côte
          d'Ivoire.
        </p>
        <ul>
          <li v-for="highlight in highlights" :key="highlight">
            <i class="pi pi-check-circle" aria-hidden="true" />
            <span>{{ highlight }}</span>
          </li>
        </ul>
      </div>

      <p class="auth-layout__footnote">Le vaccin contre les surprises amoureuses.</p>
    </aside>

    <div class="auth-layout__panel">
      <header class="auth-layout__header">
        <RouterLink to="/" class="auth-layout__header-brand" aria-label="AntiGoumin — Accueil">
          <BrandMark size="sm" />
          <span class="font-display">AntiGoumin</span>
        </RouterLink>
        <RouterLink to="/" class="auth-layout__header-link">
          <i class="pi pi-arrow-left" aria-hidden="true" />
          <span>Accueil</span>
        </RouterLink>
      </header>

      <main class="auth-layout__main">
        <div class="auth-card">
          <div class="auth-card__intro">
            <h1 class="font-display">{{ title }}</h1>
            <p>{{ subtitle }}</p>
          </div>

          <slot />
        </div>

        <nav class="auth-layout__legal" aria-label="Informations légales">
          <RouterLink to="/cgu">CGU</RouterLink>
          <span aria-hidden="true">•</span>
          <RouterLink to="/confidentialite">Confidentialité</RouterLink>
          <span aria-hidden="true">•</span>
          <RouterLink to="/contact">Contact</RouterLink>
        </nav>
      </main>
    </div>
  </div>
</template>

<style scoped>
.auth-layout {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  background-color: #f8fafc;
}

.auth-layout__aside {
  display: none;
}

.auth-layout__panel {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
}

.auth-layout__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.875rem 1.25rem;
  background-color: var(--color-surface-raised);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 10;
}

.auth-layout__header-brand {
  display: inline-flex;
  align-items: center;
  gap: 0.625rem;
  text-decoration: none;
  color: var(--color-ink);
  font-size: 1.0625rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.auth-layout__header-link {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.625rem;
  text-decoration: none;
  color: var(--color-primary);
  font-size: 0.875rem;
  font-weight: 600;
  border: 1px solid transparent;
}

.auth-layout__header-link:hover {
  background-color: var(--color-accent-soft);
  border-color: #fbcfe8;
}

.auth-layout__main {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 1.25rem;
  padding: 1.5rem 1.25rem 2rem;
}

.auth-card {
  width: 100%;
  max-width: 28rem;
  background-color: var(--color-surface-raised);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 12px 32px -20px rgb(15 23 42 / 35%);
}

.auth-card__intro {
  margin-bottom: 1.5rem;
}

.auth-card__intro h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-ink);
  letter-spacing: -0.02em;
}

.auth-card__intro p {
  margin-top: 0.375rem;
  color: var(--color-muted);
  font-size: 0.9375rem;
  line-height: 1.5;
}

.auth-layout__legal {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.625rem;
  font-size: 0.8125rem;
  color: var(--color-muted);
}

.auth-layout__legal a {
  color: var(--color-muted);
  text-decoration: none;
  font-weight: 600;
}

.auth-layout__legal a:hover {
  color: var(--color-primary);
  text-decoration: underline;
}

@media (min-width: 640px) {
  .auth-card {
    padding: 2rem;
  }
}

@media (min-width: 1024px) {
  .auth-layout {
    display: grid;
    grid-template-columns: 5fr 6fr;
  }

  .auth-layout__aside {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 3rem;
    padding: 3rem;
    color: #ffffff;
    background: linear-gradient(160deg, #172554 0%, #1e1b4b 48%, #831843 100%);
  }

  .auth-layout__brand {
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    text-decoration: none;
    color: #ffffff;
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: -0.02em;
  }

  .auth-layout__pitch h2 {
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.2;
    letter-spacing: -0.03em;
  }

  .auth-layout__pitch p {
    margin-top: 1rem;
    max-width: 34ch;
    color: rgb(255 255 255 / 78%);
    line-height: 1.6;
  }

  .auth-layout__pitch ul {
    margin-top: 2rem;
    display: flex;
    flex-direction: column;
    gap: 0.875rem;
  }

  .auth-layout__pitch li {
    display: flex;
    align-items: flex-start;
    gap: 0.625rem;
    font-size: 0.9375rem;
    line-height: 1.45;
    color: rgb(255 255 255 / 88%);
  }

  .auth-layout__pitch li i {
    margin-top: 0.15rem;
    color: #f9a8d4;
  }

  .auth-layout__footnote {
    font-size: 0.8125rem;
    color: rgb(255 255 255 / 60%);
  }

  .auth-layout__header {
    display: none;
  }

  .auth-layout__main {
    padding: 3rem;
    gap: 1.75rem;
  }
}
</style>
