<script setup lang="ts">
import Button from 'primevue/button'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { ApiError } from '@/api/client'
import {
  fetchTransparencyRequest,
  respondToTransparencyRequest,
  type TransparencyRequestPreview,
  type TransparencyResponsePayload,
} from '@/api/transparency'
import AppShell from '@/layouts/AppShell.vue'

const route = useRoute()
const router = useRouter()
const token = route.params.token as string

const preview = ref<TransparencyRequestPreview | null>(null)
const declaredStatus = ref<TransparencyResponsePayload['declared_status']>()
const partnerName = ref('')
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const success = ref('')

const statusOptions = [
  { label: 'Je suis en couple', value: 'ENGAGED' },
  { label: 'Je suis disponible', value: 'AVAILABLE' },
  { label: 'Je préfère ne pas répondre', value: 'PREFER_NOT_TO_ANSWER' },
]

onMounted(async () => {
  try {
    preview.value = await fetchTransparencyRequest(token)
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Demande introuvable.'
  } finally {
    loading.value = false
  }
})

async function respond(action: TransparencyResponsePayload['action']) {
  if (action === 'ACCEPT' && !declaredStatus.value) {
    error.value = 'Choisissez une réponse avant de continuer.'
    return
  }

  error.value = ''
  submitting.value = true
  try {
    const result = await respondToTransparencyRequest(token, {
      action,
      declared_status: action === 'ACCEPT' ? declaredStatus.value : undefined,
      declared_partner_name:
        action === 'ACCEPT' && declaredStatus.value === 'ENGAGED'
          ? partnerName.value.trim()
          : undefined,
    })
    success.value = result.message
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Réponse impossible.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AppShell>
    <Card>
      <template #title>
        <h1 class="page-title font-display">Demande de Transparence</h1>
      </template>
      <template #subtitle>
        <p v-if="preview" class="page-subtitle">
          Invitation envoyée par <strong>{{ preview.requester_display_name }}</strong>
        </p>
      </template>
      <template #content>
        <Message v-if="loading" severity="info" :closable="false">
          Chargement de la demande…
        </Message>
        <Message v-else-if="error" severity="error" :closable="false">{{ error }}</Message>
        <Message v-if="success" severity="success" :closable="false">{{ success }}</Message>

        <template v-if="preview && !success">
          <Message severity="info" :closable="false">
            {{ preview.consent_notice }}
          </Message>

          <div class="response-form">
            <label for="declared-status">Votre réponse volontaire</label>
            <Select
              id="declared-status"
              v-model="declaredStatus"
              :options="statusOptions"
              option-label="label"
              option-value="value"
              placeholder="Choisir une réponse"
              class="w-full"
            />

            <div v-if="declaredStatus === 'ENGAGED'" class="field">
              <label for="partner-name">Prénom du partenaire (facultatif et privé)</label>
              <InputText
                id="partner-name"
                v-model="partnerName"
                placeholder="Vous pouvez laisser ce champ vide"
                class="w-full"
              />
            </div>

            <Button
              label="Envoyer ma réponse privée"
              icon="pi pi-check"
              :loading="submitting"
              class="w-full"
              @click="respond('ACCEPT')"
            />
            <Button
              label="Je préfère refuser"
              severity="secondary"
              outlined
              :disabled="submitting"
              class="w-full"
              @click="respond('REFUSE')"
            />

            <div class="safety-actions">
              <button type="button" :disabled="submitting" @click="respond('BLOCK')">
                Bloquer l’auteur
              </button>
              <button type="button" :disabled="submitting" @click="respond('REPORT')">
                Signaler un abus
              </button>
            </div>
          </div>
        </template>

        <Button
          v-if="success"
          label="Retour à l'accueil"
          icon="pi pi-home"
          class="w-full"
          @click="router.push('/')"
        />
      </template>
    </Card>
  </AppShell>
</template>

<style scoped>
.page-title {
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--color-ink);
}

.page-subtitle {
  color: var(--color-muted);
}

.response-form {
  display: grid;
  gap: 1rem;
  margin-top: 1.25rem;
}

.response-form label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-ink);
}

.field {
  display: grid;
  gap: 0.5rem;
}

.safety-actions {
  display: flex;
  justify-content: center;
  gap: 1.25rem;
  margin-top: 0.25rem;
}

.safety-actions button {
  border: 0;
  background: none;
  color: var(--color-muted);
  font-size: 0.75rem;
  text-decoration: underline;
  cursor: pointer;
}

.safety-actions button:hover {
  color: #ed147d;
}
</style>
