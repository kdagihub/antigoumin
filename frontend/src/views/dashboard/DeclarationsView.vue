<script setup lang="ts">
import Button from 'primevue/button'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
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
import DashboardShell from '@/layouts/DashboardShell.vue'
import { useAuthStore } from '@/stores/auth'
import { downloadDeclarationPdf } from '@/utils/moduleReceipts'

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
const relationType = ref<RelationType>('AMOUR')
const visibility = ref<DeclarationVisibility>('PUBLIC_CERTIFIED')

const relationOptions = [
  { label: 'Amour', value: 'AMOUR' },
  { label: 'Flirt', value: 'FLIRT' },
  { label: 'Fiançailles', value: 'FIANCE' },
  { label: 'Mariage', value: 'MARIAGE' },
]

const visibilityOptions = [
  {
    label: 'Certifiée publique',
    value: 'PUBLIC_CERTIFIED',
    hint: 'Statut « En couple » consultable après acceptation du partenaire.',
  },
  {
    label: 'Privée',
    value: 'PRIVATE',
    hint: 'Relation confirmée sans statut public.',
  },
]

const canCreate = computed(() => Boolean(paymentId.value) || import.meta.env.DEV)
const showForm = computed(() => canCreate.value && auth.isFullyVerified)

const statusMeta: Record<
  Declaration['status'],
  { label: string; severity: 'success' | 'warn' | 'danger' | 'secondary' | 'info' }
> = {
  PENDING: { label: 'En attente du partenaire', severity: 'warn' },
  VERIFIED: { label: 'Relation certifiée', severity: 'success' },
  REJECTED: { label: 'Refusée', severity: 'danger' },
  ENDED: { label: 'Terminée', severity: 'secondary' },
}

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
        success.value = 'Paiement confirmé. Complétez votre déclaration ci-dessous.'
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
  const phone = partnerPhone.value.trim()
  if (phone.length < 8) return
  try {
    const preview = await fetchPartnerPreview(phone)
    previewNotice.value = preview.consent_notice
    allianceNotice.value = preview.partner_alliance_notice
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Aperçu indisponible.'
  }
}

function onPhotoChange(event: Event) {
  const input = event.target as HTMLInputElement
  partnerPhoto.value = input.files?.[0] ?? null
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
    error.value = 'Ajoutez une photo du partenaire.'
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
    success.value =
      'Déclaration envoyée. Votre partenaire recevra un SMS pour accepter ou refuser.'
    partnerName.value = ''
    partnerPhoto.value = null
    paymentId.value = null
    await loadDeclarations()
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Envoi impossible.'
  } finally {
    submitting.value = false
  }
}

async function terminateDeclaration(declaration: Declaration) {
  if (
    !window.confirm(
      'Mettre fin à cette relation certifiée sur AntiGoumin ? Cette action est définitive.',
    )
  ) {
    return
  }
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

onMounted(async () => {
  if (typeof route.query.phone === 'string') {
    partnerPhone.value = route.query.phone
    await previewPartner()
  }
  await Promise.all([loadDeclarations(), resolvePayment()])
})
</script>

<template>
  <DashboardShell>
    <header class="declarations-page__header">
      <div>
        <p class="declarations-page__eyebrow">Relations certifiées</p>
        <h1 class="declarations-page__title font-display">Mes déclarations</h1>
        <p class="declarations-page__subtitle">
          Déclarez une relation et invitez votre partenaire à confirmer. Même s’il n’est
          pas encore membre, il recevra un lien par SMS.
        </p>
      </div>
      <Tag value="300 FCFA / déclaration" severity="info" />
    </header>

    <Message v-if="!auth.isFullyVerified" severity="warn" :closable="false" class="mb-3">
      Vérifiez votre email ou votre téléphone depuis
      <RouterLink to="/app/profil">Mon profil</RouterLink>
      avant de déclarer une relation.
    </Message>

    <Message v-if="error" severity="error" :closable="false" class="mb-3">{{ error }}</Message>
    <Message v-if="success" severity="success" :closable="false" class="mb-3">
      {{ success }}
    </Message>

    <section v-if="!canCreate && auth.isFullyVerified" class="declarations-page__pay">
      <Card>
        <template #content>
          <h2 class="declarations-page__section-title font-display">Nouvelle déclaration</h2>
          <p>
            Payez 300 FCFA pour envoyer une invitation certifiée à votre partenaire par SMS.
          </p>
          <Button
            label="Payer 300 FCFA"
            icon="pi pi-credit-card"
            :loading="paying"
            @click="payDeclaration"
          />
        </template>
      </Card>
    </section>

    <section v-if="showForm" class="declarations-page__form-section">
      <Card>
        <template #content>
          <h2 class="declarations-page__section-title font-display">Nouvelle déclaration</h2>
          <p v-if="paymentId" class="declarations-page__hint">
            Paiement validé — complétez le formulaire pour envoyer l’invitation.
          </p>
          <form class="declarations-page__form" @submit.prevent="submitDeclaration">
            <label class="declarations-page__field">
              <span>Téléphone du partenaire</span>
              <InputText
                v-model="partnerPhone"
                type="tel"
                inputmode="tel"
                required
                placeholder="Ex. 07 00 00 00 00"
                @blur="previewPartner"
              />
            </label>
            <p v-if="previewNotice" class="declarations-page__notice">{{ previewNotice }}</p>
            <Message v-if="allianceNotice" severity="warn" :closable="false" class="mt-3">
              {{ allianceNotice }}
            </Message>

            <label class="declarations-page__field">
              <span>Prénom ou surnom du partenaire</span>
              <InputText v-model="partnerName" required placeholder="Prénom affiché dans l’invitation" />
            </label>

            <label class="declarations-page__field">
              <span>Photo du partenaire</span>
              <input type="file" accept="image/jpeg,image/png,image/webp" required @change="onPhotoChange" />
            </label>

            <label class="declarations-page__field">
              <span>Type de relation</span>
              <Select
                v-model="relationType"
                :options="relationOptions"
                option-label="label"
                option-value="value"
                class="w-full"
              />
            </label>

            <label class="declarations-page__field">
              <span>Visibilité</span>
              <Select
                v-model="visibility"
                :options="visibilityOptions"
                option-label="label"
                option-value="value"
                class="w-full"
              />
              <small>
                {{
                  visibilityOptions.find((option) => option.value === visibility)?.hint
                }}
              </small>
            </label>

            <Button
              type="submit"
              label="Envoyer l’invitation"
              icon="pi pi-send"
              :loading="submitting"
              class="declarations-page__submit"
            />
          </form>
        </template>
      </Card>
    </section>

    <section class="declarations-page__list">
      <h2 class="declarations-page__section-title font-display">Historique</h2>
      <p v-if="loadingList">Chargement…</p>
      <p v-else-if="!declarations.length" class="declarations-page__empty">
        Aucune déclaration pour le moment.
      </p>
      <div v-else class="declarations-page__cards">
        <Card v-for="item in declarations" :key="item.id">
          <template #content>
            <div class="declarations-page__card-head">
              <div class="declarations-page__card-photo">
                <img
                  v-if="item.partner_photo"
                  :src="item.partner_photo"
                  :alt="`Photo de ${item.partner_name}`"
                />
                <i v-else class="pi pi-user" aria-hidden="true" />
              </div>
              <div>
                <h3>{{ item.partner_name }}</h3>
                <p>{{ item.partner_phone }}</p>
                <Tag
                  :value="statusMeta[item.status].label"
                  :severity="statusMeta[item.status].severity"
                />
              </div>
            </div>
            <p class="declarations-page__meta">
              {{ item.relation_type }} ·
              {{ item.visibility === 'PUBLIC_CERTIFIED' ? 'Publique' : 'Privée' }} ·
              {{ new Date(item.created_at).toLocaleDateString('fr-CI') }}
            </p>
            <div class="declarations-page__card-actions">
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
.declarations-page__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.declarations-page__eyebrow {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.declarations-page__title {
  margin: 0.25rem 0 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-ink);
}

.declarations-page__subtitle {
  margin: 0.5rem 0 0;
  color: var(--color-muted);
  line-height: 1.55;
  max-width: 40rem;
}

.declarations-page__section-title {
  margin: 0 0 0.75rem;
  font-size: 1.125rem;
  font-weight: 800;
  color: var(--color-ink);
}

.declarations-page__hint,
.declarations-page__notice,
.declarations-page__empty,
.declarations-page__meta {
  color: var(--color-muted);
  line-height: 1.55;
}

.declarations-page__form-section,
.declarations-page__pay,
.declarations-page__list {
  margin-bottom: 1.5rem;
}

.declarations-page__form {
  display: grid;
  gap: 1rem;
}

.declarations-page__field {
  display: grid;
  gap: 0.375rem;
}

.declarations-page__field span {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-ink);
}

.declarations-page__field small {
  color: var(--color-muted);
  font-size: 0.8125rem;
}

.declarations-page__submit :deep(.p-button) {
  width: 100%;
  justify-content: center;
}

.declarations-page__cards {
  display: grid;
  gap: 0.875rem;
}

.declarations-page__card-head {
  display: flex;
  gap: 0.875rem;
  align-items: flex-start;
}

.declarations-page__card-photo {
  width: 4rem;
  height: 4rem;
  border-radius: 1rem;
  overflow: hidden;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.declarations-page__card-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.declarations-page__card-head h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 800;
  color: var(--color-ink);
}

.declarations-page__card-head p {
  margin: 0.125rem 0 0.5rem;
  color: var(--color-muted);
  font-size: 0.875rem;
}

.declarations-page__card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-top: 0.5rem;
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.w-full {
  width: 100%;
}
</style>
