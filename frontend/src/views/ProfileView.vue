<script setup lang="ts">
import Button from 'primevue/button'
import Card from 'primevue/card'
import Divider from 'primevue/divider'
import Message from 'primevue/message'
import Tag from 'primevue/tag'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fetchAlliances, type Alliance } from '@/api/alliances'
import {
  fetchUnreadNotifications,
  markNotificationRead,
  type InAppNotification,
} from '@/api/notifications'
import VerificationBanner from '@/components/VerificationBanner.vue'
import PremiumVisibilityControl from '@/components/PremiumVisibilityControl.vue'
import DashboardShell from '@/layouts/DashboardShell.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const alliances = ref<Alliance[]>([])
const notifications = ref<InAppNotification[]>([])

const displayName = computed(() => {
  if (!auth.user) return ''
  const full = `${auth.user.first_name} ${auth.user.last_name}`.trim()
  return full || auth.user.email
})

const authProviderLabel = computed(() => {
  const map: Record<string, string> = {
    email: 'Email et mot de passe',
    google: 'Google',
    apple: 'Apple',
  }
  return map[auth.user?.auth_provider ?? 'email'] ?? auth.user?.auth_provider
})

const subscriptionLabel = computed(() =>
  auth.hasActiveSubscription ? 'Abonnement actif' : 'Sans abonnement',
)

const subscriptionSeverity = computed(() =>
  auth.hasActiveSubscription ? 'success' : 'warn',
)

const subscriptionEnd = computed(() => {
  if (!auth.user?.subscription_end_date) return null
  return new Date(auth.user.subscription_end_date).toLocaleDateString('fr-CI', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
})

const activeAlliance = computed(() =>
  alliances.value.find((alliance) => alliance.status === 'ACTIVE'),
)

const alliancePartner = computed(() => {
  const alliance = activeAlliance.value
  const user = auth.user
  if (!alliance || !user) return null
  const userIsInitiator = alliance.initiator_id === user.id
  return {
    name: userIsInitiator ? alliance.partner_name : alliance.initiator_name,
    isVisible: userIsInitiator
      ? alliance.partner_is_status_searchable
      : alliance.initiator_is_status_searchable,
  }
})

function logout() {
  auth.logout()
  router.push('/')
}

async function dismissNotification(notificationId: number) {
  await markNotificationRead(notificationId)
  notifications.value = notifications.value.filter(
    (notification) => notification.id !== notificationId,
  )
}

onMounted(async () => {
  try {
    notifications.value = await fetchUnreadNotifications()
    if (auth.isFullyVerified) {
      alliances.value = await fetchAlliances()
    }
  } catch {
    // Le profil reste utilisable si ces informations secondaires sont indisponibles.
  }
})
</script>

<template>
  <DashboardShell>
    <VerificationBanner />
    <Card v-if="auth.user">
      <template #title>
        <h1 class="page-title font-display">Mon profil</h1>
      </template>
      <template #subtitle>
        <p class="page-subtitle">Gérez votre compte AntiGoumin.</p>
      </template>
      <template #content>
        <div v-if="notifications.length" class="profile-notifications">
          <Message
            v-for="notification in notifications"
            :key="notification.id"
            severity="warn"
            :closable="false"
          >
            <div>
              <strong>{{ notification.title }}</strong>
              <p>{{ notification.message }}</p>
              <Button
                label="Marquer comme lue"
                severity="secondary"
                text
                size="small"
                @click="dismissNotification(notification.id)"
              />
            </div>
          </Message>
        </div>

        <div class="profile-header">
          <div class="profile-avatar" aria-hidden="true">
            <i class="pi pi-user" />
          </div>
          <div>
            <h2 class="profile-name">{{ displayName }}</h2>
            <p class="profile-email">{{ auth.user.email }}</p>
          </div>
        </div>

        <Divider />

        <dl class="profile-details">
          <div class="profile-detail">
            <dt><i class="pi pi-shield" aria-hidden="true" /> Connexion</dt>
            <dd>{{ authProviderLabel }}</dd>
          </div>
          <div class="profile-detail">
            <dt><i class="pi pi-heart" aria-hidden="true" /> Abonnement</dt>
            <dd class="profile-detail__value">
              <Tag :value="subscriptionLabel" :severity="subscriptionSeverity" />
              <span v-if="subscriptionEnd" class="profile-detail__meta">
                Jusqu'au {{ subscriptionEnd }}
              </span>
              <span v-else class="profile-detail__meta">
                1 200 FCFA / mois — Alliance Digitale VIP
              </span>
            </dd>
          </div>
          <div class="profile-detail profile-detail--full">
            <dt><i class="pi pi-eye" aria-hidden="true" /> Visibilité du statut</dt>
            <dd>
              <PremiumVisibilityControl compact />
            </dd>
          </div>
          <div v-if="alliancePartner" class="profile-detail">
            <dt><i class="pi pi-users" aria-hidden="true" /> Partenaire d’Alliance</dt>
            <dd class="profile-detail__value">
              <span>{{ alliancePartner.name }}</span>
              <Tag
                :value="alliancePartner.isVisible ? 'Visible' : 'Non visible'"
                :severity="alliancePartner.isVisible ? 'success' : 'warn'"
                :icon="alliancePartner.isVisible ? 'pi pi-check' : 'pi pi-eye-slash'"
              />
            </dd>
          </div>
        </dl>

        <Divider />

        <div class="profile-actions">
          <Button
            label="Se déconnecter"
            icon="pi pi-sign-out"
            severity="secondary"
            outlined
            class="w-full"
            @click="logout"
          />
        </div>
      </template>
    </Card>
  </DashboardShell>
</template>

<style scoped>
.page-title {
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--color-ink);
}

.page-subtitle {
  color: var(--color-muted);
  font-size: 0.9375rem;
}

.profile-notifications {
  display: grid;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.profile-notifications p {
  margin-top: 0.25rem;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.profile-avatar {
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 50%;
  background-color: #ecfeff;
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.profile-name {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-ink);
}

.profile-email {
  font-size: 0.875rem;
  color: var(--color-muted);
  margin-top: 0.125rem;
}

.profile-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.profile-detail dt {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin-bottom: 0.375rem;
}

.profile-detail dd {
  font-size: 0.9375rem;
  color: var(--color-ink);
}

.profile-detail--full dd {
  margin-inline-start: 0;
}

.profile-detail__value {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  align-items: flex-start;
}

.profile-detail__meta {
  font-size: 0.8125rem;
  color: var(--color-muted);
}

.profile-actions {
  margin-top: 0.5rem;
}

.w-full :deep(.p-button) {
  width: 100%;
  justify-content: center;
}
</style>
