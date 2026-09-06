import { computed, onMounted, onUnmounted, ref } from 'vue'

type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

function isIosDevice() {
  return /iphone|ipad|ipod/i.test(navigator.userAgent)
}

function isStandaloneDisplay() {
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    (navigator as Navigator & { standalone?: boolean }).standalone === true
  )
}

export function usePwaInstall() {
  const deferredPrompt = ref<BeforeInstallPromptEvent | null>(null)
  const isStandalone = ref(isStandaloneDisplay())
  const isIos = ref(isIosDevice())
  const updateMessage = ref('')
  const checkingUpdate = ref(false)

  function onBeforeInstallPrompt(event: Event) {
    event.preventDefault()
    deferredPrompt.value = event as BeforeInstallPromptEvent
  }

  function onAppInstalled() {
    deferredPrompt.value = null
    isStandalone.value = true
  }

  async function installApp() {
    updateMessage.value = ''
    if (deferredPrompt.value) {
      await deferredPrompt.value.prompt()
      const choice = await deferredPrompt.value.userChoice
      if (choice.outcome === 'accepted') {
        deferredPrompt.value = null
      }
      return
    }

    if (isIos.value && !isStandalone.value) {
      updateMessage.value =
        'Sur iPhone : touchez Partager, puis « Sur l’écran d’accueil » pour installer AntiGoumin.'
      return
    }

    updateMessage.value =
      'Si l’installation n’apparaît pas, ouvrez le menu du navigateur (⋮) puis « Installer l’application » ou « Ajouter à l’écran d’accueil ».'
  }

  async function checkForUpdates() {
    updateMessage.value = ''
    checkingUpdate.value = true
    try {
      if (!('serviceWorker' in navigator)) {
        updateMessage.value = 'Les mises à jour automatiques ne sont pas disponibles ici.'
        return
      }
      const registration = await navigator.serviceWorker.getRegistration()
      if (!registration) {
        updateMessage.value = 'Rechargez la page pour récupérer la dernière version.'
        return
      }
      await registration.update()
      updateMessage.value = registration.waiting
        ? 'Une mise à jour est prête. Fermez puis rouvrez l’application.'
        : 'Vous utilisez la dernière version disponible.'
    } catch {
      updateMessage.value = 'Impossible de vérifier la mise à jour pour le moment.'
    } finally {
      checkingUpdate.value = false
    }
  }

  async function handlePrimaryAction() {
    if (isStandalone.value) {
      await checkForUpdates()
      return
    }
    await installApp()
  }

  const buttonLabel = computed(() => {
    if (isStandalone.value) return 'Mettre à jour l’app'
    if (deferredPrompt.value || isIos.value) return 'Installer l’application'
    return 'Installer l’application'
  })

  const buttonHint = computed(() => {
    if (isStandalone.value) {
      return 'Vérifiez qu’AntiGoumin est à jour après un déploiement.'
    }
    return 'Accédez à AntiGoumin depuis votre écran d’accueil, même hors navigateur.'
  })

  const showInstallButton = computed(() => !isStandalone.value)

  onMounted(() => {
    window.addEventListener('beforeinstallprompt', onBeforeInstallPrompt)
    window.addEventListener('appinstalled', onAppInstalled)
  })

  onUnmounted(() => {
    window.removeEventListener('beforeinstallprompt', onBeforeInstallPrompt)
    window.removeEventListener('appinstalled', onAppInstalled)
  })

  return {
    buttonLabel,
    buttonHint,
    updateMessage,
    checkingUpdate,
    isStandalone,
    showInstallButton,
    handlePrimaryAction,
  }
}
