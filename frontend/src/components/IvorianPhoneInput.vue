<script setup lang="ts">
import { computed } from 'vue'

import { formatIvorianLocalDisplay, toIvorianLocalDigits } from '@/utils/ivorianPhone'

const props = withDefaults(
  defineProps<{
    modelValue: string
    id?: string
    placeholder?: string
    ariaLabel?: string
    disabled?: boolean
    variant?: 'default' | 'dark'
  }>(),
  {
    placeholder: '07 00 00 00 00',
    ariaLabel: 'Numéro mobile ivoirien',
    disabled: false,
    variant: 'default',
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const displayValue = computed(() => formatIvorianLocalDisplay(props.modelValue))

function onInput(event: Event) {
  const target = event.target as HTMLInputElement
  const digits = toIvorianLocalDigits(target.value).slice(0, 10)
  emit('update:modelValue', digits)
  target.value = formatIvorianLocalDisplay(digits)
}

function onBlur(event: Event) {
  const target = event.target as HTMLInputElement
  target.value = formatIvorianLocalDisplay(props.modelValue)
}
</script>

<template>
  <div
    class="ivorian-phone-input"
    :class="[
      `ivorian-phone-input--${variant}`,
      { 'ivorian-phone-input--disabled': disabled },
    ]"
  >
    <span class="ivorian-phone-input__prefix" aria-hidden="true">
      <svg
        class="ivorian-phone-input__flag"
        viewBox="0 0 24 16"
        role="img"
        aria-label="Côte d'Ivoire"
      >
        <rect width="8" height="16" x="0" fill="#F77F00" />
        <rect width="8" height="16" x="8" fill="#FFFFFF" />
        <rect width="8" height="16" x="16" fill="#009E60" />
      </svg>
      <span class="ivorian-phone-input__code">+225</span>
    </span>
    <input
      :id="id"
      class="ivorian-phone-input__field"
      type="tel"
      inputmode="tel"
      autocomplete="tel-national"
      :value="displayValue"
      :placeholder="placeholder"
      :aria-label="ariaLabel"
      :disabled="disabled"
      @input="onInput"
      @blur="onBlur"
    />
  </div>
</template>

<style scoped>
.ivorian-phone-input {
  display: flex;
  align-items: stretch;
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  background: var(--color-surface);
  overflow: hidden;
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease;
}

.ivorian-phone-input:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-primary) 18%, transparent);
}

.ivorian-phone-input--dark {
  border-color: rgb(255 255 255 / 0.2);
  background: rgb(255 255 255 / 0.08);
}

.ivorian-phone-input--dark:focus-within {
  border-color: rgb(255 255 255 / 0.45);
  box-shadow: 0 0 0 3px rgb(237 20 125 / 0.25);
}

.ivorian-phone-input--disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.ivorian-phone-input__prefix {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0 0.875rem;
  border-right: 1px solid var(--color-border);
  background: color-mix(in srgb, var(--color-ink) 4%, white);
  white-space: nowrap;
  flex-shrink: 0;
}

.ivorian-phone-input--dark .ivorian-phone-input__prefix {
  border-right-color: rgb(255 255 255 / 0.15);
  background: rgb(255 255 255 / 0.06);
}

.ivorian-phone-input__flag {
  width: 1.375rem;
  height: 0.9375rem;
  border-radius: 0.125rem;
  box-shadow: 0 0 0 1px rgb(0 0 0 / 0.08);
}

.ivorian-phone-input__code {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--color-ink);
}

.ivorian-phone-input--dark .ivorian-phone-input__code {
  color: #fff;
}

.ivorian-phone-input__field {
  min-width: 0;
  flex: 1;
  border: 0;
  background: transparent;
  padding: 0.75rem 0.875rem;
  font-size: 1rem;
  font-weight: 500;
  color: var(--color-ink);
}

.ivorian-phone-input__field:focus {
  outline: none;
}

.ivorian-phone-input__field::placeholder {
  color: color-mix(in srgb, var(--color-muted) 70%, white);
}

.ivorian-phone-input--dark .ivorian-phone-input__field {
  color: #fff;
}

.ivorian-phone-input--dark .ivorian-phone-input__field::placeholder {
  color: rgb(148 163 184);
}

.ivorian-phone-input--disabled .ivorian-phone-input__field {
  cursor: not-allowed;
}
</style>
