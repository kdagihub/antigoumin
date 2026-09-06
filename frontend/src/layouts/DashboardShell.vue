<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import BrandMark from '@/components/BrandMark.vue'
import DashboardUserMenu from '@/components/DashboardUserMenu.vue'
import AllianceRingsIcon from '@/components/icons/AllianceRingsIcon.vue'
import DashboardTutorial from '@/components/onboarding/DashboardTutorial.vue'
import OnboardingWizard from '@/components/onboarding/OnboardingWizard.vue'
import PwaInstallButton from '@/components/PwaInstallButton.vue'
import {
  markTutorialCompleted,
  markWizardCompleted,
  shouldShowTutorial,
  shouldShowWizard,
} from '@/composables/useOnboarding'
import { dashboardAccountLinks, dashboardModuleNavItems } from '@/config/dashboardNav'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()

const showWizard = ref(false)
const showTutorial = ref(false)

const displayName = computed(() => {
  if (!auth.user) return ''
  const full = `${auth.user.first_name} ${auth.user.last_name}`.trim()
  return full || auth.user.email.split('@')[0]
})

function isActive(path: string): boolean {
  if (path === '/app') {
    return route.path === '/app'
  }
  return route.path.startsWith(path)
}

function openTutorialIfNeeded() {
  if (route.path !== '/app' || !auth.user) return
  if (!shouldShowTutorial(auth.user.id)) return
  window.setTimeout(() => {
    if (route.path === '/app') {
      showTutorial.value = true
    }
  }, 450)
}

function onWizardFinished() {
  if (!auth.user) return
  markWizardCompleted(auth.user.id)
  openTutorialIfNeeded()
}

function onTutorialFinished() {
  if (!auth.user) return
  markTutorialCompleted(auth.user.id)
}

onMounted(() => {
  if (auth.user && shouldShowWizard(auth.user.id)) {
    showWizard.value = true
    return
  }
  openTutorialIfNeeded()
})

watch(
  () => [route.path, auth.user?.id] as const,
  () => {
    if (showWizard.value) return
    openTutorialIfNeeded()
  },
)
</script>

<template>
  <div class="dashboard">
    <aside class="dashboard__sidebar" aria-label="Navigation des modules">
      <RouterLink to="/app" class="dashboard__brand">
        <BrandMark size="sm" />
        <span class="dashboard__brand-name font-display">AntiGoumin</span>
      </RouterLink>

      <div v-if="auth.user" class="dashboard__user">
        <div class="dashboard__avatar" aria-hidden="true">
          <i class="pi pi-user" />
        </div>
        <div class="dashboard__user-meta">
          <p class="dashboard__user-name">{{ displayName }}</p>
          <p class="dashboard__user-email">{{ auth.user.email }}</p>
        </div>
      </div>

      <nav class="dashboard__nav" data-tutorial="dashboard-nav-desktop">
        <RouterLink
          v-for="item in dashboardModuleNavItems"
          :key="item.to"
          :to="item.to"
          class="dashboard__nav-link"
          :class="{ 'dashboard__nav-link--active': isActive(item.to) }"
        >
          <AllianceRingsIcon
            v-if="item.customIcon === 'alliance-rings'"
            class="dashboard__nav-svg"
          />
          <i v-else :class="item.icon" aria-hidden="true" />
          <span>{{ item.label }}</span>
        </RouterLink>

        <div class="dashboard__nav-divider" aria-hidden="true" />

        <RouterLink
          v-for="item in dashboardAccountLinks"
          :key="item.to"
          :to="item.to"
          class="dashboard__nav-link"
          :class="{
            'dashboard__nav-link--active': isActive(item.to),
            'dashboard__nav-link--premium': item.to === '/app/abonnement',
          }"
          :data-tutorial="item.to === '/app/abonnement' ? 'dashboard-premium-desktop' : undefined"
        >
          <i :class="item.icon" aria-hidden="true" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <div class="dashboard__sidebar-footer">
        <PwaInstallButton variant="sidebar" />
        <RouterLink to="/" class="dashboard__back-link">
          <i class="pi pi-arrow-left" aria-hidden="true" />
          Retour au site
        </RouterLink>
      </div>
    </aside>

    <div class="dashboard__body">
      <header class="dashboard__topbar">
        <RouterLink to="/app" class="dashboard__topbar-brand">
          <BrandMark size="sm" />
        </RouterLink>

        <div class="dashboard__topbar-actions">
          <PwaInstallButton variant="icon" />
          <RouterLink
            to="/app/abonnement"
            class="dashboard__premium-chip"
            :class="{ 'dashboard__premium-chip--active': auth.hasActiveSubscription }"
            data-tutorial="dashboard-premium-mobile"
          >
            <i class="pi pi-star-fill" aria-hidden="true" />
            <span class="dashboard__premium-chip-text">
              {{ auth.hasActiveSubscription ? 'Premium actif' : 'Passer Premium' }}
            </span>
          </RouterLink>
          <RouterLink
            v-if="auth.user && !auth.isFullyVerified"
            to="/app/profil"
            class="dashboard__verify-chip"
          >
            <i class="pi pi-exclamation-circle" aria-hidden="true" />
            <span class="dashboard__verify-chip-text">Vérifier le compte</span>
          </RouterLink>
          <DashboardUserMenu compact />
        </div>
      </header>

      <main class="dashboard__main">
        <slot />
      </main>
    </div>

    <nav class="dashboard__bottom-nav" aria-label="Navigation mobile" data-tutorial="dashboard-nav-mobile">
      <template v-for="item in dashboardModuleNavItems" :key="`mobile-${item.to}`">
        <RouterLink
          v-if="item.mobileFab"
          :to="item.to"
          class="dashboard__bottom-fab"
          :class="{ 'dashboard__bottom-fab--active': isActive(item.to) }"
          :aria-label="item.label"
        >
          <span class="dashboard__bottom-fab-bubble" aria-hidden="true">
            <i :class="item.icon" />
          </span>
          <span class="dashboard__bottom-fab-label">{{ item.shortLabel ?? item.label }}</span>
        </RouterLink>
        <RouterLink
          v-else
          :to="item.to"
          class="dashboard__bottom-link"
          :class="{ 'dashboard__bottom-link--active': isActive(item.to) }"
        >
          <AllianceRingsIcon
            v-if="item.customIcon === 'alliance-rings'"
            class="dashboard__bottom-svg"
          />
          <i v-else :class="item.icon" aria-hidden="true" />
          <span>{{ item.shortLabel ?? item.label }}</span>
        </RouterLink>
      </template>
    </nav>

    <OnboardingWizard
      v-model:visible="showWizard"
      @complete="onWizardFinished"
      @skip="onWizardFinished"
    />
    <DashboardTutorial
      v-model:visible="showTutorial"
      @complete="onTutorialFinished"
      @skip="onTutorialFinished"
    />
  </div>
</template>

<style scoped>
.dashboard {
  min-height: 100dvh;
  display: flex;
  background: #f8fafc;
}

.dashboard__sidebar {
  display: none;
  width: 17.5rem;
  flex-shrink: 0;
  flex-direction: column;
  border-right: 1px solid var(--color-border);
  background: #fff;
  padding: 1.25rem 1rem;
}

.dashboard__brand {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  text-decoration: none;
  color: var(--color-ink);
  padding: 0.25rem 0.5rem;
  margin-bottom: 1.5rem;
}

.dashboard__brand-name {
  font-size: 1.125rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.dashboard__user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem;
  margin-bottom: 1rem;
  border-radius: 1rem;
  background: #f8fafc;
  border: 1px solid var(--color-border);
}

.dashboard__avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 999px;
  background: var(--color-accent-soft);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.dashboard__user-name {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-ink);
  margin: 0;
}

.dashboard__user-email {
  font-size: 0.75rem;
  color: var(--color-muted);
  margin: 0.125rem 0 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 10rem;
}

.dashboard__nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.dashboard__nav-link {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem 0.875rem;
  border-radius: 0.75rem;
  text-decoration: none;
  color: var(--color-muted);
  font-size: 0.9375rem;
  font-weight: 600;
  transition: background-color 0.15s, color 0.15s;
}

.dashboard__nav-link:hover {
  background: #f1f5f9;
  color: var(--color-ink);
}

.dashboard__nav-link--active {
  background: var(--color-accent-soft);
  color: #be123c;
}

.dashboard__nav-link--premium {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border: 1px solid #fbbf24;
  color: #92400e;
  box-shadow: 0 2px 8px rgb(251 191 36 / 0.2);
}

.dashboard__nav-link--premium:hover {
  background: linear-gradient(135deg, #fde68a 0%, #fcd34d 100%);
  color: #78350f;
}

.dashboard__nav-link--premium.dashboard__nav-link--active {
  background: linear-gradient(135deg, #fde68a 0%, #fbbf24 100%);
  color: #78350f;
}

.dashboard__nav-svg {
  width: 1.125rem;
  height: 1.125rem;
  flex-shrink: 0;
}

.dashboard__nav-divider {
  height: 1px;
  margin: 0.75rem 0.5rem;
  background: var(--color-border);
}

.dashboard__sidebar-footer {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.dashboard__back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-muted);
  text-decoration: none;
}

.dashboard__back-link:hover {
  color: var(--color-primary);
}

.dashboard__body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding-bottom: calc(5.5rem + env(safe-area-inset-bottom));
}

.dashboard__topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  background: #fff;
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 20;
}

.dashboard__topbar-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: var(--color-ink);
  font-weight: 800;
  font-size: 1rem;
  min-width: 0;
}

.dashboard__topbar-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.dashboard__premium-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.75rem;
  border-radius: 999px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border: 1px solid #fbbf24;
  color: #92400e;
  font-size: 0.6875rem;
  font-weight: 800;
  text-decoration: none;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgb(251 191 36 / 0.25);
}

.dashboard__premium-chip--active {
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border-color: #34d399;
  color: #047857;
  box-shadow: 0 2px 8px rgb(52 211 153 / 0.2);
}

.dashboard__premium-chip i {
  font-size: 0.75rem;
}

@media (max-width: 380px) {
  .dashboard__premium-chip-text {
    max-width: 5.5rem;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

@media (min-width: 1024px) {
  .dashboard__premium-chip {
    display: none;
  }
}

.dashboard__verify-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  border-radius: 999px;
  background: #fff1f2;
  border: 1px solid #fecdd3;
  color: #be123c;
  font-size: 0.75rem;
  font-weight: 700;
  text-decoration: none;
}

.dashboard__verify-chip-text {
  max-width: 7rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dashboard__main {
  flex: 1;
  padding: 1rem;
  width: 100%;
  max-width: 56rem;
  margin: 0 auto;
}

.dashboard__bottom-nav {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 30;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  align-items: end;
  gap: 0;
  background: #fff;
  border-top: 1px solid var(--color-border);
  padding: 0.25rem 0.35rem calc(0.5rem + env(safe-area-inset-bottom));
  box-shadow: 0 -4px 24px rgb(15 23 42 / 0.06);
}

.dashboard__bottom-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  gap: 0.2rem;
  min-height: 3rem;
  padding: 0.35rem 0.15rem 0.15rem;
  text-decoration: none;
  color: var(--color-muted);
  font-size: 0.625rem;
  font-weight: 700;
  line-height: 1.1;
  text-align: center;
}

.dashboard__bottom-link span {
  max-width: 4.25rem;
  font-size: 0.5625rem;
  line-height: 1.15;
}

.dashboard__bottom-link i {
  font-size: 1.125rem;
}

.dashboard__bottom-svg {
  width: 1.25rem;
  height: 1.25rem;
}

.dashboard__bottom-link--active {
  color: var(--color-primary);
}

.dashboard__bottom-fab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  gap: 0.3rem;
  margin-top: -1.35rem;
  padding-bottom: 0.1rem;
  text-decoration: none;
  color: var(--color-primary);
}

.dashboard__bottom-fab-bubble {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3.65rem;
  height: 3.65rem;
  border-radius: 999px;
  background: linear-gradient(145deg, #ff4d94 0%, #ed147d 52%, #c41068 100%);
  color: #fff;
  box-shadow:
    0 10px 24px rgb(237 20 125 / 0.42),
    0 0 0 4px #fff,
    0 0 0 5px rgb(237 20 125 / 0.12);
  transition:
    transform 0.15s ease,
    box-shadow 0.15s ease;
}

.dashboard__bottom-fab-bubble i {
  font-size: 1.55rem;
}

.dashboard__bottom-fab:active .dashboard__bottom-fab-bubble {
  transform: scale(0.94);
}

.dashboard__bottom-fab--active .dashboard__bottom-fab-bubble {
  box-shadow:
    0 12px 28px rgb(237 20 125 / 0.5),
    0 0 0 4px #fff,
    0 0 0 6px rgb(237 20 125 / 0.22);
  transform: scale(1.04);
}

.dashboard__bottom-fab-label {
  font-size: 0.5625rem;
  font-weight: 800;
  line-height: 1.15;
  color: var(--color-primary);
  max-width: 4.25rem;
  text-align: center;
}

@media (max-width: 380px) {
  .dashboard__verify-chip-text {
    display: none;
  }
}

@media (min-width: 1024px) {
  .dashboard__sidebar {
    display: flex;
  }

  .dashboard__topbar {
    display: none;
  }

  .dashboard__body {
    padding-bottom: 0;
  }

  .dashboard__bottom-nav {
    display: none;
  }

  .dashboard__main {
    padding: 1.75rem 2rem 2.5rem;
  }
}
</style>
