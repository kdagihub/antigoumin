import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/connexion',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/inscription',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { guest: true },
    },
    {
      path: '/profil',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/verifier-email/:token',
      name: 'verify-email',
      component: () => import('@/views/VerifyEmailView.vue'),
    },
    {
      path: '/verifier-telephone',
      name: 'verify-phone',
      component: () => import('@/views/VerifyPhoneView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/contact',
      name: 'contact',
      component: () => import('@/views/ContactView.vue'),
    },
    {
      path: '/v/:token',
      name: 'verify',
      component: () => import('@/views/VerifyPlaceholderView.vue'),
    },
    {
      path: '/transparence/:token',
      name: 'transparency-request',
      component: () => import('@/views/TransparencyRequestView.vue'),
    },
    {
      path: '/paiement/succes',
      name: 'payment-success',
      component: () => import('@/views/PaymentSuccessView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/paiement/erreur',
      name: 'payment-error',
      component: () => import('@/views/PaymentErrorView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/confidentialite',
      name: 'privacy',
      component: () => import('@/views/PrivacyView.vue'),
    },
    {
      path: '/cgu',
      name: 'cgu',
      component: () => import('@/views/CguView.vue'),
    },
  ],
  scrollBehavior(to) {
    if (to.hash) {
      return { el: to.hash, top: 88, behavior: 'smooth' }
    }
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (!auth.initialized) {
    await auth.initialize()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.guest && auth.isAuthenticated) {
    return { name: 'profile' }
  }

  return true
})

export default router
