<script setup lang="ts">
import Button from 'primevue/button'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Tag from 'primevue/tag'
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { redirectToGeniusPay } from '@/api/checkout'
import { ApiError } from '@/api/client'
import {
  createDeclaration,
  endDeclaration,
  fetchDeclarations,
  fetchPartnerPreview,
  type Declaration,
  type DeclarationVisibility,
  type RelationType,
} from '@/api/declarations'
import { fetchCheckoutStatus, fetchUnusedPayment } from '@/api/payments'
import DeclarationLoader from '@/components/DeclarationLoader.vue'
import IvorianPhoneInput from '@/components/IvorianPhoneInput.vue'
import {
  declarationRelationCopy,
  declarationsPageCopy,
  declarationStatusCopy,
  declarationVisibilityCopy,
} from '@/content/declarationsCopy'
import DashboardShell from '@/layouts/DashboardShell.vue'
import { useAuthStore } from '@/stores/auth'
import { downloadDeclarationPdf } from '@/utils/moduleReceipts'
import { formatIvorianLocalDisplay, isValidIvorianLocalPhone, toIvorianLocalDigits } from '@/utils/ivorianPhone'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const declarations = ref<Declaration[]>([])
const loadingList = ref(true)
const paymentId = ref<number | null>(null)
const paying = ref(false)
const submitting = ref(false)
const endingId = ref<number | null>(null)
const downloadingPdfId = ref<number | null>(null)
const error = ref('')
const success = ref('')
const previewNotice = ref('')
const allianceNotice = ref('')

const partnerPhone = ref('')
const partnerName = ref('')
const partnerPhoto = ref<File | null>(null)
const partnerPhotoPreview = ref('')
const relationType = ref<RelationType>('AMOUR')
const visibility = ref<DeclarationVisibility>('PUBLIC_CERTIFIED')

const relationTypes = Object.entries(declarationRelationCopy) as [
  RelationType,
  (typeof declarationRelationCopy)[RelationType],
][]

const visibilityOptions = Object.entries(declarationVisibilityCopy) as [
  DeclarationVisibility,
  (typeof declarationVisibilityCopy)[DeclarationVisibility],
][]

const canCreate = computed(() => Boolean(paymentId.value) || import.meta.env.DEV)
const showForm = computed(() => canCreate.value && auth.isFullyVerified)

async function exportDeclarationPdf(item: Declaration) {
  downloadingPdfId.value = item.id
  try {
    await downloadDeclarationPdf(item)
  } finally {
    downloadingPdfId.value = null
  }
}

async function loadDeclarations() {
  loadingList.value = true
  try {
    const result = await fetchDeclarations()
    declarations.value = result.items
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Chargement impossible.'
  } finally {
    loadingList.value = false
  }
}

async function resolvePayment() {
  const reference = typeof route.query.reference === 'string' ? route.query.reference : ''
  if (reference) {
    try {
      const status = await fetchCheckoutStatus(reference)
      if (status.payment_id) {
        paymentId.value = status.payment_id
        success.value = declarationsPageCopy.paymentSuccess
      }
    } catch {
      // Le formulaire reste bloqué sans paiement valide.
    }
    await router.replace({
      path: '/app/declarations',
      query: route.query.phone ? { phone: String(route.query.phone) } : {},
    })
    return
  }
  try {
    const unused = await fetchUnusedPayment('DECLARATION')
    paymentId.value = unused.payment_id
  } catch {
    paymentId.value = null
  }
}

async function previewPartner() {
  previewNotice.value = ''
  allianceNotice.value = ''
  if (!isValidIvorianLocalPhone(partnerPhone.value)) return
  try {
    const preview = await fetchPartnerPreview(partnerPhone.value)
    previewNotice.value = preview.consent_notice
    allianceNotice.value = preview.partner_alliance_notice
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Aperçu indisponible.'
  }
}

function onPhotoChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0] ?? null
  partnerPhoto.value = file
  if (partnerPhotoPreview.value) URL.revokeObjectURL(partnerPhotoPreview.value)
  partnerPhotoPreview.value = file ? URL.createObjectURL(file) : ''
}

async function payDeclaration() {
  paying.value = true
  error.value = ''
  try {
    await redirectToGeniusPay({ service_type: 'DECLARATION' })
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Paiement impossible.'
    paying.value = false
  }
}

async function submitDeclaration() {
  error.value = ''
  success.value = ''
  if (!partnerPhoto.value) {
    error.value = 'Ajoutez une photo de votre moitié pour personnaliser l’invitation.'
    return
  }
  if (!isValidIvorianLocalPhone(partnerPhone.value)) {
    error.value = 'Saisissez un numéro mobile ivoirien valide (10 chiffres).'
    return
  }
  submitting.value = true
  try {
    await createDeclaration({
      partner_phone: partnerPhone.value.trim(),
      partner_name: partnerName.value.trim(),
      partner_photo: partnerPhoto.value,
      relation_type: relationType.value,
      visibility: visibility.value,
      payment_id: paymentId.value ?? undefined,
    })
    success.value = declarationsPageCopy.sendSuccess
    partnerName.value = ''
    partnerPhoto.value = null
    if (partnerPhotoPreview.value) URL.revokeObjectURL(partnerPhotoPreview.value)
    partnerPhotoPreview.value = ''
    paymentId.value = null
    await loadDeclarations()
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Envoi impossible.'
  } finally {
    submitting.value = false
  }
}

async function terminateDeclaration(declaration: Declaration) {
  if (!window.confirm(declarationsPageCopy.endConfirm)) return
  endingId.value = declaration.id
  error.value = ''
  try {
    const result = await endDeclaration(declaration.id)
    success.value = result.message
    await loadDeclarations()
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Action impossible.'
  } finally {
    endingId.value = null
  }
}

function relationLabel(type: RelationType) {
  return declarationRelationCopy[type]?.label ?? type
}

function visibilityLabel(value: DeclarationVisibility) {
  return value === 'PUBLIC_CERTIFIED' ? 'Visible' : 'Privée'
}

onMounted(async () => {
  if (typeof route.query.phone === 'string') {
    partnerPhone.value = toIvorianLocalDigits(route.query.phone)
    await previewPartner()
  }
  await Promise.all([loadDeclarations(), resolvePayment()])
})
</script>

<template>
  <DashboardShell>
    <header class="declarations-hero">
      <div class="declarations-hero__glow" aria-hidden="true" />
      <div class="declarations-hero__content">
        <div class="declarations-hero__icon" aria-hidden="true">💕</div>
        <div class="declarations-hero__text">
          <p class="declarations-hero__eyebrow">{{ declarationsPageCopy.eyebrow }}</p>
          <h1 class="declarations-hero__title font-display">{{ declarationsPageCopy.title }}</h1>
          <p class="declarations-hero__subtitle">{{ declarationsPageCopy.subtitle }}</p>
        </div>
        <Tag :value="declarationsPageCopy.priceTag" severity="info" class="declarations-hero__tag" />
      </div>
    </header>

    <Message v-if="!auth.isFullyVerified" severity="warn" :closable="false" class="mb-3">
      Confirmez votre email ou votre téléphone depuis
      <RouterLink to="/app/profil">Mon profil</RouterLink>
      pour déclarer votre amour.
    </Message>

    <Message v-if="error" severity="error" :closable="false" class="mb-3">{{ error }}</Message>
    <Message v-if="success" severity="success" :closable="false" class="mb-3">
      {{ success }}
    </Message>

    <section v-if="!canCreate && auth.isFullyVerified" class="declarations-page__section">
      <Card class="declarations-card declarations-card--pay">
        <template #content>
          <div class="declarations-card__head">
            <span class="declarations-card__emoji" aria-hidden="true">💌</span>
            <div>
              <h2 class="declarations-card__title font-display">{{ declarationsPageCopy.payTitle }}</h2>
              <p class="declarations-card__body">{{ declarationsPageCopy.payBody }}</p>
            </div>
          </div>
          <Button
            :label="declarationsPageCopy.payCta"
            icon="pi pi-heart"
            class="declarations-card__cta"
            :loading="paying"
            @click="payDeclaration"
          />
        </template>
      </Card>
    </section>

    <section v-if="showForm" class="declarations-page__section">
      <Card class="declarations-card declarations-card--form">
        <template #content>
          <div class="declarations-card__head">
            <span class="declarations-card__emoji" aria-hidden="true">✨</span>
            <div>
              <h2 class="declarations-card__title font-display">{{ declarationsPageCopy.formTitle }}</h2>
              <p v-if="paymentId" class="declarations-card__body">{{ declarationsPageCopy.formHint }}</p>
            </div>
          </div>

          <form class="declarations-form" @submit.prevent="submitDeclaration">
            <label class="declarations-form__field">
              <span>{{ declarationsPageCopy.partnerPhoneLabel }}</span>
              <IvorianPhoneInput
                id="declaration-partner-phone"
                v-model="partnerPhone"
                aria-label="Numéro mobile ivoirien du partenaire"
                @blur="previewPartner"
              />
            </label>
            <p v-if="previewNotice" class="declarations-form__notice">{{ previewNotice }}</p>
            <Message v-if="allianceNotice" severity="warn" :closable="false" class="mt-3">
              {{ allianceNotice }}
            </Message>

            <label class="declarations-form__field">
              <span>{{ declarationsPageCopy.partnerNameLabel }}</span>
              <InputText
                v-model="partnerName"
                required
                :placeholder="declarationsPageCopy.partnerNamePlaceholder"
              />
            </label>

            <div class="declarations-form__field">
              <span>{{ declarationsPageCopy.partnerPhotoLabel }}</span>
              <label class="declarations-photo-upload">
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  required
                  class="declarations-photo-upload__input"
                  @change="onPhotoChange"
                />
                <span v-if="partnerPhotoPreview" class="declarations-photo-upload__preview">
                  <img :src="partnerPhotoPreview" alt="Aperçu photo partenaire" />
                </span>
                <span v-else class="declarations-photo-upload__placeholder">
                  <i class="pi pi-camera" aria-hidden="true" />
                  Choisir une photo
                </span>
              </label>
              <small>{{ declarationsPageCopy.partnerPhotoHint }}</small>
            </div>

            <fieldset class="declarations-form__fieldset">
              <legend>{{ declarationsPageCopy.relationLabel }}</legend>
              <div class="declarations-pills">
                <button
                  v-for="[value, meta] in relationTypes"
                  :key="value"
                  type="button"
                  class="declarations-pill"
                  :class="{ 'declarations-pill--active': relationType === value }"
                  @click="relationType = value"
                >
                  <span aria-hidden="true">{{ meta.emoji }}</span>
                  {{ meta.label }}
                </button>
              </div>
            </fieldset>

            <fieldset class="declarations-form__fieldset">
              <legend>{{ declarationsPageCopy.visibilityLabel }}</legend>
              <div class="declarations-visibility">
                <button
                  v-for="[value, meta] in visibilityOptions"
                  :key="value"
                  type="button"
                  class="declarations-visibility__option"
                  :class="{ 'declarations-visibility__option--active': visibility === value }"
                  @click="visibility = value"
                >
                  <span class="declarations-visibility__icon" aria-hidden="true">
                    {{ meta.icon === 'public' ? '🌍' : '🔒' }}
                  </span>
                  <span class="declarations-visibility__label">{{ meta.label }}</span>
                  <span class="declarations-visibility__hint">{{ meta.hint }}</span>
                </button>
              </div>
            </fieldset>

            <Button
              type="submit"
              :label="declarationsPageCopy.submitLabel"
              icon="pi pi-send"
              :loading="submitting"
              class="declarations-form__submit"
            />
          </form>
        </template>
      </Card>
    </section>

    <section class="declarations-page__section">
      <h2 class="declarations-page__history-title font-display">{{ declarationsPageCopy.historyTitle }}</h2>
      <DeclarationLoader v-if="loadingList" />
      <div v-else-if="!declarations.length" class="declarations-empty">
        <span class="declarations-empty__emoji" aria-hidden="true">💑</span>
        <p>{{ declarationsPageCopy.historyEmpty }}</p>
      </div>
      <div v-else class="declarations-list">
        <Card
          v-for="item in declarations"
          :key="item.id"
          class="declarations-list__card"
        >
          <template #content>
            <div class="declarations-list__head">
              <div class="declarations-list__photo">
                <img
                  v-if="item.partner_photo"
                  :src="item.partner_photo"
                  :alt="`Photo de ${item.partner_name}`"
                />
                <span v-else aria-hidden="true">💕</span>
              </div>
              <div class="declarations-list__info">
                <h3>{{ item.partner_name }}</h3>
                <p>{{ formatIvorianLocalDisplay(item.partner_phone) }}</p>
                <Tag
                  :value="declarationStatusCopy[item.status].label"
                  :severity="declarationStatusCopy[item.status].severity"
                />
              </div>
            </div>
            <p class="declarations-list__meta">
              {{ relationLabel(item.relation_type) }} ·
              {{ visibilityLabel(item.visibility) }} ·
              {{ new Date(item.created_at).toLocaleDateString('fr-CI') }}
            </p>
            <div class="declarations-list__actions">
              <Button
                label="Télécharger en PDF"
                icon="pi pi-download"
                severity="secondary"
                text
                size="small"
                :loading="downloadingPdfId === item.id"
                @click="exportDeclarationPdf(item)"
              />
              <Button
                v-if="item.status === 'VERIFIED'"
                label="Mettre fin à la relation"
                severity="secondary"
                text
                size="small"
                :loading="endingId === item.id"
                @click="terminateDeclaration(item)"
              />
            </div>
          </template>
        </Card>
      </div>
    </section>
  </DashboardShell>
</template>

<style scoped>
.declarations-hero {
  position: relative;
  margin-bottom: 1.25rem;
  border-radius: 1.25rem;
  overflow: hidden;
  background: linear-gradient(
    135deg,
    #fff1f5 0%,
    #ffffff 45%,
    #fdf2f8 100%
  );
  border: 1px solid rgb(237 20 125 / 0.12);
}

.declarations-hero__glow {
  position: absolute;
  top: -3rem;
  right: -2rem;
  width: 10rem;
  height: 10rem;
  border-radius: 50%;
  background: radial-gradient(circle, rgb(237 20 125 / 0.18) 0%, transparent 70%);
  pointer-events: none;
}

.declarations-hero__content {
  position: relative;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem 1.375rem;
}

.declarations-hero__icon {
  font-size: 2rem;
  line-height: 1;
  filter: drop-shadow(0 4px 8px rgb(237 20 125 / 0.2));
}

.declarations-hero__text {
  flex: 1 1 14rem;
  min-width: 0;
}

.declarations-hero__eyebrow {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-primary);
}

.declarations-hero__title {
  margin: 0.25rem 0 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-ink);
}

.declarations-hero__subtitle {
  margin: 0.5rem 0 0;
  color: var(--color-muted);
  line-height: 1.6;
  max-width: 40rem;
}

.declarations-hero__tag :deep(.p-tag) {
  background: rgb(237 20 125 / 0.1);
  color: var(--color-primary);
}

.declarations-page__section {
  margin-bottom: 1.5rem;
}

.declarations-card :deep(.p-card-body) {
  padding: 0;
}

.declarations-card :deep(.p-card-content) {
  padding: 1.25rem;
}

.declarations-card--pay,
.declarations-card--form {
  border: 1px solid rgb(237 20 125 / 0.14);
  box-shadow: 0 8px 24px rgb(237 20 125 / 0.06);
}

.declarations-card__head {
  display: flex;
  gap: 0.875rem;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.declarations-card__emoji {
  font-size: 1.75rem;
  line-height: 1;
}

.declarations-card__title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 800;
  color: var(--color-ink);
}

.declarations-card__body {
  margin: 0.375rem 0 0;
  color: var(--color-muted);
  line-height: 1.6;
}

.declarations-card__cta :deep(.p-button-label) {
  font-weight: 800;
  letter-spacing: 0.04em;
}

.declarations-form {
  display: grid;
  gap: 1.125rem;
}

.declarations-form__field {
  display: grid;
  gap: 0.375rem;
}

.declarations-form__field span,
.declarations-form__fieldset legend {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-ink);
}

.declarations-form__field small {
  color: var(--color-muted);
  font-size: 0.8125rem;
  line-height: 1.45;
}

.declarations-form__notice {
  margin: 0;
  padding: 0.75rem 0.875rem;
  border-radius: 0.75rem;
  background: #fff7ed;
  color: #9a3412;
  font-size: 0.875rem;
  line-height: 1.55;
}

.declarations-form__fieldset {
  margin: 0;
  padding: 0;
  border: 0;
  display: grid;
  gap: 0.625rem;
}

.declarations-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.declarations-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: #fff;
  color: var(--color-ink);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition:
    border-color 0.15s ease,
    background 0.15s ease,
    transform 0.15s ease;
}

.declarations-pill:hover {
  border-color: rgb(237 20 125 / 0.35);
}

.declarations-pill--active {
  border-color: var(--color-primary);
  background: rgb(237 20 125 / 0.08);
  color: var(--color-primary);
  transform: translateY(-1px);
}

.declarations-visibility {
  display: grid;
  gap: 0.625rem;
}

@media (min-width: 640px) {
  .declarations-visibility {
    grid-template-columns: 1fr 1fr;
  }
}

.declarations-visibility__option {
  display: grid;
  gap: 0.25rem;
  padding: 0.875rem;
  border-radius: 0.875rem;
  border: 1px solid var(--color-border);
  background: #fff;
  text-align: left;
  cursor: pointer;
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease;
}

.declarations-visibility__option:hover {
  border-color: rgb(237 20 125 / 0.3);
}

.declarations-visibility__option--active {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgb(237 20 125 / 0.12);
  background: rgb(237 20 125 / 0.04);
}

.declarations-visibility__icon {
  font-size: 1.25rem;
}

.declarations-visibility__label {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--color-ink);
}

.declarations-visibility__hint {
  font-size: 0.8125rem;
  color: var(--color-muted);
  line-height: 1.45;
}

.declarations-photo-upload {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 7rem;
  border-radius: 0.875rem;
  border: 2px dashed rgb(237 20 125 / 0.28);
  background: rgb(237 20 125 / 0.03);
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.15s ease;
}

.declarations-photo-upload:hover {
  border-color: rgb(237 20 125 / 0.5);
}

.declarations-photo-upload__input {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.declarations-photo-upload__placeholder {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-primary);
  font-weight: 700;
  font-size: 0.9375rem;
}

.declarations-photo-upload__preview {
  display: block;
  width: 100%;
  height: 7rem;
}

.declarations-photo-upload__preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.declarations-form__submit :deep(.p-button) {
  width: 100%;
  justify-content: center;
}

.declarations-page__history-title {
  margin: 0 0 0.875rem;
  font-size: 1.125rem;
  font-weight: 800;
  color: var(--color-ink);
}

.declarations-empty {
  display: grid;
  justify-items: center;
  gap: 0.625rem;
  padding: 2rem 1rem;
  border-radius: 1rem;
  border: 1px dashed rgb(237 20 125 / 0.2);
  background: rgb(237 20 125 / 0.03);
  text-align: center;
}

.declarations-empty__emoji {
  font-size: 2rem;
}

.declarations-empty p {
  margin: 0;
  max-width: 22rem;
  color: var(--color-muted);
  line-height: 1.6;
}

.declarations-list {
  display: grid;
  gap: 0.875rem;
}

.declarations-list__card {
  border: 1px solid rgb(237 20 125 / 0.1);
  transition: box-shadow 0.2s ease;
}

.declarations-list__card:hover {
  box-shadow: 0 6px 20px rgb(237 20 125 / 0.08);
}

.declarations-list__head {
  display: flex;
  gap: 0.875rem;
  align-items: flex-start;
}

.declarations-list__photo {
  width: 4rem;
  height: 4rem;
  border-radius: 1rem;
  overflow: hidden;
  background: linear-gradient(135deg, #fff1f5, #fce7f3);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1.5rem;
}

.declarations-list__photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.declarations-list__info h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 800;
  color: var(--color-ink);
}

.declarations-list__info p {
  margin: 0.125rem 0 0.5rem;
  color: var(--color-muted);
  font-size: 0.875rem;
}

.declarations-list__meta {
  margin: 0.75rem 0 0;
  color: var(--color-muted);
  font-size: 0.8125rem;
  line-height: 1.5;
}

.declarations-list__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-top: 0.5rem;
}

.mb-3 {
  margin-bottom: 0.75rem;
}
</style>
