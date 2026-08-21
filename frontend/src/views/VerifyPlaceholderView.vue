<script setup lang="ts">
import Button from 'primevue/button'
import Card from 'primevue/card'
import Message from 'primevue/message'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { ApiError } from '@/api/client'
import {
  decideDeclaration,
  fetchDeclarationPreview,
  type DeclarationPreview,
} from '@/api/declarations'
import AppShell from '@/layouts/AppShell.vue'

const route = useRoute()
const router = useRouter()
const token = route.params.token as string
const preview = ref<DeclarationPreview | null>(null)
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const success = ref('')

onMounted(async () => {
  try {
    preview.value = await fetchDeclarationPreview(token)
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Déclaration introuvable.'
  } finally {
    loading.value = false
  }
})

async function decide(accept: boolean) {
  submitting.value = true
  error.value = ''
  try {
    const result = await decideDeclaration(token, accept)
    success.value = result.message
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Décision impossible.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AppShell>
    <Card>
      <template #title>
        <h1 class="page-title font-display">Validation de relation</h1>
      </template>
      <template #content>
        <Message v-if="loading" severity="info" :closable="false">
          Chargement de la déclaration…
        </Message>
        <Message v-else-if="error" severity="error" :closable="false">{{ error }}</Message>
        <Message v-if="success" severity="success" :closable="false">{{ success }}</Message>

        <template v-if="preview && !success">
          <div class="declaration-summary">
            <p>
              <strong>{{ preview.author_name }}</strong> vous invite à certifier une relation
              <strong>{{ preview.relation_type.toLowerCase() }}</strong>.
            </p>
            <span
              class="visibility-badge"
              :class="{ private: preview.visibility === 'PRIVATE' }"
            >
              {{
                preview.visibility === 'PUBLIC_CERTIFIED'
                  ? 'Statut certifié public'
                  : 'Relation privée'
              }}
            </span>
          </div>

          <Message severity="info" :closable="false" icon="pi pi-info-circle">
            {{ preview.consent_notice }}
          </Message>

          <div class="decision-actions">
            <Button
              :label="
                preview.visibility === 'PUBLIC_CERTIFIED'
                  ? 'Accepter et certifier publiquement'
                  : 'Accepter la relation privée'
              "
              icon="pi pi-check"
              :loading="submitting"
              class="w-full"
              @click="decide(true)"
            />
            <Button
              label="Refuser"
              severity="secondary"
              outlined
              :disabled="submitting"
              class="w-full"
              @click="decide(false)"
            />
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

.declaration-summary {
  margin-bottom: 1rem;
  color: var(--color-ink);
}

.visibility-badge {
  display: inline-flex;
  margin-top: 0.75rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  background: #fce7f3;
  color: #be185d;
  font-size: 0.75rem;
  font-weight: 700;
}

.visibility-badge.private {
  background: #f1f5f9;
  color: #475569;
}

.decision-actions {
  display: grid;
  gap: 0.75rem;
  margin-top: 1.25rem;
}

.w-full :deep(.p-button) {
  width: 100%;
  justify-content: center;
}

</style>
