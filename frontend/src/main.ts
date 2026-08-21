import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import { AntiGouminPreset } from './theme/preset'

import '@/assets/main.css'

async function bootstrap() {
  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)
  app.use(PrimeVue, {
    // Clé de licence PrimeUI (Community ou Commercial) à obtenir sur primeui.dev.
    // Sans clé valide, PrimeVue affiche un bandeau « Invalid PrimeUI License ».
    license: import.meta.env.VITE_PRIMEVUE_LICENSE_KEY,
    theme: {
      preset: AntiGouminPreset,
      options: {
        prefix: 'p',
        darkModeSelector: false,
      },
    },
  })
  app.use(ToastService)
  app.use(router)

  const auth = useAuthStore()
  await auth.initialize()

  app.mount('#app')
}

bootstrap()
