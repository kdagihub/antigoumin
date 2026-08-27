<script setup lang="ts">
import Button from 'primevue/button'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Tag from 'primevue/tag'
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { redirectToGeniusPay } from '@/api/checkout'
import { ApiError } from '@/api/client'
import { fetchCheckoutStatus, fetchUnusedPayment } from '@/api/payments'
import {
  createTransparencyRequest,
  fetchTransparencyRequests,
  type TransparencyRequest,
} from '@/api/transparency'
import DashboardShell from '@/layouts/DashboardShell.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const requests = ref<TransparencyRequest[]>([])
const loadingList = ref(true)
const paymentId = ref<number | null>(null)
const paying = ref(false)
const submitting = ref(false)
const error = ref('')
const success = ref('')
const targetPhone = ref('')

const canCreate = computed(() => Boolean(paymentId.value) || import.meta.env.DEV)
const showForm = computed(() => canCreate.value && auth.isFullyVerified)

const statusMeta: Record<
  TransparencyRequest['status'],
  { label: string; severity: 'success' | 'warn' | 'danger' | 'secondary' | 'info' }
> = {
  PENDING: { label: 'En attente de réponse', severity: 'warn' },
  ACCEPTED: { label: 'Réponse reçue', severity: 'success' },
  REFUSED: { label: 'Refusée', severity: 'secondary' },
  EXPIRED: { label: 'Expirée', severity: 'secondary' },
  BLOCKED: { label: 'Bloquée', severity: 'danger' },
  REPORTED: { label: 'Signalée', severity: 'danger' },
}

const declaredStatusLabels: Record<string, string> = {
  ENGAGED: 'En couple',
  AVAILABLE: 'Disponible',
  PREFER_NOT_TO_ANSWER: 'Préfère ne pas répondre',
}

async function loadRequests() {
  loadingList.value = true
  try {
    const result = await fetchTransparencyRequests()
    requests.value = result.items
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Chargement impossible.'
  } finally {
    loadingList.value = false
  }
}

async function resolvePayment() {
  const reference = typeof route.query.reference === 'string' ? route.query.reference : ''
  if (reference) {
    try {
      const status = await fetchCheckoutStatus(reference)
      if (status.payment_id) {
        paymentId.value = status.payment_id
        success.value = 'Paiement confirmé. Envoyez votre demande ci-dessous.'
      }
    } catch {
      // Le formulaire reste bloqué sans paiement valide.
    }
    await router.replace({ path: '/app/transparence' })
    return
  }
  try {
    const unused = await fetchUnusedPayment('TRANSPARENCY_REQUEST')
    paymentId.value = unused.payment_id
  } catch {
    paymentId.value = null
  }
}

async function payTransparency() {
  paying.value = true
  error.value = ''
  try {
    await redirectToGeniusPay({ service_type: 'TRANSPARENCY_REQUEST' })
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Paiement impossible.'
    paying.value = false
  }
}

async function submitRequest() {
  error.value = ''
  success.value = ''
  if (!paymentId.value && !import.meta.env.DEV) {
    error.value = 'Paiement requis avant envoi.'
    return
  }
  submitting.value = true
  try {
    await createTransparencyRequest({
      target_phone: targetPhone.value.trim(),
      payment_id: paymentId.value ?? undefined,
    })
    success.value =
      'Demande envoyée. La personne recevra un SMS identifiable avec un lien de réponse volontaire.'
    targetPhone.value = ''
    paymentId.value = null
    await loadRequests()
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Envoi impossible.'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadRequests(), resolvePayment()])
})
</script>

<template>
  <DashboardShell>
    <header class="transparency-page__header">
      <div>
        <p class="transparency-page__eyebrow">Clarification volontaire</p>
        <h1 class="transparency-page__title font-display">Tests de transparence</h1>
        <p class="transparency-page__subtitle">
          Envoyez une demande identifiable à un numéro. La personne choisit librement de
          répondre, refuser ou ignorer — son silence ne constitue aucune preuve.
        </p>
      </div>
      <Tag value="550 FCFA / demande" severity="info" />
    </header>

    <Message v-if="!auth.isFullyVerified" severity="warn" :closable="false" class="mb-3">
      Vérifiez votre email ou votre téléphone depuis
      <RouterLink to="/app/profil">Mon profil</RouterLink>
      avant d'envoyer une demande.
    </Message>

    <Message v-if="error" severity="error" :closable="false" class="mb-3">{{ error }}</Message>
    <Message v-if="success" severity="success" :closable="false" class="mb-3">
      {{ success }}
    </Message>

    <section v-if="!canCreate && auth.isFullyVerified" class="transparency-page__pay">
      <Card>
        <template #content>
          <h2 class="transparency-page__section-title font-display">Nouvelle demande</h2>
          <p>
            Payez 550 FCFA pour envoyer une invitation identifiable par SMS. Votre nom sera
            visible par le destinataire.
          </p>
          <Button
            label="Payer 550 FCFA"
            icon="pi pi-credit-card"
            :loading="paying"
            @click="payTransparency"
          />
        </template>
      </Card>
    </section>

    <section v-if="showForm" class="transparency-page__form-section">
      <Card>
        <template #content>
          <h2 class="transparency-page__section-title font-display">Nouvelle demande</h2>
          <p v-if="paymentId" class="transparency-page__hint">
            Paiement validé — saisissez le numéro à inviter.
          </p>
          <form class="transparency-page__form" @submit.prevent="submitRequest">
            <label class="transparency-page__field">
              <span>Numéro à inviter</span>
              <InputText
                v-model="targetPhone"
                type="tel"
                inputmode="tel"
                required
                placeholder="Ex. 07 00 00 00 00"
              />
            </label>
            <p class="transparency-page__notice">
              La personne verra votre identité AntiGoumin et pourra répondre en toute liberté.
            </p>
            <Button
              type="submit"
              label="Envoyer la demande"
              icon="pi pi-send"
              :loading="submitting"
              class="transparency-page__submit"
            />
          </form>
        </template>
      </Card>
    </section>

    <section class="transparency-page__list">
      <h2 class="transparency-page__section-title font-display">Historique</h2>
      <p v-if="loadingList">Chargement…</p>
      <p v-else-if="!requests.length" class="transparency-page__empty">
        Aucune demande pour le moment.
      </p>
      <div v-else class="transparency-page__cards">
        <Card v-for="item in requests" :key="item.id">
          <template #content>
            <div class="transparency-page__card-head">
              <div>
                <h3>{{ item.target_phone }}</h3>
                <Tag
                  :value="statusMeta[item.status]?.label ?? item.status"
                  :severity="statusMeta[item.status]?.severity ?? 'info'"
                />
              </div>
            </div>
            <p class="transparency-page__meta">
              Envoyée le {{ new Date(item.created_at).toLocaleDateString('fr-CI') }}
              · expire le {{ new Date(item.expires_at).toLocaleDateString('fr-CI') }}
            </p>
            <p v-if="item.status === 'ACCEPTED' && item.declared_status" class="transparency-page__response">
              Réponse privée :
              <strong>{{ declaredStatusLabels[item.declared_status] ?? item.declared_status }}</strong>
              <span v-if="item.declared_partner_name">
                ({{ item.declared_partner_name }})
              </span>
            </p>
          </template>
        </Card>
      </div>
    </section>
  </DashboardShell>
</template>

<style scoped>
.transparency-page__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.transparency-page__eyebrow {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.transparency-page__title {
  margin: 0.25rem 0 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-ink);
}

.transparency-page__subtitle {
  margin: 0.5rem 0 0;
  color: var(--color-muted);
  line-height: 1.55;
  max-width: 40rem;
}

.transparency-page__section-title {
  margin: 0 0 0.75rem;
  font-size: 1.125rem;
  font-weight: 800;
  color: var(--color-ink);
}

.transparency-page__hint,
.transparency-page__notice,
.transparency-page__empty,
.transparency-page__meta,
.transparency-page__response {
  color: var(--color-muted);
  line-height: 1.55;
}

.transparency-page__form-section,
.transparency-page__pay,
.transparency-page__list {
  margin-bottom: 1.5rem;
}

.transparency-page__form {
  display: grid;
  gap: 1rem;
}

.transparency-page__field {
  display: grid;
  gap: 0.375rem;
}

.transparency-page__field span {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-ink);
}

.transparency-page__submit :deep(.p-button) {
  width: 100%;
  justify-content: center;
}

.transparency-page__cards {
  display: grid;
  gap: 0.875rem;
}

.transparency-page__card-head h3 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 800;
  color: var(--color-ink);
}

.mb-3 {
  margin-bottom: 0.75rem;
}
</style>
