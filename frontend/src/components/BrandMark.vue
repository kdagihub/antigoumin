<script setup lang="ts">
import logoAgm from '@/assets/img/logo_agm_sf.png'

defineProps<{
  size?: 'sm' | 'md' | 'lg'
}>()
</script>

<template>
  <img
    :src="logoAgm"
    alt="AntiGoumin"
    class="brand-logo object-contain"
    :class="{
      'brand-logo--sm': size === 'sm',
      'brand-logo--lg': size === 'lg',
    }"
  />
</template>

<style scoped>
.brand-logo {
  width: 2.75rem;
  height: 2.75rem;
  flex-shrink: 0;
}

.brand-logo--sm {
  width: 2.25rem;
  height: 2.25rem;
}

.brand-logo--lg {
  width: 4.5rem;
  height: 4.5rem;
}
</style>
