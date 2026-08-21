<script setup lang="ts">
import Button from 'primevue/button'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Textarea from 'primevue/textarea'
import { ref } from 'vue'

import { submitContact, type ContactDestination } from '@/api/contact'
import { ApiError } from '@/api/client'
import LegalShell from '@/layouts/LegalShell.vue'

const destinations = [
  { label: 'Contact général (contact@antigoumin.live)', value: 'contact' },
  { label: 'Confidentialité (privacy@antigoumin.live)', value: 'privacy' },
]

const name = ref('')
const email = ref('')
const destination = ref<ContactDestination>('contact')
const message = ref('')
const website = ref('')
const error = ref('')
const success = ref('')
const submitting = ref(false)

async function handleSubmit() {
  error.value = ''
  success.value = ''
  submitting.value = true
  try {
    const result = await submitContact({
      name: name.value.trim(),
      email: email.value.trim(),
      destination: destination.value,
      message: message.value.trim(),
      website: website.value,
    })
    success.value = result.message
    message.value = ''
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Envoi impossible.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <LegalShell>
    <h1>Contact</h1>
    <p>
      Écrivez à l’équipe AntiGoumin. Choisissez
      <strong>contact@antigoumin.live</strong> pour une question générale, ou
      <strong>privacy@antigoumin.live</strong> pour une demande relative à vos
      données.
    </p>

    <form class="contact-form" @submit.prevent="handleSubmit">
      <label class="hp" aria-hidden="true">
        Site web
        <input v-model="website" tabindex="-1" autocomplete="off" />
      </label>
      <label>
        Nom
        <InputText v-model="name" required minlength="2" />
      </label>
      <label>
        Email
        <InputText v-model="email" type="email" required />
      </label>
      <label>
        Destinataire
        <Select v-model="destination" :options="destinations" option-label="label" option-value="value" />
      </label>
      <label>
        Message
        <Textarea v-model="message" rows="6" required minlength="10" />
      </label>
      <Button type="submit" label="Envoyer" :loading="submitting" />
    </form>

    <Message v-if="success" class="mt-4" severity="success" :closable="false">{{ success }}</Message>
    <Message v-if="error" class="mt-4" severity="error" :closable="false">{{ error }}</Message>
  </LegalShell>
</template>

<style scoped>
.contact-form {
  display: grid;
  gap: 1rem;
  max-width: 36rem;
  margin-top: 1.5rem;
}

.contact-form label {
  display: grid;
  gap: 0.4rem;
  font-weight: 700;
}

.hp {
  position: absolute;
  left: -9999px;
  height: 0;
  overflow: hidden;
}
</style>
