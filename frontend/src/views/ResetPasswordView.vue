<script setup lang="ts">
import Button from 'primevue/button'
import Message from 'primevue/message'
import Password from 'primevue/password'
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { ApiError } from '@/api/client'
import { confirmPasswordReset } from '@/api/passwordReset'
import AuthLayout from '@/layouts/AuthLayout.vue'

const route = useRoute()
const router = useRouter()
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const message = ref('')
const submitting = ref(false)

async function handleSubmit() {
  error.value = ''
  if (password.value !== confirmPassword.value) {
    error.value = 'Les mots de passe ne correspondent pas.'
    return
  }
  submitting.value = true
  try {
    const result = await confirmPasswordReset(String(route.params.token), password.value)
    message.value = result.message
  } catch (err) {
    error.value =
      err instanceof ApiError ? err.message : 'Réinitialisation impossible.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AuthLayout
    title="Nouveau mot de passe"
    subtitle="Choisissez un mot de passe solide pour sécuriser votre compte."
  >
    <Message v-if="error" severity="error" :closable="false" class="form-message">
      {{ error }}
    </Message>
    <Message v-if="message" severity="success" :closable="false" class="form-message">
      {{ message }}
    </Message>

    <form v-if="!message" class="auth-form" @submit.prevent="handleSubmit">
      <div class="field">
        <label for="new-password">Nouveau mot de passe</label>
        <Password
          id="new-password"
          v-model="password"
          toggle-mask
          autocomplete="new-password"
          required
          placeholder="Minimum 8 caractères"
          input-class="w-full"
          class="w-full"
        />
      </div>
      <div class="field">
        <label for="confirm-password">Confirmer le mot de passe</label>
        <Password
          id="confirm-password"
          v-model="confirmPassword"
          :feedback="false"
          toggle-mask
          autocomplete="new-password"
          required
          placeholder="Retapez le mot de passe"
          input-class="w-full"
          class="w-full"
        />
      </div>
      <Button
        type="submit"
        label="Enregistrer"
        icon="pi pi-check"
        :loading="submitting"
        class="w-full submit-button"
      />
    </form>

    <Button
      v-else
      label="Se connecter"
      icon="pi pi-sign-in"
      class="w-full submit-button"
      @click="router.push('/connexion')"
    />

    <p v-if="!message" class="auth-switch">
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
.w-full :deep(.p-inputtext),
.w-full :deep(.p-password),
.w-full :deep(.p-password-input) {
  width: 100%;
}

.field :deep(.p-inputtext),
.field :deep(.p-password-input) {
  min-height: 2.875rem;
}

.submit-button :deep(.p-button) {
  min-height: 3rem;
  font-weight: 700;
}
</style>
