<script setup lang="ts">
import Button from 'primevue/button'
import Menu from 'primevue/menu'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { dashboardAccountLinks } from '@/config/dashboardNav'
import { useAuthStore } from '@/stores/auth'

defineProps<{
  compact?: boolean
}>()

const menu = ref<InstanceType<typeof Menu> | null>(null)
const router = useRouter()
const auth = useAuthStore()

const displayName = computed(() => {
  if (!auth.user) return 'Compte'
  const full = `${auth.user.first_name} ${auth.user.last_name}`.trim()
  return full || auth.user.email.split('@')[0]
})

const items = computed(() => [
  ...dashboardAccountLinks.map((link) => ({
    label: link.label,
    icon: link.icon,
    command: () => router.push(link.to),
  })),
  { separator: true },
  {
    label: 'Déconnexion',
    icon: 'pi pi-sign-out',
    command: () => {
      auth.logout()
      router.push('/')
    },
  },
])

function toggle(event: Event) {
  menu.value?.toggle(event)
}
</script>

<template>
  <div class="dashboard-user-menu">
    <Button
      type="button"
      class="dashboard-user-menu__trigger"
      :class="{ 'dashboard-user-menu__trigger--compact': compact }"
      rounded
      text
      aria-haspopup="true"
      aria-controls="dashboard-user-menu"
      :aria-label="`Menu compte — ${displayName}`"
      @click="toggle"
    >
      <span class="dashboard-user-menu__avatar" aria-hidden="true">
        <i class="pi pi-user" />
      </span>
      <span v-if="!compact" class="dashboard-user-menu__name">{{ displayName }}</span>
      <i class="pi pi-chevron-down dashboard-user-menu__chevron" aria-hidden="true" />
    </Button>
    <Menu
      id="dashboard-user-menu"
      ref="menu"
      :model="items"
      :popup="true"
      class="dashboard-user-menu__panel"
    />
  </div>
</template>

<style scoped>
.dashboard-user-menu {
  position: relative;
}

.dashboard-user-menu__trigger {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.375rem;
  color: var(--color-ink);
}

.dashboard-user-menu__trigger--compact {
  padding: 0.125rem;
}

.dashboard-user-menu__avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 999px;
  background: var(--color-accent-soft);
  color: var(--color-primary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.dashboard-user-menu__name {
  max-width: 7rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.8125rem;
  font-weight: 700;
}

.dashboard-user-menu__chevron {
  font-size: 0.75rem;
  color: var(--color-muted);
}

.dashboard-user-menu__trigger--compact .dashboard-user-menu__chevron {
  display: none;
}
</style>
