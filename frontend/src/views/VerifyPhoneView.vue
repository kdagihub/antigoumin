<script setup lang="ts">
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { ApiError } from '@/api/client'
import IvorianPhoneInput from '@/components/IvorianPhoneInput.vue'
import AppShell from '@/layouts/AppShell.vue'
import { useAuthStore } from '@/stores/auth'
import { isValidIvorianLocalPhone, toIvorianLocalDigits } from '@/utils/ivorianPhone'

const auth = useAuthStore()
const router = useRouter()
const phone = ref(toIvorianLocalDigits(auth.user?.phone_number ?? ''))
const code = ref('')
const error = ref('')
const message = ref('')
const savingPhone = ref(false)
const sending = ref(false)
const verifying = ref(false)

const needsPhone = computed(() => !auth.user?.phone_number)

async function savePhone() {
  error.value = ''
  if (!isValidIvorianLocalPhone(phone.value)) {
    error.value = 'Saisissez un numéro mobile ivoirien valide (10 chiffres).'
    return
  }
  savingPhone.value = true
  try {
    await auth.updatePhone(phone.value.trim())
    message.value = 'Numéro enregistré. Demandez maintenant le code SMS.'
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Numéro invalide.'
  } finally {
    savingPhone.value = false
  }
}

async function sendCode() {
  error.value = ''
  sending.value = true
  try {
    const result = await auth.sendPhoneOtp()
    message.value = result.message
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Envoi impossible.'
  } finally {
    sending.value = false
  }
}

async function confirm() {
  error.value = ''
  verifying.value = true
  try {
    await auth.verifyPhone(code.value.trim())
    await router.push('/profil')
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Code incorrect.'
  } finally {
    verifying.value = false
  }
}
</script>

<template>
  <AppShell>
    <h1>Vérifier votre téléphone</h1>
    <p>
      Le numéro est obligatoire. Un code SMS (et une copie email) confirme que
      c’est bien le vôtre.
    </p>

    <form v-if="needsPhone || !auth.user?.phone_verified" class="phone-form" @submit.prevent>
      <label class="field">
        <span>Numéro ivoirien</span>
        <IvorianPhoneInput v-model="phone" aria-label="Numéro mobile ivoirien" />
      </label>
      <Button
        v-if="needsPhone || toIvorianLocalDigits(phone) !== toIvorianLocalDigits(auth.user?.phone_number ?? '')"
        label="Enregistrer le numéro"
        :loading="savingPhone"
        @click="savePhone"
      />
      <label class="field">
        <span>Code SMS à 6 chiffres</span>
        <InputText v-model="code" inputmode="numeric" maxlength="6" />
      </label>
      <div class="actions">
        <Button
          label="Renvoyer le SMS"
          severity="secondary"
          :loading="sending"
          :disabled="!auth.user?.phone_number"
          @click="sendCode"
        />
        <Button
          label="Confirmer"
          :loading="verifying"
          :disabled="code.trim().length < 6"
          @click="confirm"
        />
      </div>
    </form>

    <Message v-if="message" severity="success" :closable="false">{{ message }}</Message>
    <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>
  </AppShell>
</template>

<style scoped>
.phone-form {
  display: grid;
  gap: 0.9rem;
  margin: 1.25rem 0;
}

.field {
  display: grid;
  gap: 0.35rem;
  font-weight: 700;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}
</style>
