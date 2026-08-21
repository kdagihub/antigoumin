<script setup lang="ts">
import Button from 'primevue/button'
import Divider from 'primevue/divider'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Password from 'primevue/password'
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { ApiError } from '@/api/client'
import GoogleSignIn from '@/components/GoogleSignIn.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'
import { postAuthPath, useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const email = ref('')
const password = ref('')
const error = ref('')
const submitting = ref(false)

async function handleSubmit() {
  error.value = ''
  submitting.value = true

  try {
    await auth.login({ email: email.value.trim(), password: password.value })
    const redirect =
      typeof route.query.redirect === 'string' ? route.query.redirect : postAuthPath(auth.user)
    await router.push(auth.isFullyVerified ? redirect : postAuthPath(auth.user))
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Connexion impossible.'
  } finally {
    submitting.value = false
  }
}

async function handleGoogle(idToken: string) {
  error.value = ''
  submitting.value = true

  try {
    await auth.loginWithGoogle(idToken)
    const redirect =
      typeof route.query.redirect === 'string' ? route.query.redirect : postAuthPath(auth.user)
    await router.push(auth.isFullyVerified ? redirect : postAuthPath(auth.user))
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Connexion Google impossible.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AuthLayout title="Connexion" subtitle="Accédez à votre espace AntiGoumin.">
    <Message v-if="error" severity="error" :closable="false" class="form-message">
      {{ error }}
    </Message>

    <form class="auth-form" @submit.prevent="handleSubmit">
      <div class="field">
        <label for="login-email">Adresse email</label>
        <InputText
          id="login-email"
          v-model="email"
          type="email"
          autocomplete="email"
          required
          placeholder="vous@exemple.com"
          class="w-full"
        />
      </div>

      <div class="field">
        <label for="login-password">Mot de passe</label>
        <Password
          id="login-password"
          v-model="password"
          :feedback="false"
          toggle-mask
          autocomplete="current-password"
          required
          placeholder="Votre mot de passe"
          input-class="w-full"
          class="w-full"
        />
      </div>

      <Button
        type="submit"
        label="Se connecter"
        icon="pi pi-sign-in"
        :loading="submitting"
        class="w-full submit-button"
      />
    </form>

    <Divider align="center" type="solid"> ou </Divider>

    <GoogleSignIn @success="handleGoogle" @error="(msg) => (error = msg)" />

    <p class="auth-switch">
      Pas encore de compte ?
      <RouterLink to="/inscription">Créer un compte</RouterLink>
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
  color: var(--color-muted);
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

.submit-button :deep(.p-button),
.submit-button.p-button {
  min-height: 3rem;
  font-weight: 700;
}
</style>
