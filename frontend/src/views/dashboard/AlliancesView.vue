<script setup lang="ts">
import Button from 'primevue/button'
import Card from 'primevue/card'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import ToggleSwitch from 'primevue/toggleswitch'
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

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
import { useAuthStore } from '@/stores/auth'
import { downloadAlliancePdf } from '@/utils/moduleReceipts'

const auth = useAuthStore()

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
</script>

<template>
  <DashboardShell>
    <header class="alliances-page__header">
      <div>
        <p class="alliances-page__eyebrow">Confiance mutuelle</p>
        <h1 class="alliances-page__title font-display">Mes alliances digitales</h1>
        <p class="alliances-page__subtitle">
          Scellez une Alliance VIP après une relation certifiée. L'activation requiert le
          consentement des deux parties ; le badge public reste optionnel pour chacun.
        </p>
      </div>
      <Tag value="1200 FCFA / mois" severity="info" />
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
        <h2 class="alliances-page__section-title font-display">Alertes Alliance VIP</h2>
        <Tag
          v-if="unreadAllianceAlerts.length"
          :value="`${unreadAllianceAlerts.length} non lue(s)`"
          severity="warn"
        />
      </div>
      <p v-if="loadingAlerts">Chargement des alertes…</p>
      <p v-else-if="!allianceAlerts.length" class="alliances-page__empty">
        Aucune alerte pour le moment. Vous serez informé si votre partenaire est déclaré
        par une autre personne sur la plateforme, sans révéler l'identité du déclarant.
      </p>
      <div v-else class="alliances-page__cards">
        <Card v-for="item in allianceAlerts" :key="item.id">
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
        <Card v-for="item in pendingInvitations" :key="item.id">
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
        <Card v-for="item in sentInvitations" :key="item.id">
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
      <Card>
        <template #content>
          <h2 class="alliances-page__section-title font-display">Nouvelle Alliance VIP</h2>
          <p class="alliances-page__meta">
            Choisissez une relation mutuellement validée, puis payez l'abonnement mensuel.
            Votre partenaire devra accepter pour activer l'Alliance.
          </p>
          <form class="alliances-page__form" @submit.prevent="payAlliance">
            <label class="alliances-page__field">
              <span>Relation certifiée</span>
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
              label="Payer 1200 FCFA et inviter mon partenaire"
              icon="pi pi-credit-card"
              :loading="paying"
              class="alliances-page__submit"
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
        <RouterLink to="/app/declarations">Déclarez et faites certifier une relation</RouterLink>
        avant de créer une Alliance.
      </Message>
    </section>

    <section v-if="activeAlliances.length" class="alliances-page__section">
      <h2 class="alliances-page__section-title font-display">Alliance active</h2>
      <div class="alliances-page__cards">
        <Card v-for="item in activeAlliances" :key="item.id">
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
            <div class="alliances-page__badge-row">
              <label :for="`badge-${item.id}`">Afficher mon badge Alliance</label>
              <ToggleSwitch
                :id="`badge-${item.id}`"
                :model-value="myBadgePublic(item)"
                :disabled="updatingBadgeId === item.id"
                @update:model-value="toggleBadge(item, $event)"
              />
            </div>
            <p class="alliances-page__meta">
              Le badge est optionnel et indépendant pour chaque partie.
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
      <h2 class="alliances-page__section-title font-display">Historique</h2>
      <p v-if="loadingList">Chargement…</p>
      <p v-else-if="!alliances.length" class="alliances-page__empty">
        Aucune Alliance pour le moment.
      </p>
      <div v-else class="alliances-page__cards">
        <Card v-for="item in historyAlliances" :key="item.id">
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
.alliances-page__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.alliances-page__eyebrow {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.alliances-page__title {
  margin: 0.25rem 0 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-ink);
}

.alliances-page__subtitle {
  margin: 0.5rem 0 0;
  color: var(--color-muted);
  line-height: 1.55;
  max-width: 40rem;
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
