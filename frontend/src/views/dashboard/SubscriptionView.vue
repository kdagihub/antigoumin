<script setup lang="ts">
import Button from 'primevue/button'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import {
  fetchAlliances,
  fetchEligibleDeclarations,
  type Alliance,
  type EligibleDeclaration,
} from '@/api/alliances'
import { redirectToGeniusPay } from '@/api/checkout'
import { ApiError } from '@/api/client'
import { fetchVipQuotaStatus, type VipQuotaStatus } from '@/api/subscriptions'
import PremiumVisibilityControl from '@/components/PremiumVisibilityControl.vue'
import { subscriptionPageCopy } from '@/content/alliancesCopy'
import DashboardShell from '@/layouts/DashboardShell.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const alliances = ref<Alliance[]>([])
const eligibleDeclarations = ref<EligibleDeclaration[]>([])
const loading = ref(true)
const paying = ref(false)
const error = ref('')
const vipQuota = ref<VipQuotaStatus | null>(null)

const selectedDeclarationId = ref<number | null>(null)

const activeAlliance = computed(() =>
  alliances.value.find((item) => item.status === 'ACTIVE') ?? null,
)

const canRenew = computed(
  () => auth.isFullyVerified && Boolean(activeAlliance.value),
)

const subscriptionEndDate = computed(() => {
  const raw =
    activeAlliance.value?.subscription_end_date ?? auth.user?.subscription_end_date ?? null
  return raw ? new Date(raw) : null
})

const subscriptionEnd = computed(() => {
  if (!subscriptionEndDate.value) return null
  return subscriptionEndDate.value.toLocaleDateString('fr-CI', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
})

const daysUntilExpiry = computed(() => {
  if (!subscriptionEndDate.value) return null
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const end = new Date(subscriptionEndDate.value)
  end.setHours(0, 0, 0, 0)
  return Math.round((end.getTime() - today.getTime()) / 86_400_000)
})

const isExpired = computed(() => {
  if (daysUntilExpiry.value === null) return false
  return daysUntilExpiry.value < 0
})

const isExpiringSoon = computed(() => {
  if (daysUntilExpiry.value === null) return false
  return daysUntilExpiry.value >= 0 && daysUntilExpiry.value <= 7
})

const declarationOptions = computed(() =>
  eligibleDeclarations.value.map((item) => ({
    label: item.partner_label,
    value: item.id,
  })),
)

const canSubscribe = computed(
  () =>
    auth.isFullyVerified &&
    !canRenew.value &&
    !auth.hasActiveSubscription &&
    eligibleDeclarations.value.length > 0,
)

const needsDeclaration = computed(
  () =>
    auth.isFullyVerified &&
    !canRenew.value &&
    !auth.hasActiveSubscription &&
    !loading.value &&
    eligibleDeclarations.value.length === 0,
)

const quotaLabels: Record<string, string> = {
  VERIFICATION: subscriptionPageCopy.quotaVerification,
  DECLARATION: subscriptionPageCopy.quotaDeclaration,
  TRANSPARENCY_REQUEST: subscriptionPageCopy.quotaTransparency,
}

async function loadSubscriptionContext() {
  loading.value = true
  error.value = ''
  try {
    const [allianceList, eligible, quotaStatus] = await Promise.all([
      fetchAlliances(),
      fetchEligibleDeclarations(),
      fetchVipQuotaStatus().catch(() => null),
    ])
    alliances.value = allianceList
    eligibleDeclarations.value = eligible
    vipQuota.value = quotaStatus
    if (!selectedDeclarationId.value && eligible.length === 1) {
      selectedDeclarationId.value = eligible[0]?.id ?? null
    }
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Chargement impossible.'
  } finally {
    loading.value = false
  }
}

async function subscribe() {
  if (!selectedDeclarationId.value) {
    error.value = 'Choisissez une relation.'
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

async function renew() {
  paying.value = true
  error.value = ''
  try {
    await redirectToGeniusPay({
      service_type: 'ALLIANCE_VIP',
      renewal: true,
    })
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Paiement impossible.'
    paying.value = false
  }
}

onMounted(loadSubscriptionContext)
</script>

<template>
  <DashboardShell>
    <header class="subscription-hero">
      <div class="subscription-hero__glow" aria-hidden="true" />
      <div class="subscription-hero__content">
        <div class="subscription-hero__icon" aria-hidden="true">🔔</div>
        <div class="subscription-hero__text">
          <p class="subscription-hero__eyebrow">{{ subscriptionPageCopy.heroLine }}</p>
          <h1 class="subscription-hero__title font-display">{{ subscriptionPageCopy.title }}</h1>
          <p class="subscription-hero__subtitle">{{ subscriptionPageCopy.intro }}</p>
        </div>
      </div>
    </header>

    <Message v-if="!auth.isFullyVerified" severity="warn" :closable="false" class="mb-3">
      <RouterLink to="/app/profil">Vérifiez votre compte</RouterLink>
      pour activer le Premium.
    </Message>

    <Message v-if="error" severity="error" :closable="false" class="mb-3">{{ error }}</Message>

    <nav
      v-if="!canRenew && !auth.hasActiveSubscription && auth.isFullyVerified"
      class="subscription-steps"
      aria-label="Étapes Premium"
    >
      <RouterLink
        to="/app/declarations"
        class="subscription-steps__item"
        :class="{ 'subscription-steps__item--done': eligibleDeclarations.length > 0 }"
      >
        <span class="subscription-steps__num">1</span>
        {{ subscriptionPageCopy.stepDeclare }}
      </RouterLink>
      <span class="subscription-steps__sep" aria-hidden="true" />
      <span
        class="subscription-steps__item"
        :class="{ 'subscription-steps__item--current': canSubscribe }"
      >
        <span class="subscription-steps__num">2</span>
        {{ subscriptionPageCopy.stepAlliance }}
      </span>
    </nav>

    <section class="subscription-action">
      <div v-if="canRenew" class="subscription-action__panel subscription-action__panel--cta">
        <div class="subscription-action__status-row">
          <Tag
            v-if="isExpired"
            :value="subscriptionPageCopy.expiredTag"
            severity="danger"
          />
          <Tag
            v-else-if="auth.hasActiveSubscription"
            :value="subscriptionPageCopy.activeTitle"
            severity="success"
          />
          <Tag
            v-if="isExpiringSoon && !isExpired && daysUntilExpiry !== null"
            :value="subscriptionPageCopy.expiringTag(daysUntilExpiry)"
            severity="warn"
          />
        </div>
        <p v-if="subscriptionEnd && !isExpired" class="subscription-action__meta">
          {{ subscriptionPageCopy.activeUntil }} {{ subscriptionEnd }}
        </p>
        <Button
          type="button"
          :label="subscriptionPageCopy.renewCta"
          icon="pi pi-refresh"
          class="subscription-action__cta"
          :loading="paying"
          @click="renew"
        />
      </div>

      <form
        v-else-if="canSubscribe"
        class="subscription-action__panel subscription-action__panel--cta"
        @submit.prevent="subscribe"
      >
        <Select
          v-if="eligibleDeclarations.length > 1"
          v-model="selectedDeclarationId"
          :options="declarationOptions"
          option-label="label"
          option-value="value"
          placeholder="Choisir une relation"
          class="subscription-action__select w-full"
        />
        <Button
          type="submit"
          :label="subscriptionPageCopy.subscribeCta"
          icon="pi pi-bell"
          class="subscription-action__cta"
          :loading="paying"
        />
      </form>

      <div
        v-else-if="needsDeclaration"
        class="subscription-action__panel subscription-action__panel--cta"
      >
        <p class="subscription-action__hint">{{ subscriptionPageCopy.declareHint }}</p>
        <RouterLink to="/app/declarations" class="subscription-action__cta-link">
          {{ subscriptionPageCopy.declareCta }}
          <i class="pi pi-heart-fill" aria-hidden="true" />
        </RouterLink>
      </div>

      <p v-else-if="loading" class="subscription-action__loading">Chargement…</p>
    </section>

    <ul class="subscription-benefits" aria-label="Avantages Premium">
      <li v-for="benefit in subscriptionPageCopy.benefits" :key="benefit">
        <i class="pi pi-check" aria-hidden="true" />
        {{ benefit }}
      </li>
    </ul>

    <section v-if="vipQuota?.active" class="subscription-page__section">
      <h2 class="subscription-quota__title font-display">{{ subscriptionPageCopy.quotaTitle }}</h2>
      <div class="subscription-quota__grid">
        <div
          v-for="item in vipQuota.quotas"
          :key="item.service_type"
          class="subscription-quota__item"
        >
          <span class="subscription-quota__label">
            {{ quotaLabels[item.service_type] ?? item.service_type }}
          </span>
          <strong class="subscription-quota__value">
            {{ item.remaining }}/{{ item.limit }}
          </strong>
          <span class="subscription-quota__hint">restant ce mois</span>
        </div>
      </div>
    </section>

    <section class="subscription-page__section">
      <PremiumVisibilityControl compact />
    </section>
  </DashboardShell>
</template>

<style scoped>
.subscription-hero {
  position: relative;
  margin-bottom: 1rem;
  border-radius: 1.25rem;
  overflow: hidden;
  background: linear-gradient(135deg, #fffbeb 0%, #ffffff 45%, #fef3c7 100%);
  border: 1px solid rgb(251 191 36 / 0.25);
}

.subscription-hero__glow {
  position: absolute;
  top: -3rem;
  right: -2rem;
  width: 10rem;
  height: 10rem;
  border-radius: 50%;
  background: radial-gradient(circle, rgb(251 191 36 / 0.22) 0%, transparent 70%);
  pointer-events: none;
}

.subscription-hero__content {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 0.875rem;
  padding: 1.125rem 1.25rem;
}

.subscription-hero__icon {
  font-size: 1.75rem;
  line-height: 1;
}

.subscription-hero__text {
  flex: 1;
  min-width: 0;
}

.subscription-hero__eyebrow {
  margin: 0;
  font-size: 0.6875rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: #b45309;
}

.subscription-hero__title {
  margin: 0.2rem 0 0;
  font-size: 1.375rem;
  font-weight: 800;
  color: var(--color-ink);
}

.subscription-hero__subtitle {
  margin: 0.375rem 0 0;
  font-size: 0.875rem;
  color: var(--color-muted);
  line-height: 1.5;
}

.subscription-steps {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 0.625rem 0.75rem;
  border-radius: 0.875rem;
  background: #f8fafc;
  border: 1px solid var(--color-border);
}

.subscription-steps__item {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-muted);
  text-decoration: none;
}

.subscription-steps__item--done {
  color: #047857;
}

.subscription-steps__item--current {
  color: #92400e;
}

.subscription-steps__num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 999px;
  background: #e2e8f0;
  font-size: 0.6875rem;
  font-weight: 800;
}

.subscription-steps__item--done .subscription-steps__num {
  background: #d1fae5;
  color: #047857;
}

.subscription-steps__item--current .subscription-steps__num {
  background: #fde68a;
  color: #92400e;
}

.subscription-steps__sep {
  flex: 1;
  height: 1px;
  background: #e2e8f0;
  min-width: 0.5rem;
}

.subscription-action {
  margin-bottom: 1.25rem;
}

.subscription-action__panel {
  padding: 1.125rem;
  border-radius: 1rem;
  border: 1px solid rgb(251 191 36 / 0.25);
  background: #fff;
  box-shadow: 0 8px 24px rgb(251 191 36 / 0.08);
}

.subscription-action__panel--cta {
  display: grid;
  gap: 0.875rem;
}

.subscription-action__status-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.subscription-action__meta {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-muted);
  text-align: center;
}

.subscription-action__hint {
  margin: 0;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-muted);
  text-align: center;
}

.subscription-action__select :deep(.p-select) {
  width: 100%;
}

.subscription-action__cta :deep(.p-button) {
  width: 100%;
  justify-content: center;
  padding: 0.875rem 1rem;
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  border-color: #d97706;
  color: #78350f;
  font-weight: 800;
  font-size: 0.9375rem;
}

.subscription-action__cta-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.875rem 1rem;
  border-radius: 0.75rem;
  background: linear-gradient(135deg, #ff4d94 0%, #ed147d 100%);
  color: #fff;
  font-weight: 800;
  font-size: 0.9375rem;
  text-decoration: none;
  box-shadow: 0 6px 18px rgb(237 20 125 / 0.28);
}

.subscription-action__loading {
  margin: 0;
  text-align: center;
  color: var(--color-muted);
  font-size: 0.875rem;
}

.subscription-benefits {
  list-style: none;
  margin: 0 0 1.25rem;
  padding: 0;
  display: grid;
  gap: 0.5rem;
}

.subscription-benefits li {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-ink);
  line-height: 1.4;
}

.subscription-benefits li:first-child,
.subscription-benefits li:nth-child(2) {
  font-weight: 700;
  color: #92400e;
}

.subscription-benefits i {
  color: #d97706;
  margin-top: 0.125rem;
  font-size: 0.75rem;
}

.subscription-page__section {
  margin-bottom: 1rem;
}

.subscription-quota__title {
  margin: 0 0 0.75rem;
  font-size: 1rem;
  color: var(--color-ink);
}

.subscription-quota__grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

.subscription-quota__item {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  padding: 0.875rem;
  border-radius: 0.875rem;
  background: linear-gradient(135deg, #fffbeb 0%, #ffffff 100%);
  border: 1px solid rgb(251 191 36 / 0.25);
}

.subscription-quota__label {
  font-size: 0.75rem;
  color: var(--color-muted);
}

.subscription-quota__value {
  font-size: 1.125rem;
  color: #92400e;
}

.subscription-quota__hint {
  font-size: 0.6875rem;
  color: var(--color-muted);
}

@media (max-width: 640px) {
  .subscription-quota__grid {
    grid-template-columns: 1fr;
  }
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.w-full {
  width: 100%;
}
</style>
