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
import { searchByPhone, type CertifiedStatus, type SearchResult } from '@/api/search'
import { verificationResultCopy } from '@/content/verificationResults'
import DashboardShell from '@/layouts/DashboardShell.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const phone = ref('')
const loading = ref(false)
const paying = ref(false)
const error = ref('')
const result = ref<SearchResult | null>(null)

const formattedPhone = computed(() => result.value?.phone ?? phone.value.trim())

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

async function runSearch(nextPhone?: string) {
  error.value = ''
  result.value = null
  const queryPhone = (nextPhone ?? phone.value).trim()
  if (!queryPhone) {
    error.value = 'Saisissez un numéro ivoirien à vérifier.'
    return
  }
  phone.value = queryPhone
  loading.value = true
  try {
    result.value = await searchByPhone(queryPhone)
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
  const queryPhone = typeof route.query.phone === 'string' ? route.query.phone : ''
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
        <p class="verification-page__eyebrow">Service payant</p>
        <h1 class="verification-page__title font-display">Vérifier un numéro</h1>
        <p class="verification-page__subtitle">
          Consultez uniquement ce qu’AntiGoumin sait sur un numéro — jamais ce qui se
          passe en dehors de la plateforme.
        </p>
      </div>
      <Tag value="200 FCFA / numéro" severity="info" />
    </header>

    <Card class="verification-page__form-card">
      <template #content>
        <form class="verification-page__form" @submit.prevent="runSearch()">
          <label class="verification-page__field">
            <span>Numéro ivoirien</span>
            <InputText
              v-model="phone"
              type="tel"
              inputmode="tel"
              autocomplete="tel"
              placeholder="Ex. 07 00 00 00 00"
              aria-label="Numéro à vérifier"
            />
          </label>
          <Button
            type="submit"
            label="Lancer la vérification"
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

    <Card v-if="needsPayment && result" class="verification-page__result">
      <template #content>
        <Tag value="Paiement requis" severity="warn" />
        <h2 class="verification-page__result-title font-display">
          Débloquer la consultation
        </h2>
        <p>
          Pour consulter le statut certifié du numéro
          <strong>{{ formattedPhone }}</strong>, payez
          <strong>{{ result.price_fcfa }} FCFA</strong>. L’accès reste valable 24 h pour
          ce numéro.
        </p>
        <Button
          label="Payer et consulter"
          icon="pi pi-credit-card"
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
        <RouterLink
          v-if="resultCopy.ctaRoute && resultCopy.ctaLabel"
          :to="{ path: resultCopy.ctaRoute, query: { phone: formattedPhone } }"
          class="verification-page__cta"
        >
          {{ resultCopy.ctaLabel }}
          <i class="pi pi-arrow-right" aria-hidden="true" />
        </RouterLink>
      </template>
    </Card>
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

.verification-page__cta {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  background: var(--color-primary);
  color: #fff;
  font-weight: 700;
  text-decoration: none;
}

.mt-3 {
  margin-top: 0.75rem;
}
</style>
