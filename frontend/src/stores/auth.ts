import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import * as authApi from '@/api/auth'
import { getStoredToken, setStoredToken } from '@/api/client'
import * as verificationApi from '@/api/verification'
import type { LoginPayload, RegisterPayload, User } from '@/types/user'

export function postAuthPath(sessionUser: User | null | undefined): string {
  if (!sessionUser) return '/connexion'
  if (!sessionUser.phone_number || !sessionUser.phone_verified) {
    return '/verifier-telephone'
  }
  return '/profil'
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(getStoredToken())
  const loading = ref(false)
  const initialized = ref(false)

  const isAuthenticated = computed(() => Boolean(token.value && user.value))
  const isFullyVerified = computed(() => Boolean(user.value?.is_fully_verified))
  const hasActiveSubscription = computed(() => {
    if (!user.value?.subscription_end_date) return false
    return new Date(user.value.subscription_end_date) > new Date()
  })

  function applySession(accessToken: string, sessionUser: User) {
    token.value = accessToken
    user.value = sessionUser
    setStoredToken(accessToken)
  }

  function clearSession() {
    token.value = null
    user.value = null
    setStoredToken(null)
  }

  async function initialize() {
    if (initialized.value) return

    if (!token.value) {
      initialized.value = true
      return
    }

    loading.value = true
    try {
      user.value = await authApi.fetchMe()
    } catch {
      clearSession()
    } finally {
      loading.value = false
      initialized.value = true
    }
  }

  async function register(payload: RegisterPayload) {
    loading.value = true
    try {
      const response = await authApi.register(payload)
      applySession(response.access_token, response.user)
      return response
    } finally {
      loading.value = false
    }
  }

  async function login(payload: LoginPayload) {
    loading.value = true
    try {
      const response = await authApi.login(payload)
      applySession(response.access_token, response.user)
      return response
    } finally {
      loading.value = false
    }
  }

  async function loginWithGoogle(idToken: string) {
    loading.value = true
    try {
      const response = await authApi.loginWithGoogle({ id_token: idToken })
      applySession(response.access_token, response.user)
      return response
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    if (!token.value) return null
    user.value = await authApi.fetchMe()
    return user.value
  }

  async function setStatusVisibility(isStatusSearchable: boolean) {
    user.value = await authApi.updateStatusVisibility(isStatusSearchable)
    return user.value
  }

  async function resendEmailVerification() {
    return verificationApi.resendEmailVerification()
  }

  async function sendPhoneOtp() {
    return verificationApi.sendPhoneOtp()
  }

  async function verifyPhone(code: string) {
    user.value = await verificationApi.verifyPhoneOtp(code)
    return user.value
  }

  async function verifyEmailToken(tokenValue: string) {
    const verified = await verificationApi.verifyEmailToken(tokenValue)
    if (user.value && user.value.id === verified.id) {
      user.value = verified
    }
    return verified
  }

  async function updatePhone(phoneNumber: string) {
    user.value = await verificationApi.updatePhone(phoneNumber)
    return user.value
  }

  function logout() {
    clearSession()
  }

  return {
    user,
    token,
    loading,
    initialized,
    isAuthenticated,
    isFullyVerified,
    hasActiveSubscription,
    initialize,
    register,
    login,
    loginWithGoogle,
    fetchMe,
    setStatusVisibility,
    resendEmailVerification,
    sendPhoneOtp,
    verifyPhone,
    verifyEmailToken,
    updatePhone,
    logout,
  }
})
