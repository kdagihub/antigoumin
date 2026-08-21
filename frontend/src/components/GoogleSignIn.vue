<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

const emit = defineEmits<{
  success: [idToken: string]
  error: [message: string]
}>()

const props = withDefaults(
  defineProps<{
    disabled?: boolean
    /** Texte du bouton — « Se connecter » sur login, « Continuer » à l'inscription */
    label?: string
  }>(),
  {
    label: 'Se connecter avec Google',
  },
)

const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
const loading = ref(false)
const scriptReady = ref(false)
const hiddenContainer = ref<HTMLDivElement | null>(null)

interface GoogleCredentialResponse {
  credential: string
}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string
            callback: (response: GoogleCredentialResponse) => void
            locale?: string
          }) => void
          renderButton: (
            parent: HTMLElement,
            options: Record<string, string | number>,
          ) => void
        }
      }
    }
  }
}

let scriptEl: HTMLScriptElement | null = null

function handleCredential(response: GoogleCredentialResponse) {
  loading.value = false
  emit('success', response.credential)
}

function initGoogle() {
  if (!clientId || !window.google?.accounts?.id) return
  window.google.accounts.id.initialize({
    client_id: clientId,
    callback: handleCredential,
    locale: 'fr',
  })
  scriptReady.value = true
}

function loadScript() {
  if (!clientId) return

  if (window.google?.accounts?.id) {
    initGoogle()
    return
  }

  scriptEl = document.createElement('script')
  scriptEl.src = 'https://accounts.google.com/gsi/client'
  scriptEl.async = true
  scriptEl.defer = true
  scriptEl.onload = () => initGoogle()
  scriptEl.onerror = () => emit('error', 'Impossible de charger la connexion Google.')
  document.head.appendChild(scriptEl)
}

function triggerSignIn() {
  if (!scriptReady.value || !hiddenContainer.value || !window.google?.accounts?.id) {
    emit('error', 'Connexion Google indisponible. Réessayez dans un instant.')
    return
  }

  loading.value = true
  hiddenContainer.value.innerHTML = ''
  window.google.accounts.id.renderButton(hiddenContainer.value, {
    theme: 'outline',
    size: 'large',
    type: 'standard',
    shape: 'pill',
    text: 'continue_with',
    locale: 'fr',
    width: 320,
  })

  const googleButton = hiddenContainer.value.querySelector('[role="button"]') as HTMLElement | null
  if (googleButton) {
    googleButton.click()
  } else {
    loading.value = false
    emit('error', 'Impossible d’ouvrir la fenêtre de connexion Google.')
  }
}

onMounted(() => {
  loadScript()
})

onUnmounted(() => {
  scriptEl?.remove()
})
</script>

<template>
  <div class="google-signin">
    <div v-if="!clientId" class="google-signin__fallback">
      <p>Connexion Google non configurée.</p>
    </div>
    <button
      v-else
      type="button"
      class="google-signin__btn"
      :disabled="disabled || loading || !scriptReady"
      :aria-busy="loading"
      :aria-label="label"
      @click="triggerSignIn"
    >
      <svg class="google-signin__icon" viewBox="0 0 24 24" aria-hidden="true">
        <path
          fill="#4285F4"
          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        />
        <path
          fill="#34A853"
          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        />
        <path
          fill="#FBBC05"
          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
        />
        <path
          fill="#EA4335"
          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        />
      </svg>
      <span class="google-signin__label">{{ loading ? 'Connexion…' : label }}</span>
    </button>
    <div ref="hiddenContainer" class="google-signin__hidden" aria-hidden="true" />
  </div>
</template>

<style scoped>
.google-signin {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  width: 100%;
}

.google-signin__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  width: 100%;
  min-height: 2.75rem;
  padding: 0.625rem 1.25rem;
  border: 1px solid #dadce0;
  border-radius: 9999px;
  background: #ffffff;
  color: #1f1f1f;
  font-size: 0.9375rem;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: background-color 0.15s ease, box-shadow 0.15s ease;
}

.google-signin__btn:hover:not(:disabled) {
  background: #f8f9fa;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.google-signin__btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.google-signin__btn:focus-visible {
  outline: 2px solid #ed147d;
  outline-offset: 2px;
}

.google-signin__icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.google-signin__label {
  white-space: nowrap;
}

.google-signin__hidden {
  position: absolute;
  width: 0;
  height: 0;
  overflow: hidden;
  opacity: 0;
  pointer-events: none;
}

.google-signin__fallback {
  width: 100%;
  text-align: center;
  padding: 0.75rem;
  border: 1px dashed #cbd5e1;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  color: #64748b;
}
</style>
