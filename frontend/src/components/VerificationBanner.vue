<script setup lang="ts">
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import { computed, ref } from 'vue'

import { ApiError } from '@/api/client'
import IvorianPhoneInput from '@/components/IvorianPhoneInput.vue'
import { useAuthStore } from '@/stores/auth'
import { isValidIvorianLocalPhone, toIvorianLocalDigits } from '@/utils/ivorianPhone'

const auth = useAuthStore()
const emailMessage = ref('')
const emailError = ref('')
const sendingEmail = ref(false)
const editingEmail = ref(false)
const correctedEmail = ref('')
const savingEmail = ref(false)
const otpCode = ref('')
const otpMessage = ref('')
const otpError = ref('')
const sendingOtp = ref(false)
const verifyingOtp = ref(false)
const otpSent = ref(false)
const editingPhone = ref(false)
const correctedPhone = ref('')
const savingPhone = ref(false)

const needsEmail = computed(() => Boolean(auth.user && !auth.user.email_verified))
const needsPhone = computed(() => Boolean(auth.user && !auth.user.phone_verified))
const canEditEmail = computed(() => auth.user?.auth_provider === 'email')
const visible = computed(() => Boolean(auth.user && !auth.isFullyVerified))

function startEmailEdit() {
  correctedEmail.value = auth.user?.email ?? ''
  editingEmail.value = true
  emailError.value = ''
  emailMessage.value = ''
}

async function saveEmail() {
  emailError.value = ''
  emailMessage.value = ''
  const nextEmail = correctedEmail.value.trim()
  if (!nextEmail) {
    emailError.value = 'Saisissez une adresse email valide.'
    return
  }
  savingEmail.value = true
  try {
    await auth.updateEmail(nextEmail)
    editingEmail.value = false
    emailMessage.value =
      'Adresse mise à jour. Un nouveau lien de confirmation vient d’être envoyé.'
  } catch (err) {
    emailError.value = err instanceof ApiError ? err.message : 'Modification impossible.'
  } finally {
    savingEmail.value = false
  }
}

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

function startPhoneEdit() {
  correctedPhone.value = toIvorianLocalDigits(auth.user?.phone_number ?? '')
  editingPhone.value = true
  otpSent.value = false
  otpCode.value = ''
  otpError.value = ''
  otpMessage.value = ''
}

async function savePhone() {
  otpError.value = ''
  otpMessage.value = ''
  const nextPhone = correctedPhone.value.trim()
  if (!isValidIvorianLocalPhone(nextPhone)) {
    otpError.value = 'Saisissez un numéro mobile ivoirien valide (10 chiffres).'
    return
  }
  savingPhone.value = true
  try {
    await auth.updatePhone(nextPhone)
    editingPhone.value = false
    otpSent.value = false
    otpMessage.value = 'Numéro mis à jour. Vous pouvez maintenant recevoir le code SMS.'
  } catch (err) {
    otpError.value = err instanceof ApiError ? err.message : 'Modification impossible.'
  } finally {
    savingPhone.value = false
  }
}

async function sendOtp() {
  otpError.value = ''
  otpMessage.value = ''
  sendingOtp.value = true
  try {
    const result = await auth.sendPhoneOtp()
    otpMessage.value = result.message
    otpSent.value = true
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
    otpMessage.value = 'Téléphone vérifié avec succès.'
    otpCode.value = ''
  } catch (err) {
    otpError.value = err instanceof ApiError ? err.message : 'Code incorrect.'
  } finally {
    verifyingOtp.value = false
  }
}
</script>

<template>
  <section v-if="visible" class="verification-card" aria-labelledby="verification-title">
    <header class="verification-card__header">
      <div class="verification-card__badge" aria-hidden="true">
        <i class="pi pi-shield" />
      </div>
      <div>
        <h2 id="verification-title" class="verification-card__title font-display">
          Vérifiez votre compte pour commencer
        </h2>
        <p class="verification-card__lead">
          Confirmez au moins votre email ou votre téléphone pour accéder aux
          déclarations, recherches et alliances.
        </p>
      </div>
    </header>

    <div class="verification-card__grid">
      <article v-if="needsEmail" class="verification-card__step">
        <div class="verification-card__step-head">
          <span class="verification-card__step-num">1</span>
          <div>
            <h3>Confirmer votre email</h3>
            <p>{{ auth.user?.email }}</p>
          </div>
        </div>
        <p class="verification-card__hint">
          Un lien de confirmation vous a été envoyé. Pensez aussi à vérifier vos
          courriers indésirables (spam). Cette étape suffit à débloquer les services.
        </p>

        <template v-if="editingEmail">
          <label class="verification-card__field">
            <span>Nouvelle adresse email</span>
            <InputText
              v-model="correctedEmail"
              type="email"
              inputmode="email"
              autocomplete="email"
              placeholder="votre@email.com"
              class="w-full"
            />
          </label>
          <div class="verification-card__actions">
            <Button
              label="Enregistrer et renvoyer le lien"
              icon="pi pi-check"
              :loading="savingEmail"
              @click="saveEmail"
            />
            <Button
              label="Annuler"
              severity="secondary"
              text
              :disabled="savingEmail"
              @click="editingEmail = false"
            />
          </div>
        </template>
        <template v-else>
          <Button
            v-if="canEditEmail"
            label="Corriger mon adresse email"
            icon="pi pi-pencil"
            severity="secondary"
            outlined
            class="verification-card__action"
            @click="startEmailEdit"
          />
          <Button
            label="Renvoyer l’email de confirmation"
            icon="pi pi-envelope"
            :loading="sendingEmail"
            class="verification-card__action"
            @click="resendEmail"
          />
        </template>
        <Message v-if="emailMessage" severity="success" :closable="false">
          {{ emailMessage }}
        </Message>
        <Message v-if="emailError" severity="error" :closable="false">
          {{ emailError }}
        </Message>
      </article>

      <article v-if="needsPhone" class="verification-card__step">
        <div class="verification-card__step-head">
          <span class="verification-card__step-num">{{ needsEmail ? '2' : '1' }}</span>
          <div>
            <h3>Confirmer votre téléphone</h3>
            <p>{{ auth.user?.phone_number || 'Numéro non renseigné' }}</p>
          </div>
        </div>

        <template v-if="editingPhone">
          <label class="verification-card__field">
            <span>Nouveau numéro de téléphone</span>
            <IvorianPhoneInput
              v-model="correctedPhone"
              aria-label="Numéro mobile ivoirien"
            />
          </label>
          <div class="verification-card__actions">
            <Button
              label="Enregistrer le numéro"
              icon="pi pi-check"
              :loading="savingPhone"
              @click="savePhone"
            />
            <Button
              label="Annuler"
              severity="secondary"
              text
              :disabled="savingPhone"
              @click="editingPhone = false"
            />
          </div>
        </template>

        <template v-else-if="!otpSent">
          <p class="verification-card__hint">
            Nous enverrons un code SMS à 6 chiffres. Une copie peut aussi arriver par email.
            Cette étape suffit à débloquer les services.
          </p>
          <Button
            label="Corriger mon numéro"
            icon="pi pi-pencil"
            severity="secondary"
            outlined
            class="verification-card__action"
            @click="startPhoneEdit"
          />
          <Button
            label="Recevoir le code SMS"
            icon="pi pi-mobile"
            :loading="sendingOtp"
            :disabled="!auth.user?.phone_number"
            class="verification-card__action"
            @click="sendOtp"
          />
        </template>

        <template v-else>
          <label class="verification-card__field">
            <span>Code reçu par SMS</span>
            <InputText
              v-model="otpCode"
              inputmode="numeric"
              maxlength="6"
              placeholder="000000"
              aria-label="Code de vérification téléphone"
            />
          </label>
          <div class="verification-card__actions">
            <Button
              label="Valider le code"
              icon="pi pi-check"
              :loading="verifyingOtp"
              :disabled="otpCode.trim().length < 6"
              @click="confirmOtp"
            />
            <Button
              label="Renvoyer le SMS"
              icon="pi pi-refresh"
              severity="secondary"
              :loading="sendingOtp"
              @click="sendOtp"
            />
          </div>
        </template>

        <Message v-if="otpMessage" severity="success" :closable="false">
          {{ otpMessage }}
        </Message>
        <Message v-if="otpError" severity="error" :closable="false">
          {{ otpError }}
        </Message>
      </article>
    </div>
  </section>
</template>

<style scoped>
.verification-card {
  margin-bottom: 1.5rem;
  border: 1px solid #fecdd3;
  border-radius: 1.25rem;
  background: linear-gradient(180deg, #fff7fb 0%, #ffffff 100%);
  padding: 1.25rem;
  box-shadow: 0 10px 30px rgba(237, 20, 125, 0.06);
}

.verification-card__header {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 1.25rem;
}

.verification-card__badge {
  width: 3rem;
  height: 3rem;
  border-radius: 1rem;
  background: var(--color-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.verification-card__title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 800;
  color: var(--color-ink);
}

.verification-card__lead {
  margin: 0.375rem 0 0;
  color: var(--color-muted);
  font-size: 0.9375rem;
  line-height: 1.5;
}

.verification-card__grid {
  display: grid;
  gap: 1rem;
}

@media (min-width: 768px) {
  .verification-card__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.verification-card__step {
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  background: #fff;
  padding: 1rem;
  display: grid;
  gap: 0.75rem;
}

.verification-card__step-head {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.verification-card__step-num {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 999px;
  background: var(--color-accent-soft);
  color: #be123c;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8125rem;
  font-weight: 800;
  flex-shrink: 0;
}

.verification-card__step h3 {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 800;
  color: var(--color-ink);
}

.verification-card__step p {
  margin: 0.2rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-muted);
}

.verification-card__hint {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.5;
  color: var(--color-muted);
}

.verification-card__field {
  display: grid;
  gap: 0.375rem;
}

.verification-card__field span {
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--color-ink);
}

.verification-card__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.verification-card__action :deep(.p-button) {
  width: 100%;
  justify-content: center;
}

.w-full {
  width: 100%;
}
</style>
