<script setup lang="ts">
import Button from 'primevue/button'
import Card from 'primevue/card'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import ToggleSwitch from 'primevue/toggleswitch'
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { redirectToGeniusPay } from '@/api/checkout'
import { ApiError } from '@/api/client'
import {
  decideAlliance,
  endAlliance,
  fetchAlliances,
  fetchEligibleDeclarations,
  setAllianceBadge,
  type Alliance,
  type EligibleDeclaration,
} from '@/api/alliances'
import {
  fetchNotifications,
  markNotificationRead,
  type InAppNotification,
} from '@/api/notifications'
import DashboardShell from '@/layouts/DashboardShell.vue'
import PremiumVisibilityControl from '@/components/PremiumVisibilityControl.vue'
import { alliancesPageCopy } from '@/content/alliancesCopy'
import { useAuthStore } from '@/stores/auth'
import { downloadAlliancePdf } from '@/utils/moduleReceipts'

const auth = useAuthStore()
const router = useRouter()

const alliances = ref<Alliance[]>([])
const eligibleDeclarations = ref<EligibleDeclaration[]>([])
const loadingList = ref(true)
const paying = ref(false)
const decidingId = ref<number | null>(null)
const endingId = ref<number | null>(null)
const updatingBadgeId = ref<number | null>(null)
const downloadingPdfId = ref<number | null>(null)
const error = ref('')
const success = ref('')
const selectedDeclarationId = ref<number | null>(null)
const notifications = ref<InAppNotification[]>([])
const loadingAlerts = ref(true)
const dismissingAlertId = ref<number | null>(null)

const allianceAlertTypes = new Set([
  'PARTNER_DECLARED_BY_OTHER',
  'PARTNER_VISIBILITY_DISABLED',
  'SUBSCRIPTION_EXPIRING',
  'SUBSCRIPTION_EXPIRED',
  'SUBSCRIPTION_RENEWED',
])

const allianceAlerts = computed(() =>
  notifications.value.filter((notification) => allianceAlertTypes.has(notification.type)),
)

const unreadAllianceAlerts = computed(() =>
  allianceAlerts.value.filter((notification) => !notification.read_at),
)

const userId = computed(() => auth.user?.id ?? 0)

const hasBlockingAlliance = computed(() =>
  alliances.value.some(
    (alliance) => alliance.status === 'ACTIVE' || alliance.status === 'PENDING_PARTNER',
  ),
)

const pendingInvitations = computed(() =>
  alliances.value.filter(
    (alliance) => alliance.status === 'PENDING_PARTNER' && alliance.partner_id === userId.value,
  ),
)

const sentInvitations = computed(() =>
  alliances.value.filter(
    (alliance) => alliance.status === 'PENDING_PARTNER' && alliance.initiator_id === userId.value,
  ),
)

const activeAlliances = computed(() =>
  alliances.value.filter((alliance) => alliance.status === 'ACTIVE'),
)

const historyAlliances = computed(() =>
  alliances.value.filter(
    (alliance) => alliance.status === 'ENDED' || alliance.status === 'REFUSED',
  ),
)

const declarationOptions = computed(() =>
  eligibleDeclarations.value.map((item) => ({
    label: `${item.partner_label} (${item.relation_type})`,
    value: item.id,
  })),
)

const statusMeta: Record<
  Alliance['status'],
  { label: string; severity: 'success' | 'warn' | 'danger' | 'secondary' | 'info' }
> = {
  PENDING_PARTNER: { label: 'En attente du partenaire', severity: 'warn' },
  ACTIVE: { label: 'Alliance active', severity: 'success' },
  REFUSED: { label: 'Refusée', severity: 'secondary' },
  ENDED: { label: 'Terminée', severity: 'secondary' },
}

function partnerName(alliance: Alliance): string {
  return alliance.initiator_id === userId.value
    ? alliance.partner_name
    : alliance.initiator_name
}

function myBadgePublic(alliance: Alliance): boolean {
  return alliance.initiator_id === userId.value
    ? alliance.initiator_badge_public
    : alliance.partner_badge_public
}

async function exportAlliancePdf(item: Alliance) {
  downloadingPdfId.value = item.id
  try {
    await downloadAlliancePdf(item, partnerName(item))
  } finally {
    downloadingPdfId.value = null
  }
}

async function loadAlerts() {
  loadingAlerts.value = true
  try {
    notifications.value = await fetchNotifications()
  } catch {
    notifications.value = []
  } finally {
    loadingAlerts.value = false
  }
}

async function dismissAlert(notificationId: number) {
  dismissingAlertId.value = notificationId
  try {
    const result = await markNotificationRead(notificationId)
    notifications.value = notifications.value.map((notification) =>
      notification.id === notificationId
        ? { ...notification, read_at: result.read_at }
        : notification,
    )
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Action impossible.'
  } finally {
    dismissingAlertId.value = null
  }
}

async function loadAlliancesData() {
  loadingList.value = true
  try {
    const [allianceList, eligible] = await Promise.all([
      fetchAlliances(),
      fetchEligibleDeclarations(),
    ])
    alliances.value = allianceList
    eligibleDeclarations.value = eligible
    if (!selectedDeclarationId.value && eligible.length === 1) {
      selectedDeclarationId.value = eligible[0]?.id ?? null
    }
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Chargement impossible.'
  } finally {
    loadingList.value = false
  }
}

async function payAlliance() {
  if (!selectedDeclarationId.value) {
    error.value = 'Sélectionnez une relation certifiée.'
    return
  }
  paying.value = true
  error.value = ''
  try {
    await redirectToGeniusPay({
      service_type: 'ALLIANCE_VIP',
      declaration_id: selectedDeclarationId.value,
    })
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Paiement impossible.'
    paying.value = false
  }
}

async function respondInvitation(alliance: Alliance, accept: boolean) {
  decidingId.value = alliance.id
  error.value = ''
  success.value = ''
  try {
    const result = await decideAlliance(alliance.id, accept)
    success.value = result.message
    await auth.fetchMe()
    await loadAlliancesData()
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Réponse impossible.'
  } finally {
    decidingId.value = null
  }
}

async function toggleBadge(alliance: Alliance, visible: boolean) {
  if (!auth.hasActiveSubscription) {
    await router.push('/app/abonnement')
    return
  }
  updatingBadgeId.value = alliance.id
  error.value = ''
  try {
    await setAllianceBadge(alliance.id, visible)
    success.value = visible
      ? 'Votre badge Alliance est visible publiquement.'
      : 'Votre badge Alliance est masqué.'
    await loadAlliancesData()
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Modification impossible.'
  } finally {
    updatingBadgeId.value = null
  }
}

async function terminateAlliance(alliance: Alliance) {
  if (
    !window.confirm(
      'Mettre fin à cette Alliance Digitale ? Votre partenaire sera informé de façon neutre, sans motif ni détail.',
    )
  ) {
    return
  }
  endingId.value = alliance.id
  error.value = ''
  try {
    const result = await endAlliance(alliance.id)
    success.value = result.message
    await auth.fetchMe()
    await loadAlliancesData()
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Action impossible.'
  } finally {
    endingId.value = null
  }
}

onMounted(async () => {
  await Promise.all([loadAlliancesData(), loadAlerts()])
})
function onBadgeLockedClick() {
  router.push('/app/abonnement')
}
</script>

<template>
  <DashboardShell>
    <header class="alliances-hero">
      <div class="alliances-hero__glow" aria-hidden="true" />
      <div class="alliances-hero__content">
        <div class="alliances-hero__icon" aria-hidden="true">💍</div>
        <div class="alliances-hero__text">
          <p class="alliances-hero__eyebrow">{{ alliancesPageCopy.eyebrow }}</p>
          <h1 class="alliances-hero__title font-display">{{ alliancesPageCopy.title }}</h1>
          <p class="alliances-hero__subtitle">{{ alliancesPageCopy.subtitle }}</p>
        </div>
        <Tag :value="alliancesPageCopy.priceTag" severity="warn" class="alliances-hero__tag" />
      </div>
    </header>

    <Message v-if="!auth.isFullyVerified" severity="warn" :closable="false" class="mb-3">
      Vérifiez votre email ou votre téléphone depuis
      <RouterLink to="/app/profil">Mon profil</RouterLink>
      avant de créer une Alliance.
    </Message>

    <Message v-if="error" severity="error" :closable="false" class="mb-3">{{ error }}</Message>
    <Message v-if="success" severity="success" :closable="false" class="mb-3">
      {{ success }}
    </Message>

    <section class="alliances-page__section">
      <div class="alliances-page__alerts-head">
        <h2 class="alliances-page__section-title font-display">{{ alliancesPageCopy.alertsTitle }}</h2>
        <Tag
          v-if="unreadAllianceAlerts.length"
          :value="`${unreadAllianceAlerts.length} non lue(s)`"
          severity="warn"
        />
      </div>
      <p v-if="loadingAlerts">Chargement des alertes…</p>
      <p v-else-if="!allianceAlerts.length" class="alliances-page__empty">
        {{ alliancesPageCopy.alertsEmpty }}
      </p>
      <div v-else class="alliances-page__cards">
        <Card v-for="item in allianceAlerts" :key="item.id" class="alliances-card alliances-card--alert">
          <template #content>
            <div class="alliances-page__alert-head">
              <div>
                <h3>{{ item.title }}</h3>
                <Tag
                  :value="item.read_at ? 'Lue' : 'Nouvelle'"
                  :severity="item.read_at ? 'secondary' : 'warn'"
                />
              </div>
            </div>
            <p class="alliances-page__meta">{{ item.message }}</p>
            <p class="alliances-page__meta">
              {{ new Date(item.created_at).toLocaleString('fr-CI') }}
            </p>
            <Button
              v-if="!item.read_at"
              label="Marquer comme lue"
              severity="secondary"
              text
              size="small"
              :loading="dismissingAlertId === item.id"
              @click="dismissAlert(item.id)"
            />
          </template>
        </Card>
      </div>
    </section>

    <section v-if="pendingInvitations.length" class="alliances-page__section">
      <h2 class="alliances-page__section-title font-display">Invitations reçues</h2>
      <div class="alliances-page__cards">
        <Card v-for="item in pendingInvitations" :key="item.id" class="alliances-card alliances-card--invite">
          <template #content>
            <p>
              <strong>{{ item.initiator_name }}</strong> vous invite à sceller une Alliance
              Digitale.
            </p>
            <p class="alliances-page__meta">
              Aucun badge n'est publié tant que vous n'avez pas accepté.
            </p>
            <div class="alliances-page__actions">
              <Button
                label="Accepter l'Alliance"
                icon="pi pi-check"
                :loading="decidingId === item.id"
                @click="respondInvitation(item, true)"
              />
              <Button
                label="Refuser"
                severity="secondary"
                outlined
                :disabled="decidingId === item.id"
                @click="respondInvitation(item, false)"
              />
            </div>
          </template>
        </Card>
      </div>
    </section>

    <section v-if="sentInvitations.length" class="alliances-page__section">
      <h2 class="alliances-page__section-title font-display">Invitations envoyées</h2>
      <div class="alliances-page__cards">
        <Card v-for="item in sentInvitations" :key="item.id" class="alliances-card">
          <template #content>
            <h3>{{ partnerName(item) }}</h3>
            <Tag value="En attente du consentement" severity="warn" />
            <p class="alliances-page__meta">
              Votre partenaire doit accepter pour activer l'Alliance. Aucun badge n'est publié
              avant son consentement.
            </p>
          </template>
        </Card>
      </div>
    </section>

    <section
      v-if="auth.isFullyVerified && !hasBlockingAlliance && eligibleDeclarations.length"
      class="alliances-page__section"
    >
      <Card class="alliances-card alliances-card--pay">
        <template #content>
          <div class="alliances-card__head">
            <span class="alliances-card__emoji" aria-hidden="true">✨</span>
            <div>
              <h2 class="alliances-card__title font-display">{{ alliancesPageCopy.payTitle }}</h2>
              <p class="alliances-card__body">{{ alliancesPageCopy.payBody }}</p>
            </div>
          </div>
          <form class="alliances-page__form" @submit.prevent="payAlliance">
            <label class="alliances-page__field">
              <span>{{ alliancesPageCopy.relationLabel }}</span>
              <Select
                v-model="selectedDeclarationId"
                :options="declarationOptions"
                option-label="label"
                option-value="value"
                placeholder="Sélectionner une relation"
                class="w-full"
              />
            </label>
            <Button
              type="submit"
              :label="alliancesPageCopy.payCta"
              icon="pi pi-star-fill"
              :loading="paying"
              class="alliances-card__cta"
            />
          </form>
        </template>
      </Card>
    </section>

    <section
      v-else-if="auth.isFullyVerified && !hasBlockingAlliance && !loadingList"
      class="alliances-page__section"
    >
      <Message severity="info" :closable="false">
        Aucune relation certifiée disponible.
        <RouterLink to="/app/declarations">Déclarez votre relation amoureuse</RouterLink>
        avant de créer une Alliance.
      </Message>
    </section>

    <section class="alliances-page__section">
      <h2 class="alliances-page__section-title font-display">{{ alliancesPageCopy.visibilityTitle }}</h2>
      <PremiumVisibilityControl />
    </section>

    <section v-if="activeAlliances.length" class="alliances-page__section">
      <h2 class="alliances-page__section-title font-display">{{ alliancesPageCopy.activeTitle }}</h2>
      <div class="alliances-page__cards">
        <Card v-for="item in activeAlliances" :key="item.id" class="alliances-card alliances-card--active">
          <template #content>
            <div class="alliances-page__card-head">
              <div>
                <h3>{{ partnerName(item) }}</h3>
                <Tag
                  :value="statusMeta[item.status].label"
                  :severity="statusMeta[item.status].severity"
                />
              </div>
              <Button
                icon="pi pi-download"
                severity="secondary"
                text
                rounded
                aria-label="Télécharger en PDF"
                :loading="downloadingPdfId === item.id"
                @click="exportAlliancePdf(item)"
              />
            </div>
            <p v-if="item.subscription_end_date" class="alliances-page__meta">
              Abonnement actif jusqu'au
              {{ new Date(item.subscription_end_date).toLocaleDateString('fr-CI') }}
            </p>
            <div
              class="alliances-page__badge-row"
              :class="{ 'alliances-page__badge-row--locked': !auth.hasActiveSubscription }"
              @click.capture="!auth.hasActiveSubscription ? onBadgeLockedClick() : undefined"
            >
              <label :for="`badge-${item.id}`">{{ alliancesPageCopy.badgeLabel }}</label>
              <ToggleSwitch
                :id="`badge-${item.id}`"
                :model-value="myBadgePublic(item)"
                :disabled="updatingBadgeId === item.id || !auth.hasActiveSubscription"
                @update:model-value="toggleBadge(item, $event)"
              />
            </div>
            <p class="alliances-page__meta">
              {{ auth.hasActiveSubscription ? alliancesPageCopy.badgeHint : 'Réservé au service Premium — touchez pour vous abonner.' }}
            </p>
            <Button
              label="Mettre fin à l'Alliance"
              severity="secondary"
              text
              size="small"
              :loading="endingId === item.id"
              @click="terminateAlliance(item)"
            />
          </template>
        </Card>
      </div>
    </section>

    <section class="alliances-page__section">
      <h2 class="alliances-page__section-title font-display">{{ alliancesPageCopy.historyTitle }}</h2>
      <p v-if="loadingList">Chargement…</p>
      <p v-else-if="!alliances.length" class="alliances-page__empty">
        {{ alliancesPageCopy.historyEmpty }}
      </p>
      <div v-else class="alliances-page__cards">
        <Card v-for="item in historyAlliances" :key="item.id" class="alliances-card">
          <template #content>
            <div class="alliances-page__card-head">
              <div>
                <h3>{{ partnerName(item) }}</h3>
                <Tag
                  :value="statusMeta[item.status]?.label ?? item.status"
                  :severity="statusMeta[item.status]?.severity ?? 'secondary'"
                />
              </div>
              <Button
                icon="pi pi-download"
                severity="secondary"
                text
                rounded
                aria-label="Télécharger en PDF"
                :loading="downloadingPdfId === item.id"
                @click="exportAlliancePdf(item)"
              />
            </div>
            <p class="alliances-page__meta">
              {{ new Date(item.created_at).toLocaleDateString('fr-CI') }}
            </p>
          </template>
        </Card>
        <p
          v-if="alliances.length && !historyAlliances.length && !activeAlliances.length && !pendingInvitations.length"
          class="alliances-page__empty"
        >
          Vos invitations en cours apparaîtront ici une fois traitées.
        </p>
      </div>
    </section>
  </DashboardShell>
</template>

<style scoped>
.alliances-hero {
  position: relative;
  margin-bottom: 1.25rem;
  border-radius: 1.25rem;
  overflow: hidden;
  background: linear-gradient(135deg, #fffbeb 0%, #ffffff 45%, #fef3c7 100%);
  border: 1px solid rgb(251 191 36 / 0.22);
}

.alliances-hero__glow {
  position: absolute;
  top: -3rem;
  right: -2rem;
  width: 10rem;
  height: 10rem;
  border-radius: 50%;
  background: radial-gradient(circle, rgb(251 191 36 / 0.2) 0%, transparent 70%);
  pointer-events: none;
}

.alliances-hero__content {
  position: relative;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem 1.375rem;
}

.alliances-hero__icon {
  font-size: 2rem;
  line-height: 1;
  filter: drop-shadow(0 4px 8px rgb(251 191 36 / 0.25));
}

.alliances-hero__text {
  flex: 1 1 14rem;
  min-width: 0;
}

.alliances-hero__eyebrow {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #b45309;
}

.alliances-hero__title {
  margin: 0.25rem 0 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-ink);
}

.alliances-hero__subtitle {
  margin: 0.5rem 0 0;
  color: var(--color-muted);
  line-height: 1.6;
  max-width: 40rem;
}

.alliances-hero__tag :deep(.p-tag) {
  background: rgb(251 191 36 / 0.18);
  color: #92400e;
}

.alliances-card :deep(.p-card-body) {
  padding: 0;
}

.alliances-card :deep(.p-card-content) {
  padding: 1.25rem;
}

.alliances-card--pay,
.alliances-card--active,
.alliances-card--invite,
.alliances-card--alert {
  border: 1px solid rgb(251 191 36 / 0.18);
  box-shadow: 0 8px 24px rgb(251 191 36 / 0.07);
}

.alliances-card--active {
  background: linear-gradient(180deg, #fffbeb 0%, #ffffff 100%);
}

.alliances-card__head {
  display: flex;
  gap: 0.875rem;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.alliances-card__emoji {
  font-size: 1.75rem;
  line-height: 1;
}

.alliances-card__title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 800;
  color: var(--color-ink);
}

.alliances-card__body {
  margin: 0.375rem 0 0;
  color: var(--color-muted);
  line-height: 1.55;
}

.alliances-card__cta :deep(.p-button) {
  width: 100%;
  justify-content: center;
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  border-color: #d97706;
  color: #78350f;
  font-weight: 800;
}

.alliances-page__alerts-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.alliances-page__alerts-head .alliances-page__section-title {
  margin-bottom: 0;
}

.alliances-page__alert-head h3 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 800;
  color: var(--color-ink);
}

.alliances-page__section {
  margin-bottom: 1.5rem;
}

.alliances-page__section-title {
  margin: 0 0 0.75rem;
  font-size: 1.125rem;
  font-weight: 800;
  color: var(--color-ink);
}

.alliances-page__meta,
.alliances-page__empty {
  color: var(--color-muted);
  line-height: 1.55;
}

.alliances-page__form {
  display: grid;
  gap: 1rem;
}

.alliances-page__field {
  display: grid;
  gap: 0.375rem;
}

.alliances-page__field span {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-ink);
}

.alliances-page__submit :deep(.p-button) {
  width: 100%;
  justify-content: center;
}

.alliances-page__badge-row--locked {
  opacity: 0.45;
  cursor: pointer;
}

.alliances-page__cards {
  display: grid;
  gap: 0.875rem;
}

.alliances-page__card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.alliances-page__card-head h3 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 800;
  color: var(--color-ink);
}

.alliances-page__actions {
  display: grid;
  gap: 0.625rem;
  margin-top: 1rem;
}

.alliances-page__badge-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin: 1rem 0 0.5rem;
}

.alliances-page__badge-row label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-ink);
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.w-full {
  width: 100%;
}
</style>
