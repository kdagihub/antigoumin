<script setup lang="ts">
import Checkbox from 'primevue/checkbox'
import { RouterLink } from 'vue-router'

const model = defineModel<boolean>({ required: true })
</script>

<template>
  <div class="legal-acceptance">
    <Checkbox v-model="model" input-id="legal-acceptance" :binary="true" />
    <label for="legal-acceptance" class="legal-acceptance__label">
      J’ai lu et j’accepte les
      <RouterLink to="/cgu" target="_blank">Conditions Générales d’Utilisation</RouterLink>
      et la
      <RouterLink to="/confidentialite" target="_blank">Politique de confidentialité</RouterLink>.
    </label>
  </div>
</template>

<style scoped>
.legal-acceptance {
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
}

.legal-acceptance__label {
  font-size: 0.8125rem;
  line-height: 1.5;
  color: var(--color-muted);
  cursor: pointer;
}

.legal-acceptance__label a {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
}

.legal-acceptance__label a:hover {
  text-decoration: underline;
}
</style>
