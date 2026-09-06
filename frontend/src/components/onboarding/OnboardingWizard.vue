<script setup lang="ts">
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import { computed, ref } from 'vue'

import { onboardingWizardCopy } from '@/content/onboardingCopy'

const visible = defineModel<boolean>('visible', { required: true })

const emit = defineEmits<{
  complete: []
  skip: []
}>()

const stepIndex = ref(0)
const steps = onboardingWizardCopy.steps
const currentStep = computed(() => steps[stepIndex.value]!)
const isFirst = computed(() => stepIndex.value === 0)
const isLast = computed(() => stepIndex.value === steps.length - 1)

function closeWizard(mode: 'complete' | 'skip') {
  visible.value = false
  stepIndex.value = 0
  if (mode === 'complete') {
    emit('complete')
  } else {
    emit('skip')
  }
}

function goNext() {
  if (isLast.value) {
    closeWizard('complete')
    return
  }
  stepIndex.value += 1
}

function goBack() {
  if (!isFirst.value) {
    stepIndex.value -= 1
  }
}
</script>

<template>
  <Dialog
    v-model:visible="visible"
    modal
    :closable="false"
    :draggable="false"
    class="onboarding-wizard"
    :style="{ width: 'min(92vw, 28rem)' }"
  >
    <template #header>
      <div class="onboarding-wizard__head">
        <span class="onboarding-wizard__progress">
          {{ onboardingWizardCopy.progress(stepIndex + 1, steps.length) }}
        </span>
      </div>
    </template>

    <div class="onboarding-wizard__body">
      <div class="onboarding-wizard__emoji" aria-hidden="true">{{ currentStep.emoji }}</div>
      <h2 class="onboarding-wizard__title font-display">{{ currentStep.title }}</h2>
      <p class="onboarding-wizard__text">{{ currentStep.body }}</p>
    </div>

    <template #footer>
      <div class="onboarding-wizard__footer">
        <button type="button" class="onboarding-wizard__skip" @click="closeWizard('skip')">
          {{ onboardingWizardCopy.skip }}
        </button>
        <div class="onboarding-wizard__actions">
          <Button
            v-if="!isFirst"
            type="button"
            :label="onboardingWizardCopy.back"
            severity="secondary"
            outlined
            @click="goBack"
          />
          <Button
            type="button"
            :label="isLast ? onboardingWizardCopy.finish : onboardingWizardCopy.next"
            icon="pi pi-arrow-right"
            icon-pos="right"
            @click="goNext"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<style scoped>
.onboarding-wizard__head {
  width: 100%;
}

.onboarding-wizard__progress {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.onboarding-wizard__body {
  text-align: center;
  padding: 0.25rem 0 0.5rem;
}

.onboarding-wizard__emoji {
  font-size: 2.75rem;
  line-height: 1;
  margin-bottom: 0.75rem;
}

.onboarding-wizard__title {
  margin: 0 0 0.75rem;
  font-size: 1.375rem;
  color: var(--color-ink);
}

.onboarding-wizard__text {
  margin: 0;
  color: var(--color-muted);
  line-height: 1.6;
  font-size: 0.9375rem;
}

.onboarding-wizard__footer {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
  width: 100%;
}

.onboarding-wizard__skip {
  align-self: center;
  border: 0;
  background: transparent;
  color: var(--color-muted);
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.25rem;
}

.onboarding-wizard__skip:hover {
  color: var(--color-primary);
}

.onboarding-wizard__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
</style>
