<script setup lang="ts">
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

import { ApiError } from '@/api/client'
import { requestPasswordReset } from '@/api/passwordReset'
import AuthLayout from '@/layouts/AuthLayout.vue'

const email = ref('')
const error = ref('')
const message = ref('')
const submitting = ref(false)

async function handleSubmit() {
  error.value = ''
  message.value = ''
  submitting.value = true
  try {
    const result = await requestPasswordReset(email.value.trim())
    message.value = result.message
  } catch (err) {
    error.value =
      err instanceof ApiError ? err.message : 'Demande impossible pour le moment.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AuthLayout
    title="Mot de passe oublié"
    subtitle="Recevez un lien sécurisé par email pour choisir un nouveau mot de passe."
    :highlights="[
      'Lien valable 1 heure',
      'Réponse identique que l’email existe ou non',
      'Comptes Google : utilisez la connexion Google',
    ]"
  >
    <Message v-if="error" severity="error" :closable="false" class="form-message">
      {{ error }}
    </Message>
    <Message v-if="message" severity="success" :closable="false" class="form-message">
      {{ message }}
      <span class="spam-hint">
        Pensez à vérifier vos courriers indésirables si le message n’apparaît pas.
      </span>
    </Message>

    <form v-if="!message" class="auth-form" @submit.prevent="handleSubmit">
      <div class="field">
        <label for="reset-email">Adresse email du compte</label>
        <InputText
          id="reset-email"
          v-model="email"
          type="email"
          autocomplete="email"
          required
          placeholder="vous@exemple.com"
          class="w-full"
        />
      </div>
      <Button
        type="submit"
        label="Envoyer le lien"
        icon="pi pi-envelope"
        :loading="submitting"
        class="w-full submit-button"
      />
    </form>

    <p class="auth-switch">
      <RouterLink to="/connexion">Retour à la connexion</RouterLink>
    </p>
  </AuthLayout>
</template>

<style scoped>
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.125rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.field label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-ink);
}

.form-message {
  margin-bottom: 1rem;
}

.spam-hint {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.8125rem;
  opacity: 0.9;
}

.submit-button {
  margin-top: 0.25rem;
}

.auth-switch {
  margin-top: 1.25rem;
  text-align: center;
  font-size: 0.875rem;
}

.auth-switch a {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
}

.auth-switch a:hover {
  text-decoration: underline;
}

.w-full {
  width: 100%;
}

.w-full :deep(.p-button),
.w-full :deep(.p-inputtext) {
  width: 100%;
}

.field :deep(.p-inputtext) {
  min-height: 2.875rem;
}

.submit-button :deep(.p-button) {
  min-height: 3rem;
  font-weight: 700;
}
</style>
