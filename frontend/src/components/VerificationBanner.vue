<script setup lang="ts">
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import { computed, ref } from 'vue'

import { ApiError } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const emailMessage = ref('')
const emailError = ref('')
const sendingEmail = ref(false)
const otpCode = ref('')
const otpMessage = ref('')
const otpError = ref('')
const sendingOtp = ref(false)
const verifyingOtp = ref(false)

const needsEmail = computed(() => Boolean(auth.user && !auth.user.email_verified))
const needsPhone = computed(() => Boolean(auth.user && !auth.user.phone_verified))
const visible = computed(() => Boolean(auth.user && !auth.isFullyVerified))

async function resendEmail() {
  emailError.value = ''
  emailMessage.value = ''
  sendingEmail.value = true
  try {
    const result = await auth.resendEmailVerification()
    emailMessage.value = result.message
  } catch (err) {
    emailError.value = err instanceof ApiError ? err.message : 'Envoi impossible.'
  } finally {
    sendingEmail.value = false
  }
}

async function sendOtp() {
  otpError.value = ''
  otpMessage.value = ''
  sendingOtp.value = true
  try {
    const result = await auth.sendPhoneOtp()
    otpMessage.value = result.message
  } catch (err) {
    otpError.value = err instanceof ApiError ? err.message : 'Envoi du SMS impossible.'
  } finally {
    sendingOtp.value = false
  }
}

async function confirmOtp() {
  otpError.value = ''
  otpMessage.value = ''
  verifyingOtp.value = true
  try {
    await auth.verifyPhone(otpCode.value.trim())
    otpMessage.value = 'Téléphone vérifié.'
    otpCode.value = ''
  } catch (err) {
    otpError.value = err instanceof ApiError ? err.message : 'Code incorrect.'
  } finally {
    verifyingOtp.value = false
  }
}
</script>

<template>
  <aside v-if="visible" class="verification-banner" role="status">
    <p class="verification-banner__title">
      Vérifiez votre email et votre téléphone avant d’utiliser les services.
    </p>
    <p class="verification-banner__hint">
      Pensez à consulter vos courriers indésirables si le mail n’apparaît pas.
    </p>

    <div v-if="needsEmail" class="verification-banner__block">
      <p>Email non confirmé ({{ auth.user?.email }}).</p>
      <Button
        label="Renvoyer le lien"
        size="small"
        :loading="sendingEmail"
        @click="resendEmail"
      />
      <Message v-if="emailMessage" severity="success" :closable="false">{{ emailMessage }}</Message>
      <Message v-if="emailError" severity="error" :closable="false">{{ emailError }}</Message>
    </div>

    <div v-if="needsPhone" class="verification-banner__block">
      <p>
        Téléphone {{ auth.user?.phone_number ? 'non confirmé' : 'manquant' }}
        <span v-if="auth.user?.phone_number">({{ auth.user.phone_number }})</span>.
      </p>
      <div class="verification-banner__otp">
        <InputText
          v-model="otpCode"
          inputmode="numeric"
          maxlength="6"
          placeholder="Code SMS"
          aria-label="Code de vérification téléphone"
        />
        <Button
          label="Valider"
          size="small"
          :loading="verifyingOtp"
          :disabled="otpCode.trim().length < 6"
          @click="confirmOtp"
        />
        <Button
          label="Renvoyer le SMS"
          size="small"
          severity="secondary"
          :loading="sendingOtp"
          :disabled="!auth.user?.phone_number"
          @click="sendOtp"
        />
      </div>
      <Message v-if="otpMessage" severity="success" :closable="false">{{ otpMessage }}</Message>
      <Message v-if="otpError" severity="error" :closable="false">{{ otpError }}</Message>
    </div>
  </aside>
</template>

<style scoped>
.verification-banner {
  margin-bottom: 1.25rem;
  border: 1px solid #f9a8d4;
  background: #fff1f7;
  border-radius: 1rem;
  padding: 1rem 1.1rem;
}

.verification-banner__title {
  margin: 0;
  font-weight: 800;
  color: #831843;
}

.verification-banner__hint,
.verification-banner__block p {
  margin: 0.35rem 0 0;
  color: #9d174d;
  font-size: 0.92rem;
}

.verification-banner__block {
  margin-top: 0.9rem;
  display: grid;
  gap: 0.55rem;
}

.verification-banner__otp {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}
</style>
