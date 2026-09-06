<script setup lang="ts">
import Button from 'primevue/button'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { dashboardTutorialCopy } from '@/content/onboardingCopy'
import { resolveTutorialTarget } from '@/composables/useOnboarding'

const visible = defineModel<boolean>('visible', { required: true })

const emit = defineEmits<{
  complete: []
  skip: []
}>()

const route = useRoute()
const stepIndex = ref(0)
const highlightStyle = ref<Record<string, string>>({})
const cardStyle = ref<Record<string, string>>({ visibility: 'hidden' })

const steps = dashboardTutorialCopy.steps
const currentStep = computed(() => steps[stepIndex.value]!)
const isLast = computed(() => stepIndex.value === steps.length - 1)

function updatePosition() {
  if (!visible.value || route.path !== '/app') return
  const target = resolveTutorialTarget(currentStep.value.target)
  if (!target) {
    cardStyle.value = {
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      visibility: 'visible',
    }
    highlightStyle.value = { display: 'none' }
    return
  }

  const rect = target.getBoundingClientRect()
  const padding = 8
  highlightStyle.value = {
    display: 'block',
    top: `${Math.max(rect.top - padding, 8)}px`,
    left: `${Math.max(rect.left - padding, 8)}px`,
    width: `${rect.width + padding * 2}px`,
    height: `${rect.height + padding * 2}px`,
  }

  const cardWidth = Math.min(window.innerWidth - 32, 320)
  let top = rect.bottom + 16
  if (top + 180 > window.innerHeight) {
    top = Math.max(rect.top - 196, 16)
  }
  let left = rect.left + rect.width / 2 - cardWidth / 2
  left = Math.max(16, Math.min(left, window.innerWidth - cardWidth - 16))

  cardStyle.value = {
    top: `${top}px`,
    left: `${left}px`,
    width: `${cardWidth}px`,
    visibility: 'visible',
  }
}

function finish(mode: 'complete' | 'skip') {
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
    finish('complete')
    return
  }
  stepIndex.value += 1
}

watch([visible, stepIndex, () => route.path], async () => {
  if (!visible.value) return
  await nextTick()
  updatePosition()
})

onMounted(() => {
  window.addEventListener('resize', updatePosition)
  window.addEventListener('scroll', updatePosition, true)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updatePosition)
  window.removeEventListener('scroll', updatePosition, true)
})
</script>

<template>
  <Teleport to="body">
    <div v-if="visible && route.path === '/app'" class="dashboard-tutorial" role="dialog" aria-modal="true">
      <div class="dashboard-tutorial__backdrop" aria-hidden="true" @click="finish('skip')" />
      <div class="dashboard-tutorial__highlight" :style="highlightStyle" aria-hidden="true" />
      <div class="dashboard-tutorial__card" :style="cardStyle">
        <p class="dashboard-tutorial__progress">
          {{ dashboardTutorialCopy.progress(stepIndex + 1, steps.length) }}
        </p>
        <h3 class="dashboard-tutorial__title font-display">{{ currentStep.title }}</h3>
        <p class="dashboard-tutorial__body">{{ currentStep.body }}</p>
        <div class="dashboard-tutorial__actions">
          <button type="button" class="dashboard-tutorial__skip" @click="finish('skip')">
            {{ dashboardTutorialCopy.skip }}
          </button>
          <Button
            type="button"
            :label="isLast ? dashboardTutorialCopy.finish : dashboardTutorialCopy.next"
            size="small"
            @click="goNext"
          />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.dashboard-tutorial {
  position: fixed;
  inset: 0;
  z-index: 1200;
  pointer-events: none;
}

.dashboard-tutorial__backdrop {
  position: absolute;
  inset: 0;
  background: rgb(15 23 42 / 0.55);
  pointer-events: auto;
}

.dashboard-tutorial__highlight {
  position: fixed;
  border-radius: 1rem;
  box-shadow:
    0 0 0 9999px rgb(15 23 42 / 0.55),
    0 0 0 3px #fff,
    0 8px 24px rgb(237 20 125 / 0.35);
  pointer-events: none;
  z-index: 1;
  transition:
    top 0.2s ease,
    left 0.2s ease,
    width 0.2s ease,
    height 0.2s ease;
}

.dashboard-tutorial__card {
  position: fixed;
  z-index: 2;
  background: #fff;
  border-radius: 1rem;
  padding: 1rem;
  box-shadow: 0 16px 40px rgb(15 23 42 / 0.18);
  pointer-events: auto;
}

.dashboard-tutorial__progress {
  margin: 0 0 0.35rem;
  font-size: 0.6875rem;
  font-weight: 700;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.dashboard-tutorial__title {
  margin: 0 0 0.5rem;
  font-size: 1.0625rem;
  color: var(--color-ink);
}

.dashboard-tutorial__body {
  margin: 0 0 1rem;
  font-size: 0.875rem;
  line-height: 1.55;
  color: var(--color-muted);
}

.dashboard-tutorial__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.dashboard-tutorial__skip {
  border: 0;
  background: transparent;
  color: var(--color-muted);
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
}

.dashboard-tutorial__skip:hover {
  color: var(--color-primary);
}
</style>
