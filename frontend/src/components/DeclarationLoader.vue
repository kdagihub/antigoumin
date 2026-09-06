<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'

const messages = [
  'Chargement de vos relations…',
  'On prépare votre espace amoureux…',
  'Encore un instant…',
]

const messageIndex = ref(0)
let timer: ReturnType<typeof setInterval> | undefined

const currentMessage = computed(() => messages[messageIndex.value] ?? messages[0])

onMounted(() => {
  timer = setInterval(() => {
    messageIndex.value = (messageIndex.value + 1) % messages.length
  }, 2200)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="declaration-loader" role="status" aria-live="polite">
    <div class="declaration-loader__hearts" aria-hidden="true">
      <span class="declaration-loader__heart declaration-loader__heart--left">💕</span>
      <span class="declaration-loader__heart declaration-loader__heart--center">❤️</span>
      <span class="declaration-loader__heart declaration-loader__heart--right">💕</span>
    </div>
    <p class="declaration-loader__message">{{ currentMessage }}</p>
  </div>
</template>

<style scoped>
.declaration-loader {
  display: grid;
  justify-items: center;
  gap: 0.875rem;
  padding: 1.25rem 1rem;
  text-align: center;
}

.declaration-loader__hearts {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.declaration-loader__heart {
  font-size: 1.5rem;
  line-height: 1;
}

.declaration-loader__heart--center {
  font-size: 2rem;
  animation: heart-pulse 1.1s ease-in-out infinite;
}

.declaration-loader__heart--left,
.declaration-loader__heart--right {
  opacity: 0.65;
  animation: heart-float 2s ease-in-out infinite;
}

.declaration-loader__heart--right {
  animation-delay: 0.4s;
}

.declaration-loader__message {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-muted);
}

@keyframes heart-pulse {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.15);
  }
}

@keyframes heart-float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-0.25rem);
  }
}
</style>
