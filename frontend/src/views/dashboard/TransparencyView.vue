<script setup lang="ts">
import Button from 'primevue/button'
import Card from 'primevue/card'
import Message from 'primevue/message'
import Tag from 'primevue/tag'
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { redirectToGeniusPay } from '@/api/checkout'
import { ApiError } from '@/api/client'
import { fetchCheckoutStatus, fetchUnusedPayment } from '@/api/payments'
import { fetchVipQuotaStatus, getVipQuotaItem, type VipQuotaStatus } from '@/api/subscriptions'
import {
  createTransparencyRequest,
  fetchTransparencyRequests,
  type TransparencyRequest,
} from '@/api/transparency'
import FidelityLoader from '@/components/FidelityLoader.vue'
import IvorianPhoneInput from '@/components/IvorianPhoneInput.vue'
import {
  fidelityDeclaredStatusLabels,
  fidelityPageCopy,
  fidelityStatusCopy,
} from '@/content/fidelityCopy'
import DashboardShell from '@/layouts/DashboardShell.vue'
import { useAuthStore } from '@/stores/auth'
import { downloadTransparencyPdf } from '@/utils/moduleReceipts'
import { formatIvorianLocalDisplay, isValidIvorianLocalPhone } from '@/utils/ivorianPhone'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const requests = ref<TransparencyRequest[]>([])
const loadingList = ref(true)
const paymentId = ref<number | null>(null)
const vipQuota = ref<VipQuotaStatus | null>(null)
const paying = ref(false)
const submitting = ref(false)
const downloadingPdfId = ref<number | null>(null)
const error = ref('')
const success = ref('')
const targetPhone = ref('')

const transparencyQuota = computed(() => getVipQuotaItem(vipQuota.value, 'TRANSPARENCY_REQUEST'))
const canUseVipQuota = computed(() => (transparencyQuota.value?.remaining ?? 0) > 0)
const canCreate = computed(
  () => Boolean(paymentId.value) || canUseVipQuota.value || import.meta.env.DEV,
)
const showForm = computed(() => canCreate.value && auth.isFullyVerified)
const formHint = computed(() =>
  paymentId.value
    ? fidelityPageCopy.formHint
    : canUseVipQuota.value
      ? fidelityPageCopy.vipFormHint
      : fidelityPageCopy.formHint,
)

type FidelityStatusKey = keyof typeof fidelityStatusCopy

function statusMeta(status: string) {
  if (status in fidelityStatusCopy) {
    return fidelityStatusCopy[status as FidelityStatusKey]
  }
  return { label: status, severity: 'info' as const }
}

async function exportTransparencyPdf(item: TransparencyRequest) {
  downloadingPdfId.value = item.id
  try {
    await downloadTransparencyPdf(item)
  } finally {
    downloadingPdfId.value = null
  }
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

async function loadVipQuota() {
  try {
    vipQuota.value = await fetchVipQuotaStatus()
  } catch {
    vipQuota.value = null
  }
}

async function resolvePayment() {
  const reference = typeof route.query.reference === 'string' ? route.query.reference : ''
  if (reference) {
    try {
      const status = await fetchCheckoutStatus(reference)
      if (status.payment_id) {
        paymentId.value = status.payment_id
        success.value = fidelityPageCopy.paymentSuccess
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
  if (!paymentId.value && !canUseVipQuota.value && !import.meta.env.DEV) {
    error.value = 'Paiement requis avant envoi.'
    return
  }
  if (!isValidIvorianLocalPhone(targetPhone.value)) {
    error.value = 'Saisissez un numéro mobile ivoirien valide (10 chiffres).'
    return
  }
  submitting.value = true
  try {
    await createTransparencyRequest({
      target_phone: targetPhone.value.trim(),
      payment_id: paymentId.value ?? undefined,
    })
    success.value = fidelityPageCopy.sendSuccess
    targetPhone.value = ''
    paymentId.value = null
    paymentId.value = null
    await Promise.all([loadRequests(), loadVipQuota()])
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Envoi impossible.'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadRequests(), resolvePayment(), loadVipQuota()])
})
</script>

<template>
  <DashboardShell>
    <header class="fidelity-hero">
      <div class="fidelity-hero__glow" aria-hidden="true" />
      <div class="fidelity-hero__monitor-mini" aria-hidden="true">
        <svg viewBox="0 0 120 32" preserveAspectRatio="none">
          <path
            class="fidelity-hero__ecg"
            d="M0 16 H20 L24 16 L26 8 L28 24 L30 16 H50 L54 16 L56 12 L58 20 L60 16 H80 L84 16 L86 6 L88 26 L90 16 H120"
          />
        </svg>
      </div>
      <div class="fidelity-hero__content">
        <div class="fidelity-hero__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
            />
          </svg>
        </div>
        <div class="fidelity-hero__text">
          <p class="fidelity-hero__eyebrow">{{ fidelityPageCopy.eyebrow }}</p>
          <h1 class="fidelity-hero__title font-display">{{ fidelityPageCopy.title }}</h1>
          <p class="fidelity-hero__subtitle">{{ fidelityPageCopy.subtitle }}</p>
        </div>
        <Tag :value="fidelityPageCopy.priceTag" severity="info" class="fidelity-hero__tag" />
      </div>
    </header>

    <Message v-if="!auth.isFullyVerified" severity="warn" :closable="false" class="mb-3">
      Confirmez votre email ou votre téléphone depuis
      <RouterLink to="/app/profil">Mon profil</RouterLink>
      pour lancer un test de fidélité.
    </Message>

    <Message v-if="error" severity="error" :closable="false" class="mb-3">{{ error }}</Message>
    <Message v-if="success" severity="success" :closable="false" class="mb-3">
      {{ success }}
    </Message>

    <Card v-if="paying" class="fidelity-page__loader-card">
      <template #content>
        <FidelityLoader variant="payment" />
      </template>
    </Card>

    <section v-else-if="!canCreate && auth.isFullyVerified" class="fidelity-page__section">
      <Card class="fidelity-card fidelity-card--pay">
        <template #content>
          <div class="fidelity-card__head">
            <span class="fidelity-card__emoji" aria-hidden="true">🫀</span>
            <div>
              <h2 class="fidelity-card__title font-display">{{ fidelityPageCopy.payTitle }}</h2>
              <p class="fidelity-card__body">
                {{
                  auth.hasActiveSubscription
                    ? fidelityPageCopy.vipQuotaExhausted
                    : fidelityPageCopy.payBody
                }}
              </p>
            </div>
          </div>
          <Button
            :label="fidelityPageCopy.payCta"
            icon="pi pi-heart"
            class="fidelity-card__cta"
            :loading="paying"
            @click="payTransparency"
          />
        </template>
      </Card>
    </section>

    <Card v-if="submitting" class="fidelity-page__loader-card">
      <template #content>
        <FidelityLoader variant="search" />
      </template>
    </Card>

    <section v-else-if="showForm && !paying" class="fidelity-page__section">
      <Card class="fidelity-card fidelity-card--form">
        <template #content>
          <div class="fidelity-card__head">
            <span class="fidelity-card__emoji" aria-hidden="true">💙</span>
            <div>
              <h2 class="fidelity-card__title font-display">{{ fidelityPageCopy.formTitle }}</h2>
              <p v-if="canCreate" class="fidelity-card__body">{{ formHint }}</p>
            </div>
          </div>

          <form class="fidelity-form" @submit.prevent="submitRequest">
            <label class="fidelity-form__field">
              <span>{{ fidelityPageCopy.targetPhoneLabel }}</span>
              <IvorianPhoneInput
                id="transparency-target-phone"
                v-model="targetPhone"
                aria-label="Numéro mobile ivoirien à inviter"
              />
              <small>{{ fidelityPageCopy.targetPhoneHint }}</small>
            </label>

            <div class="fidelity-form__notice">
              <i class="pi pi-info-circle" aria-hidden="true" />
              <p>{{ fidelityPageCopy.formNotice }}</p>
            </div>

            <Button
              type="submit"
              :label="fidelityPageCopy.submitLabel"
              icon="pi pi-send"
              :loading="submitting"
              class="fidelity-form__submit"
            />
          </form>
        </template>
      </Card>
    </section>

    <section class="fidelity-page__section">
      <h2 class="fidelity-page__history-title font-display">{{ fidelityPageCopy.historyTitle }}</h2>
      <FidelityLoader v-if="loadingList" variant="history" />
      <div v-else-if="!requests.length" class="fidelity-empty">
        <div class="fidelity-empty__monitor" aria-hidden="true">
          <svg viewBox="0 0 200 48" preserveAspectRatio="none">
            <path
              class="fidelity-empty__ecg"
              d="M0 24 H30 L36 24 L40 10 L44 38 L48 24 H80 L86 24 L90 18 L94 30 L98 24 H130 L136 24 L140 12 L144 36 L148 24 H200"
            />
          </svg>
        </div>
        <p>{{ fidelityPageCopy.historyEmpty }}</p>
      </div>
      <div v-else class="fidelity-list">
        <Card v-for="item in requests" :key="item.id" class="fidelity-list__card">
          <template #content>
            <div class="fidelity-list__head">
              <div class="fidelity-list__icon" aria-hidden="true">💙</div>
              <div class="fidelity-list__info">
                <h3>{{ formatIvorianLocalDisplay(item.target_phone) }}</h3>
                <Tag
                  :value="statusMeta(item.status).label"
                  :severity="statusMeta(item.status).severity"
                />
              </div>
              <Button
                icon="pi pi-download"
                severity="secondary"
                text
                rounded
                aria-label="Télécharger en PDF"
                :loading="downloadingPdfId === item.id"
                @click="exportTransparencyPdf(item)"
              />
            </div>
            <p class="fidelity-list__meta">
              Envoyé le {{ new Date(item.created_at).toLocaleDateString('fr-CI') }}
              · expire le {{ new Date(item.expires_at).toLocaleDateString('fr-CI') }}
            </p>
            <p v-if="item.status === 'ACCEPTED' && item.declared_status" class="fidelity-list__response">
              Réponse privée :
              <strong>{{
                fidelityDeclaredStatusLabels[item.declared_status] ?? item.declared_status
              }}</strong>
              <span v-if="item.declared_partner_name"> ({{ item.declared_partner_name }})</span>
            </p>
          </template>
        </Card>
      </div>
    </section>
  </DashboardShell>
</template>

<style scoped>
.fidelity-hero {
  position: relative;
  margin-bottom: 1.25rem;
  border-radius: 1.25rem;
  overflow: hidden;
  background: linear-gradient(135deg, #eff6ff 0%, #ffffff 45%, #dbeafe 100%);
  border: 1px solid rgb(59 130 246 / 0.18);
}

.fidelity-hero__glow {
  position: absolute;
  top: -3rem;
  right: -2rem;
  width: 10rem;
  height: 10rem;
  border-radius: 50%;
  background: radial-gradient(circle, rgb(59 130 246 / 0.2) 0%, transparent 70%);
  pointer-events: none;
}

.fidelity-hero__monitor-mini {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2.5rem;
  opacity: 0.35;
  overflow: hidden;
  background: linear-gradient(180deg, transparent, rgb(30 58 95 / 0.08));
}

.fidelity-hero__ecg {
  fill: none;
  stroke: #3b82f6;
  stroke-width: 2;
  stroke-linecap: round;
}

.fidelity-hero__content {
  position: relative;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem 1.375rem 1.5rem;
}

.fidelity-hero__icon {
  width: 2rem;
  height: 2rem;
  color: #2563eb;
  filter: drop-shadow(0 4px 8px rgb(37 99 235 / 0.25));
  animation: hero-heart 1.1s ease-in-out infinite;
}

.fidelity-hero__text {
  flex: 1 1 14rem;
  min-width: 0;
}

.fidelity-hero__eyebrow {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #2563eb;
}

.fidelity-hero__title {
  margin: 0.25rem 0 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-ink);
}

.fidelity-hero__subtitle {
  margin: 0.5rem 0 0;
  color: var(--color-muted);
  line-height: 1.6;
  max-width: 40rem;
}

.fidelity-hero__tag :deep(.p-tag) {
  background: rgb(59 130 246 / 0.1);
  color: #1d4ed8;
}

.fidelity-page__section {
  margin-bottom: 1.5rem;
}

.fidelity-page__loader-card {
  margin-bottom: 1.5rem;
}

.fidelity-card :deep(.p-card-body),
.fidelity-card :deep(.p-card-content) {
  padding: 1.25rem;
}

.fidelity-card--pay,
.fidelity-card--form {
  border: 1px solid rgb(59 130 246 / 0.16);
  box-shadow: 0 8px 24px rgb(59 130 246 / 0.08);
}

.fidelity-card__head {
  display: flex;
  gap: 0.875rem;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.fidelity-card__emoji {
  font-size: 1.75rem;
  line-height: 1;
}

.fidelity-card__title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 800;
  color: var(--color-ink);
}

.fidelity-card__body {
  margin: 0.375rem 0 0;
  color: var(--color-muted);
  line-height: 1.6;
}

.fidelity-card__cta :deep(.p-button) {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-color: #2563eb;
}

.fidelity-card__cta :deep(.p-button-label) {
  font-weight: 800;
  letter-spacing: 0.04em;
}

.fidelity-form {
  display: grid;
  gap: 1rem;
}

.fidelity-form__field {
  display: grid;
  gap: 0.375rem;
}

.fidelity-form__field span {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-ink);
}

.fidelity-form__field small {
  font-size: 0.8125rem;
  color: var(--color-muted);
}

.fidelity-form__notice {
  display: flex;
  gap: 0.625rem;
  align-items: flex-start;
  padding: 0.875rem;
  border-radius: 0.875rem;
  background: rgb(59 130 246 / 0.06);
  border: 1px solid rgb(59 130 246 / 0.14);
}

.fidelity-form__notice i {
  color: #2563eb;
  margin-top: 0.125rem;
}

.fidelity-form__notice p {
  margin: 0;
  font-size: 0.875rem;
  color: #1e40af;
  line-height: 1.55;
}

.fidelity-form__submit :deep(.p-button) {
  width: 100%;
  justify-content: center;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-color: #2563eb;
}

.fidelity-page__history-title {
  margin: 0 0 0.875rem;
  font-size: 1.125rem;
  font-weight: 800;
  color: var(--color-ink);
}

.fidelity-empty {
  display: grid;
  justify-items: center;
  gap: 0.875rem;
  padding: 1.5rem 1rem;
  border-radius: 1rem;
  border: 1px dashed rgb(59 130 246 / 0.25);
  background: rgb(59 130 246 / 0.04);
  text-align: center;
}

.fidelity-empty__monitor {
  width: min(100%, 14rem);
  height: 3rem;
  border-radius: 0.625rem;
  overflow: hidden;
  background: #0f172a;
  padding: 0.5rem;
}

.fidelity-empty__ecg {
  fill: none;
  stroke: #38bdf8;
  stroke-width: 2;
  stroke-linecap: round;
  animation: empty-ecg 2s ease-in-out infinite;
}

.fidelity-empty p {
  margin: 0;
  max-width: 22rem;
  color: var(--color-muted);
  line-height: 1.6;
}

.fidelity-list {
  display: grid;
  gap: 0.875rem;
}

.fidelity-list__card {
  border: 1px solid rgb(59 130 246 / 0.12);
  transition: box-shadow 0.2s ease;
}

.fidelity-list__card:hover {
  box-shadow: 0 6px 20px rgb(59 130 246 / 0.1);
}

.fidelity-list__head {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.fidelity-list__icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #dbeafe, #eff6ff);
  font-size: 1.125rem;
  flex-shrink: 0;
}

.fidelity-list__info {
  flex: 1;
  min-width: 0;
}

.fidelity-list__info h3 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 800;
  color: var(--color-ink);
}

.fidelity-list__meta,
.fidelity-list__response {
  margin: 0.75rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-muted);
  line-height: 1.5;
}

.fidelity-list__response strong {
  color: #1d4ed8;
}

.mb-3 {
  margin-bottom: 0.75rem;
}

@keyframes hero-heart {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

@keyframes empty-ecg {
  0%,
  100% {
    opacity: 0.45;
  }
  50% {
    opacity: 1;
  }
}
</style>
