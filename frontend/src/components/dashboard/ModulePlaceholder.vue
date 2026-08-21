<script setup lang="ts">
import { RouterLink } from 'vue-router'

import Card from 'primevue/card'

defineProps<{
  title: string
  description: string
  icon: string
}>()
</script>

<template>
  <section class="module-placeholder">
    <header class="module-placeholder__header">
      <div class="module-placeholder__icon" aria-hidden="true">
        <i :class="icon" />
      </div>
      <div>
        <h1 class="module-placeholder__title font-display">{{ title }}</h1>
        <p class="module-placeholder__description">{{ description }}</p>
      </div>
    </header>

    <Card>
      <template #content>
        <p class="module-placeholder__body">
          Ce module sera bientôt connecté à vos services AntiGoumin.
          En attendant, finalisez la vérification de votre compte depuis
          <RouterLink to="/app/profil">Mon profil</RouterLink>.
        </p>
      </template>
    </Card>
  </section>
</template>

<style scoped>
.module-placeholder__header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.module-placeholder__icon {
  width: 3rem;
  height: 3rem;
  border-radius: 1rem;
  background: var(--color-accent-soft);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.module-placeholder__title {
  margin: 0;
  font-size: 1.375rem;
  font-weight: 800;
  color: var(--color-ink);
}

.module-placeholder__description {
  margin: 0.375rem 0 0;
  color: var(--color-muted);
  font-size: 0.9375rem;
}

.module-placeholder__body {
  margin: 0;
  color: var(--color-muted);
  line-height: 1.6;
}

.module-placeholder__body a {
  color: var(--color-primary);
  font-weight: 700;
  text-decoration: none;
}
</style>
