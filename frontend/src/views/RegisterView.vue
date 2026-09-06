<script setup lang="ts">
import Button from 'primevue/button'
import Divider from 'primevue/divider'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Password from 'primevue/password'
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { ApiError } from '@/api/client'
import GoogleSignIn from '@/components/GoogleSignIn.vue'
import IvorianPhoneInput from '@/components/IvorianPhoneInput.vue'
import LegalAcceptanceCheckbox from '@/components/legal/LegalAcceptanceCheckbox.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'
import { postAuthPath, useAuthStore } from '@/stores/auth'
import { isValidIvorianLocalPhone } from '@/utils/ivorianPhone'

const auth = useAuthStore()
const router = useRouter()

const firstName = ref('')
const lastName = ref('')
const email = ref('')
const phoneNumber = ref('')
const password = ref('')
const acceptedLegal = ref(false)
const error = ref('')
const submitting = ref(false)

async function handleSubmit() {
  error.value = ''

  if (!acceptedLegal.value) {
    error.value = 'Vous devez accepter les CGU et la Politique de confidentialité.'
    return
  }

  if (!isValidIvorianLocalPhone(phoneNumber.value)) {
    error.value = 'Saisissez un numéro mobile ivoirien valide (10 chiffres, ex. 07 00 00 00 00).'
    return
  }

  submitting.value = true

  try {
    await auth.register({
      email: email.value.trim(),
      password: password.value,
      first_name: firstName.value.trim(),
      last_name: lastName.value.trim(),
      phone_number: phoneNumber.value.trim(),
    })
    await router.push({ path: '/app', query: { welcome: '1' } })
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Inscription impossible.'
  } finally {
    submitting.value = false
  }
}

async function handleGoogle(idToken: string) {
  error.value = ''

  if (!acceptedLegal.value) {
    error.value = 'Vous devez accepter les CGU et la Politique de confidentialité.'
    return
  }

  submitting.value = true

  try {
    await auth.loginWithGoogle(idToken)
    await router.push(postAuthPath(auth.user))
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Connexion Google impossible.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AuthLayout
    title="Inscription"
    subtitle="Créez votre compte pour déclarer une relation."
    :highlights="[
      'Votre déclaration reste privée jusqu’à la validation de votre partenaire',
      'Vous choisissez si votre statut devient consultable',
      'Vous pouvez retirer votre consentement à tout moment',
    ]"
  >
    <Message v-if="error" severity="error" :closable="false" class="form-message">
      {{ error }}
    </Message>

    <form class="auth-form" @submit.prevent="handleSubmit">
      <div class="field-row">
        <div class="field">
          <label for="register-first-name">Prénom</label>
          <InputText
            id="register-first-name"
            v-model="firstName"
            autocomplete="given-name"
            placeholder="Prénom"
            class="w-full"
          />
        </div>
        <div class="field">
          <label for="register-last-name">Nom</label>
          <InputText
            id="register-last-name"
            v-model="lastName"
            autocomplete="family-name"
            placeholder="Nom"
            class="w-full"
          />
        </div>
      </div>

      <div class="field">
        <label for="register-email">Adresse email</label>
        <InputText
          id="register-email"
          v-model="email"
          type="email"
          autocomplete="email"
          required
          placeholder="vous@exemple.com"
          class="w-full"
        />
      </div>

      <div class="field">
        <label for="register-phone">Numéro de téléphone</label>
        <IvorianPhoneInput
          id="register-phone"
          v-model="phoneNumber"
          aria-label="Numéro mobile ivoirien"
        />
        <small>
          Obligatoire pour sécuriser votre compte (Côte d’Ivoire, +225). Après inscription,
          un email de confirmation et un code SMS vous seront envoyés — l’un des deux suffit
          pour activer les services. Pensez à vérifier vos courriers indésirables si le
          mail n’apparaît pas.
        </small>
      </div>

      <div class="field">
        <label for="register-password">Mot de passe</label>
        <Password
          id="register-password"
          v-model="password"
          toggle-mask
          autocomplete="new-password"
          required
          placeholder="Minimum 8 caractères"
          input-class="w-full"
          class="w-full"
        />
      </div>

      <LegalAcceptanceCheckbox v-model="acceptedLegal" />

      <Button
        type="submit"
        label="Créer mon compte"
        icon="pi pi-user-plus"
        :loading="submitting"
        :disabled="!acceptedLegal"
        class="w-full submit-button"
      />
    </form>

    <Divider align="center" type="solid"> ou </Divider>

    <GoogleSignIn
      :disabled="!acceptedLegal"
      label="Continuer avec Google"
      @success="handleGoogle"
      @error="(msg) => (error = msg)"
    />

    <p class="auth-switch">
      Déjà inscrit ?
      <RouterLink to="/connexion">Se connecter</RouterLink>
    </p>
  </AuthLayout>
</template>

<style scoped>
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.125rem;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.125rem;
}

@media (min-width: 480px) {
  .field-row {
    grid-template-columns: 1fr 1fr;
    gap: 0.875rem;
  }
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

.field small {
  font-size: 0.75rem;
  line-height: 1.45;
  color: var(--color-muted);
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
