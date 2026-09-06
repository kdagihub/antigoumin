<script setup lang="ts">
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import ToggleSwitch from 'primevue/toggleswitch'
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { updateStatusVisibility } from '@/api/auth'
import { ApiError } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const props = withDefaults(
  defineProps<{
    compact?: boolean
  }>(),
  { compact: false },
)

const auth = useAuthStore()
const router = useRouter()
const loading = ref(false)
const message = ref('')
const error = ref('')

async function onToggle(nextValue: boolean) {
  message.value = ''
  error.value = ''

  if (!auth.hasActiveSubscription) {
    await router.push('/app/abonnement')
    return
  }

  loading.value = true
  try {
    await updateStatusVisibility(nextValue)
    await auth.fetchMe()
    message.value = nextValue
      ? 'Votre statut est désormais consultable publiquement.'
      : 'Votre statut n’est plus consultable publiquement.'
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Modification impossible.'
  } finally {
    loading.value = false
  }
}

function onLockedClick() {
  router.push('/app/abonnement')
}
</script>

<template>
  <div class="premium-visibility" :class="{ 'premium-visibility--compact': compact }">
    <div class="premium-visibility__head">
      <div>
        <p class="premium-visibility__label">Visibilité de mon statut</p>
        <Tag
          :value="auth.user?.is_status_searchable ? 'Consultable' : 'Privé'"
          :severity="auth.user?.is_status_searchable ? 'success' : 'secondary'"
        />
      </div>
      <div
        class="premium-visibility__switch-wrap"
        :class="{ 'premium-visibility__switch-wrap--locked': !auth.hasActiveSubscription }"
        @click.capture="!auth.hasActiveSubscription ? onLockedClick() : undefined"
      >
        <ToggleSwitch
          :model-value="Boolean(auth.user?.is_status_searchable)"
          :disabled="loading || !auth.isFullyVerified || !auth.hasActiveSubscription"
          @update:model-value="onToggle"
        />
      </div>
    </div>
    <p v-if="!auth.hasActiveSubscription" class="premium-visibility__hint">
      Réservé au
      <RouterLink to="/app/abonnement">service Premium</RouterLink>
      — touchez pour vous abonner.
    </p>
    <p v-else class="premium-visibility__hint">
      Choisissez si votre statut certifié peut être consulté par d’autres membres.
    </p>
    <Button
      v-if="!auth.hasActiveSubscription"
      label="Passer Premium pour gérer ma visibilité"
      icon="pi pi-star-fill"
      severity="secondary"
      outlined
      size="small"
      class="premium-visibility__cta"
      @click="onLockedClick"
    />
    <p v-if="message" class="premium-visibility__success">{{ message }}</p>
    <p v-if="error" class="premium-visibility__error">{{ error }}</p>
  </div>
</template>

<style scoped>
.premium-visibility {
  padding: 1rem;
  border-radius: 0.875rem;
  border: 1px solid var(--color-border);
  background: #fff;
}

.premium-visibility--compact {
  padding: 0.875rem;
}

.premium-visibility__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.premium-visibility__label {
  margin: 0 0 0.375rem;
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-ink);
}

.premium-visibility__switch-wrap--locked {
  opacity: 0.45;
  cursor: pointer;
}

.premium-visibility__hint {
  margin: 0.625rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-muted);
  line-height: 1.5;
}

.premium-visibility__hint a {
  color: #b45309;
  font-weight: 700;
}

.premium-visibility__cta {
  margin-top: 0.75rem;
}

.premium-visibility__cta :deep(.p-button) {
  width: 100%;
  justify-content: center;
}

.premium-visibility__success {
  margin: 0.5rem 0 0;
  font-size: 0.8125rem;
  color: #047857;
  font-weight: 600;
}

.premium-visibility__error {
  margin: 0.5rem 0 0;
  font-size: 0.8125rem;
  color: #be123c;
  font-weight: 600;
}
</style>
