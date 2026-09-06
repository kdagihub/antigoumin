<script setup lang="ts">
import { usePwaInstall } from '@/composables/usePwaInstall'

withDefaults(
  defineProps<{
    variant?: 'icon' | 'chip' | 'sidebar' | 'header'
  }>(),
  { variant: 'icon' },
)

const {
  buttonLabel,
  buttonHint,
  updateMessage,
  checkingUpdate,
  showInstallButton,
  handlePrimaryAction,
} = usePwaInstall()
</script>

<template>
  <div v-if="showInstallButton" class="pwa-install" :class="`pwa-install--${variant}`">
    <button
      type="button"
      class="pwa-install__button"
      :class="{
        'pwa-install__button--icon-only': variant === 'icon' || variant === 'header',
      }"
      :disabled="checkingUpdate"
      :aria-label="buttonLabel"
      :title="buttonLabel"
      @click="handlePrimaryAction"
    >
      <i class="pi pi-mobile" aria-hidden="true" />
      <span
        v-if="variant === 'sidebar' || variant === 'header'"
        class="pwa-install__label"
      >
        {{ checkingUpdate ? 'Vérification…' : 'Télécharger l’application' }}
      </span>
    </button>
    <p v-if="updateMessage" class="pwa-install__message" role="status">{{ updateMessage }}</p>
    <p v-if="variant === 'sidebar' && !updateMessage" class="pwa-install__hint">{{ buttonHint }}</p>
  </div>
</template>

<style scoped>
.pwa-install--icon {
  display: inline-flex;
}

.pwa-install--sidebar {
  margin-top: 0.75rem;
}

.pwa-install__button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
  border: 0;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: #fff;
  font-weight: 800;
  cursor: pointer;
  transition: transform 0.15s ease;
}

.pwa-install__button--icon-only {
  width: 2.125rem;
  height: 2.125rem;
  padding: 0;
  border-radius: 999px;
  flex-shrink: 0;
}

.pwa-install__button--icon-only .pi-mobile {
  font-size: 0.875rem;
}

.pwa-install--header {
  display: inline-flex;
}

.pwa-install--header .pwa-install__button {
  box-shadow: 0 4px 12px rgb(37 99 235 / 0.2);
}

@media (min-width: 1024px) {
  .pwa-install--header .pwa-install__button--icon-only {
    width: auto;
    height: auto;
    padding: 0.5rem 0.875rem;
    border-radius: 0.75rem;
    gap: 0.4rem;
  }

  .pwa-install--header .pwa-install__button--icon-only .pi-mobile {
    font-size: 0.875rem;
  }

  .pwa-install--header .pwa-install__label {
    font-size: 0.8125rem;
  }
}

@media (max-width: 1023px) {
  .pwa-install--header .pwa-install__label {
    display: none;
  }
}

.pwa-install--sidebar .pwa-install__button {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border-radius: 0.75rem;
  font-size: 0.8125rem;
  box-shadow: 0 4px 12px rgb(37 99 235 / 0.2);
}

.pwa-install__button:active:not(:disabled) {
  transform: scale(0.96);
}

.pwa-install__button:disabled {
  opacity: 0.75;
  cursor: wait;
}

.pwa-install__hint,
.pwa-install__message {
  margin: 0.5rem 0 0;
  font-size: 0.75rem;
  line-height: 1.45;
  color: var(--color-muted);
}

.pwa-install__message {
  color: #1d4ed8;
  font-weight: 600;
}
</style>
