<script setup lang="ts">
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useRouter } from 'vue-router'

import AppShell from '@/layouts/AppShell.vue'

const router = useRouter()
</script>

<template>
  <AppShell>
    <h1>Paiement non abouti</h1>
    <Message severity="error" :closable="false">
      Le paiement a été annulé, a échoué ou a expiré. Aucun service n’a été débloqué.
    </Message>
    <Button class="mt-4" label="Retour au profil" @click="router.push('/profil')" />
  </AppShell>
</template>
