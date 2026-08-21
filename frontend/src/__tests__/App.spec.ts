import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { createRouter, createMemoryHistory } from 'vue-router'

import App from '../App.vue'
import { useAuthStore } from '../stores/auth'

vi.mock('@/api/auth', () => ({
  fetchMe: vi.fn(),
}))

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', name: 'home', component: { template: '<div>Accueil</div>' } },
    { path: '/connexion', name: 'login', component: { template: '<div>Connexion</div>' } },
  ],
})

describe('App', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('affiche le contenu une fois initialisé', async () => {
    const auth = useAuthStore()
    auth.initialized = true

    const wrapper = mount(App, {
      global: {
        plugins: [router, PrimeVue],
      },
    })

    await router.isReady()
    expect(wrapper.text()).toContain('Accueil')
  })
})
