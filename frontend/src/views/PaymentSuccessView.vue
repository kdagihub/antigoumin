<script setup lang="ts">
import Button from 'primevue/button'
import Message from 'primevue/message'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { ApiError } from '@/api/client'
import { fetchCheckoutStatus } from '@/api/payments'
import AppShell from '@/layouts/AppShell.vue'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const error = ref('')
const message = ref('')
const credited = ref(false)

onMounted(async () => {
  const reference = String(route.query.reference ?? '')
  if (!reference) {
    error.value = 'Référence de paiement manquante.'
    loading.value = false
    return
  }
  try {
    const status = await fetchCheckoutStatus(reference)
    credited.value = status.credited
    message.value = status.message
    if (
      status.credited &&
      status.service_type === 'VERIFICATION' &&
      status.phone
    ) {
      await router.replace({
        path: '/app/verification',
        query: { phone: status.phone },
      })
      return
    }
    if (status.credited && status.service_type === 'DECLARATION') {
      await router.replace({
        path: '/app/declarations',
        query: { reference },
      })
      return
    }
    if (status.credited && status.service_type === 'TRANSPARENCY_REQUEST') {
      await router.replace({
        path: '/app/transparence',
        query: { reference },
      })
      return
    }
    if (status.credited && status.service_type === 'ALLIANCE_VIP') {
      await router.replace({ path: '/app/abonnement' })
      return
    }
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Statut de paiement indisponible.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <AppShell>
    <h1>Paiement</h1>
    <p v-if="loading">Vérification du paiement…</p>
    <Message v-else-if="error" severity="error" :closable="false">{{ error }}</Message>
    <Message v-else-if="credited" severity="success" :closable="false">{{ message }}</Message>
    <Message v-else severity="warn" :closable="false">{{ message }}</Message>
    <Button class="mt-4" label="Retour à mon espace" @click="router.push('/app')" />
  </AppShell>
</template>
