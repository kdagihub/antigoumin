<script setup lang="ts">
import Button from 'primevue/button'
import Card from 'primevue/card'
import Message from 'primevue/message'
import Tag from 'primevue/tag'
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { redirectToGeniusPay } from '@/api/checkout'
import { ApiError } from '@/api/client'
import { searchByPhone, fetchVerificationHistory, type SearchResult, type VerificationHistoryItem } from '@/api/search'
import IvorianPhoneInput from '@/components/IvorianPhoneInput.vue'
import VerificationLoader from '@/components/VerificationLoader.vue'
import { verificationPageCopy } from '@/content/verificationCopy'
import { verificationResultCopy } from '@/content/verificationResults'
import DashboardShell from '@/layouts/DashboardShell.vue'
import { useAuthStore } from '@/stores/auth'
import {
  downloadVerificationHistoryPdf,
  downloadVerificationResultPdf,
  verificationHistoryLabel,
} from '@/utils/moduleReceipts'
import { formatIvorianLocalDisplay, isValidIvorianLocalPhone, toIvorianLocalDigits } from '@/utils/ivorianPhone'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const phone = ref('')
const loading = ref(false)
const paying = ref(false)
const downloadingPdf = ref(false)
const error = ref('')
const result = ref<SearchResult | null>(null)
const history = ref<VerificationHistoryItem[]>([])
const loadingHistory = ref(true)
const consultedAt = ref<Date | null>(null)

const formattedPhone = computed(() =>
  formatIvorianLocalDisplay(result.value?.phone ?? phone.value),
)

const resultCopy = computed(() => {
  if (!result.value || result.value.certified_status === 'PAYMENT_REQUIRED') {
    return null
  }
  return verificationResultCopy[result.value.certified_status]
})

const needsPayment = computed(
  () => result.value?.certified_status === 'PAYMENT_REQUIRED',
)

const toneSeverity = computed(() => {
  const tone = resultCopy.value?.tone
  if (tone === 'success') return 'success'
  if (tone === 'warn') return 'warn'
  if (tone === 'info') return 'info'
  return 'secondary'
})

async function loadHistory() {
  loadingHistory.value = true
  try {
    const response = await fetchVerificationHistory()
    history.value = response.items
  } catch {
    history.value = []
  } finally {
    loadingHistory.value = false
  }
}

async function runSearch(nextPhone?: string) {
  error.value = ''
  result.value = null
  consultedAt.value = null
  const queryPhone = toIvorianLocalDigits((nextPhone ?? phone.value).trim())
  if (!isValidIvorianLocalPhone(queryPhone)) {
    error.value = verificationPageCopy.emptyPhoneError
    return
  }
  phone.value = queryPhone
  loading.value = true
  try {
    result.value = await searchByPhone(queryPhone)
    if (result.value.certified_status !== 'PAYMENT_REQUIRED') {
      consultedAt.value = new Date()
      await loadHistory()
    }
    await router.replace({
      path: '/app/verification',
      query: { phone: result.value.phone },
    })
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Vérification impossible.'
  } finally {
    loading.value = false
  }
}

async function exportCurrentResultPdf() {
  if (!result.value || result.value.certified_status === 'PAYMENT_REQUIRED') return
  downloadingPdf.value = true
  try {
    await downloadVerificationResultPdf(result.value, consultedAt.value ?? new Date())
  } finally {
    downloadingPdf.value = false
  }
}

async function exportHistoryPdf(item: VerificationHistoryItem) {
  downloadingPdf.value = true
  try {
    await downloadVerificationHistoryPdf(item)
  } finally {
    downloadingPdf.value = false
  }
}

async function payAndSearch() {
  if (!phone.value.trim()) return
  paying.value = true
  error.value = ''
  try {
    await redirectToGeniusPay({
      service_type: 'VERIFICATION',
      phone: phone.value.trim(),
    })
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Paiement impossible.'
    paying.value = false
  }
}

onMounted(async () => {
  await loadHistory()
  const queryPhone =
    typeof route.query.phone === 'string' ? toIvorianLocalDigits(route.query.phone) : ''
  if (queryPhone) {
    phone.value = queryPhone
    await runSearch(queryPhone)
  }
})
</script>

<template>
  <DashboardShell>
    <header class="verification-page__header">
      <div>
        <p class="verification-page__eyebrow">{{ verificationPageCopy.eyebrow }}</p>
        <h1 class="verification-page__title font-display">{{ verificationPageCopy.title }}</h1>
        <p class="verification-page__subtitle">
          {{ verificationPageCopy.subtitle }}
        </p>
      </div>
      <Tag :value="verificationPageCopy.priceTag" severity="info" />
    </header>

    <Card class="verification-page__form-card">
      <template #content>
        <form class="verification-page__form" @submit.prevent="runSearch()">
          <label class="verification-page__field">
            <span>{{ verificationPageCopy.fieldLabel }}</span>
            <IvorianPhoneInput
              id="verification-phone"
              v-model="phone"
              aria-label="Numéro mobile ivoirien à vérifier"
            />
            <small class="verification-page__field-hint">{{ verificationPageCopy.fieldHint }}</small>
          </label>
          <Button
            type="submit"
            :label="verificationPageCopy.submitLabel"
            icon="pi pi-search"
            :loading="loading"
            :disabled="!auth.isFullyVerified"
          />
        </form>
        <Message v-if="!auth.isFullyVerified" severity="warn" :closable="false" class="mt-3">
          Vérifiez d’abord votre email ou votre téléphone depuis
          <RouterLink to="/app/profil">Mon profil</RouterLink>.
        </Message>
      </template>
    </Card>

    <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>

    <Card v-if="loading" class="verification-page__loader-card">
      <template #content>
        <VerificationLoader variant="search" />
      </template>
    </Card>

    <Card v-else-if="paying" class="verification-page__loader-card">
      <template #content>
        <VerificationLoader variant="payment" />
      </template>
    </Card>

    <Card v-else-if="needsPayment && result" class="verification-page__result">
      <template #content>
        <Tag :value="verificationPageCopy.paymentTag" severity="warn" />
        <h2 class="verification-page__result-title font-display">
          {{ verificationPageCopy.paymentTitle }}
        </h2>
        <p class="verification-page__payment-body">
          {{
            verificationPageCopy.paymentBody
              .replace('{phone}', formattedPhone)
              .replace('{price}', String(result.price_fcfa))
          }}
        </p>
        <Button
          :label="verificationPageCopy.paymentCta"
          icon="pi pi-credit-card"
          class="verification-page__pay-btn"
          :loading="paying"
          @click="payAndSearch"
        />
      </template>
    </Card>

    <Card v-else-if="result && resultCopy" class="verification-page__result">
      <template #content>
        <Tag :value="resultCopy.title" :severity="toneSeverity" />
        <h2 class="verification-page__result-title font-display">
          Résultat pour {{ formattedPhone }}
        </h2>
        <p>{{ resultCopy.body }}</p>
        <div class="verification-page__actions">
          <Button
            label="Télécharger en PDF"
            icon="pi pi-download"
            severity="secondary"
            outlined
            :loading="downloadingPdf"
            @click="exportCurrentResultPdf"
          />
          <RouterLink
            v-if="resultCopy.ctaRoute && resultCopy.ctaLabel"
            :to="{ path: resultCopy.ctaRoute, query: { phone: formattedPhone } }"
            class="verification-page__cta"
          >
            {{ resultCopy.ctaLabel }}
            <i class="pi pi-arrow-right" aria-hidden="true" />
          </RouterLink>
        </div>
      </template>
    </Card>

    <section class="verification-page__history">
      <h2 class="verification-page__history-title font-display">Historique</h2>
      <VerificationLoader v-if="loadingHistory" variant="history" />
      <p v-else-if="!history.length" class="verification-page__history-empty">
        {{ verificationPageCopy.historyEmpty }}
      </p>
      <div v-else class="verification-page__history-cards">
        <Card v-for="item in history" :key="item.id">
          <template #content>
            <div class="verification-page__history-head">
              <div>
                <h3>{{ item.phone }}</h3>
                <Tag
                  :value="verificationHistoryLabel(item.certified_status)"
                  severity="info"
                />
              </div>
              <Button
                icon="pi pi-download"
                severity="secondary"
                text
                rounded
                aria-label="Télécharger en PDF"
                :loading="downloadingPdf"
                @click="exportHistoryPdf(item)"
              />
            </div>
            <p class="verification-page__history-meta">
              {{ item.amount_fcfa }} FCFA ·
              {{ new Date(item.consulted_at).toLocaleString('fr-CI') }}
            </p>
          </template>
        </Card>
      </div>
    </section>
  </DashboardShell>
</template>

<style scoped>
.verification-page__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.verification-page__eyebrow {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.verification-page__title {
  margin: 0.25rem 0 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-ink);
}

.verification-page__subtitle {
  margin: 0.5rem 0 0;
  color: var(--color-muted);
  max-width: 40rem;
  line-height: 1.55;
}

.verification-page__form {
  display: grid;
  gap: 1rem;
}

.verification-page__field {
  display: grid;
  gap: 0.375rem;
}

.verification-page__field span {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-ink);
}

.verification-page__field-hint {
  font-size: 0.8125rem;
  color: var(--color-muted);
  line-height: 1.45;
}

.verification-page__loader-card {
  margin-top: 1rem;
}

.verification-page__payment-body {
  margin: 0;
  color: var(--color-muted);
  line-height: 1.6;
  font-size: 1rem;
}

.verification-page__pay-btn :deep(.p-button-label) {
  font-weight: 800;
  letter-spacing: 0.04em;
}

.verification-page__result {
  margin-top: 1rem;
}

.verification-page__result-title {
  margin: 0.75rem 0 0.5rem;
  font-size: 1.125rem;
  font-weight: 800;
  color: var(--color-ink);
}

.verification-page__result p {
  margin: 0;
  color: var(--color-muted);
  line-height: 1.6;
}

.verification-page__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1rem;
}

.verification-page__cta {
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

.verification-page__history {
  margin-top: 2rem;
}

.verification-page__history-title {
  margin: 0 0 0.75rem;
  font-size: 1.125rem;
  font-weight: 800;
  color: var(--color-ink);
}

.verification-page__history-empty,
.verification-page__history-meta {
  color: var(--color-muted);
  line-height: 1.55;
}

.verification-page__history-cards {
  display: grid;
  gap: 0.875rem;
}

.verification-page__history-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.verification-page__history-head h3 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 800;
  color: var(--color-ink);
}

.mt-3 {
  margin-top: 0.75rem;
}
</style>
