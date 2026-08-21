<script setup lang="ts">
import Button from 'primevue/button'
import Message from 'primevue/message'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { ApiError } from '@/api/client'
import AppShell from '@/layouts/AppShell.vue'
import { postAuthPath, useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const error = ref('')
const message = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    await auth.verifyEmailToken(String(route.params.token))
    message.value = 'Votre email est confirmé.'
    if (auth.isAuthenticated) {
      await auth.fetchMe()
      await router.replace(postAuthPath(auth.user))
      return
    }
  } catch (err) {
    error.value =
      err instanceof ApiError ? err.message : 'Lien invalide ou expiré.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <AppShell>
    <h1>Confirmation de l’email</h1>
    <p v-if="loading">Vérification en cours…</p>
    <Message v-else-if="error" severity="error" :closable="false">{{ error }}</Message>
    <Message v-else-if="message" severity="success" :closable="false">{{ message }}</Message>
    <Button
      v-if="!loading"
      class="mt-4"
      label="Aller à mon espace"
      @click="router.push(auth.isAuthenticated ? postAuthPath(auth.user) : '/connexion')"
    />
  </AppShell>
</template>
