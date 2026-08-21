<script setup lang="ts">
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import { computed } from 'vue'

import DashboardShell from '@/layouts/DashboardShell.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const subscriptionLabel = computed(() =>
  auth.hasActiveSubscription ? 'Abonnement actif' : 'Sans abonnement',
)

const subscriptionEnd = computed(() => {
  if (!auth.user?.subscription_end_date) return null
  return new Date(auth.user.subscription_end_date).toLocaleDateString('fr-CI', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
})
</script>

<template>
  <DashboardShell>
    <header class="subscription__header">
      <h1 class="subscription__title font-display">Abonnement</h1>
      <p class="subscription__subtitle">
        Alliance Digitale VIP — 1 200 FCFA / mois.
      </p>
    </header>

    <Card>
      <template #content>
        <div class="subscription__status">
          <Tag
            :value="subscriptionLabel"
            :severity="auth.hasActiveSubscription ? 'success' : 'warn'"
          />
          <p v-if="subscriptionEnd">Valide jusqu’au {{ subscriptionEnd }}</p>
          <p v-else>
            Souscrivez depuis la page d’accueil pour activer l’Alliance Digitale VIP.
          </p>
        </div>
      </template>
    </Card>
  </DashboardShell>
</template>

<style scoped>
.subscription__header {
  margin-bottom: 1.25rem;
}

.subscription__title {
  margin: 0;
  font-size: 1.375rem;
  font-weight: 800;
  color: var(--color-ink);
}

.subscription__subtitle {
  margin: 0.375rem 0 0;
  color: var(--color-muted);
}

.subscription__status {
  display: grid;
  gap: 0.75rem;
}

.subscription__status p {
  margin: 0;
  color: var(--color-muted);
}
</style>
