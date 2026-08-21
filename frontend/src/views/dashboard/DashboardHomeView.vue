<script setup lang="ts">
import Card from 'primevue/card'
import Message from 'primevue/message'
import Tag from 'primevue/tag'
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import DashboardShell from '@/layouts/DashboardShell.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const showWelcome = computed(() => route.query.welcome === '1')

const stats = ref([
  { label: 'Relations déclarées', value: 0, icon: 'pi pi-heart', tone: 'rose' },
  { label: 'Recherches effectuées', value: 0, icon: 'pi pi-search', tone: 'sky' },
  { label: 'Alliances actives', value: 0, icon: 'pi pi-users', tone: 'violet' },
  { label: 'Tests de transparence', value: 0, icon: 'pi pi-shield', tone: 'teal' },
])

const activity = ref([
  { time: 'À l’instant', text: 'Espace prêt — vos services apparaîtront ici en temps réel.' },
  { time: 'Bientôt', text: 'Déclarations, alliances et recherches seront listées automatiquement.' },
])

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Bonjour'
  if (hour < 18) return 'Bon après-midi'
  return 'Bonsoir'
})

const displayName = computed(() => {
  if (!auth.user) return ''
  const full = `${auth.user.first_name} ${auth.user.last_name}`.trim()
  return full || 'Membre'
})

onMounted(() => {
  if (showWelcome.value) {
    router.replace({ path: '/app', query: {} })
  }
})
</script>

<template>
  <DashboardShell>
    <Message
      v-if="showWelcome"
      severity="info"
      :closable="false"
      class="dashboard-welcome"
    >
      <strong>Bienvenue sur AntiGoumin.</strong>
      Un email de confirmation vient d’être envoyé.
      Consultez aussi vos courriers indésirables (spam) si vous ne le voyez pas.
      Finalisez ensuite la vérification depuis
      <RouterLink to="/app/profil">Mon profil</RouterLink>.
    </Message>

    <header class="dashboard-home__header">
      <div>
        <p class="dashboard-home__eyebrow">{{ greeting }}</p>
        <h1 class="dashboard-home__title font-display">{{ displayName }}</h1>
        <p class="dashboard-home__subtitle">
          Vue d’ensemble de votre activité et accès rapide aux services.
        </p>
      </div>
      <Tag
        :value="auth.isFullyVerified ? 'Compte vérifié' : 'Vérification requise'"
        :severity="auth.isFullyVerified ? 'success' : 'warn'"
      />
    </header>

    <section class="dashboard-home__stats" aria-label="Statistiques">
      <Card v-for="stat in stats" :key="stat.label" class="dashboard-home__stat">
        <template #content>
          <div class="dashboard-home__stat-inner" :data-tone="stat.tone">
            <i :class="stat.icon" aria-hidden="true" />
            <div>
              <p class="dashboard-home__stat-value">{{ stat.value }}</p>
              <p class="dashboard-home__stat-label">{{ stat.label }}</p>
            </div>
          </div>
        </template>
      </Card>
    </section>

    <section class="dashboard-home__activity">
      <h2 class="dashboard-home__section-title font-display">Activité récente</h2>
      <Card>
        <template #content>
          <ul class="dashboard-home__timeline">
            <li v-for="item in activity" :key="item.time">
              <span class="dashboard-home__time">{{ item.time }}</span>
              <span>{{ item.text }}</span>
            </li>
          </ul>
        </template>
      </Card>
    </section>

    <section v-if="!auth.isFullyVerified" class="dashboard-home__cta">
      <Card>
        <template #content>
          <h2 class="dashboard-home__section-title font-display">Prochaine étape</h2>
          <p>
            Vérifiez votre email ou votre téléphone pour débloquer les déclarations,
            les recherches et les alliances.
          </p>
          <RouterLink to="/app/profil" class="dashboard-home__cta-link">
            Aller à Mon profil
            <i class="pi pi-arrow-right" aria-hidden="true" />
          </RouterLink>
        </template>
      </Card>
    </section>
  </DashboardShell>
</template>

<style scoped>
.dashboard-welcome {
  margin-bottom: 1rem;
}

.dashboard-welcome a {
  color: inherit;
  font-weight: 700;
}

.dashboard-home__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.dashboard-home__eyebrow {
  margin: 0;
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.dashboard-home__title {
  margin: 0.25rem 0 0;
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-weight: 800;
  color: var(--color-ink);
}

.dashboard-home__subtitle {
  margin: 0.5rem 0 0;
  color: var(--color-muted);
  font-size: 0.9375rem;
  max-width: 36rem;
}

.dashboard-home__stats {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.875rem;
  margin-bottom: 1.5rem;
}

@media (min-width: 640px) {
  .dashboard-home__stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .dashboard-home__stats {
    grid-template-columns: repeat(4, 1fr);
  }
}

.dashboard-home__stat-inner {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.dashboard-home__stat-inner i {
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
}

.dashboard-home__stat-inner[data-tone='rose'] i {
  background: #fff1f2;
  color: #e11d48;
}

.dashboard-home__stat-inner[data-tone='sky'] i {
  background: #eff6ff;
  color: #2563eb;
}

.dashboard-home__stat-inner[data-tone='violet'] i {
  background: #f5f3ff;
  color: #7c3aed;
}

.dashboard-home__stat-inner[data-tone='teal'] i {
  background: #ecfeff;
  color: #0d9488;
}

.dashboard-home__stat-value {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-ink);
}

.dashboard-home__stat-label {
  margin: 0.125rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-muted);
}

.dashboard-home__section-title {
  margin: 0 0 0.875rem;
  font-size: 1.125rem;
  font-weight: 800;
  color: var(--color-ink);
}

.dashboard-home__timeline {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.875rem;
}

.dashboard-home__timeline li {
  display: grid;
  gap: 0.25rem;
  padding-left: 0.875rem;
  border-left: 2px solid #e2e8f0;
}

.dashboard-home__time {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.dashboard-home__cta {
  margin-top: 1.5rem;
}

.dashboard-home__cta p {
  margin: 0 0 1rem;
  color: var(--color-muted);
}

.dashboard-home__cta-link {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  background: var(--color-primary);
  color: #fff;
  font-weight: 700;
  text-decoration: none;
}
</style>
