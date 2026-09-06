<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'

const props = withDefaults(
  defineProps<{
    variant?: 'search' | 'payment' | 'history'
  }>(),
  { variant: 'search' },
)

const messagesByVariant: Record<typeof props.variant, string[]> = {
  search: [
    'Recherche dans le registre AntiGoumin…',
    'Analyse du statut relationnel…',
    'Vérification discrète en cours…',
    'Encore quelques secondes…',
  ],
  payment: [
    'Préparation du paiement sécurisé…',
    'Connexion à Mobile Money…',
    'Redirection vers la caisse…',
  ],
  history: ['Chargement de votre historique…', 'Récupération de vos consultations…'],
}

const messageIndex = ref(0)
let timer: ReturnType<typeof setInterval> | undefined

const currentMessage = computed(
  () => messagesByVariant[props.variant][messageIndex.value] ?? messagesByVariant[props.variant][0],
)

onMounted(() => {
  const pool = messagesByVariant[props.variant]
  timer = setInterval(() => {
    messageIndex.value = (messageIndex.value + 1) % pool.length
  }, 2400)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="verification-loader" role="status" aria-live="polite">
    <div class="verification-loader__scene" aria-hidden="true">
      <!-- Silhouettes -->
      <div class="verification-loader__crowd">
        <span v-for="n in 7" :key="n" class="verification-loader__person" :style="{ '--i': n }" />
      </div>

      <!-- Loupe -->
      <div class="verification-loader__magnifier">
        <svg viewBox="0 0 64 64" fill="none">
          <circle cx="28" cy="28" r="16" stroke="currentColor" stroke-width="4" />
          <path
            d="M40 40 L54 54"
            stroke="currentColor"
            stroke-width="4"
            stroke-linecap="round"
          />
        </svg>
      </div>

      <!-- Cœur -->
      <div class="verification-loader__heart">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path
            d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
          />
        </svg>
      </div>
    </div>

    <p class="verification-loader__message">{{ currentMessage }}</p>
    <div class="verification-loader__dots" aria-hidden="true">
      <span /><span /><span />
    </div>
  </div>
</template>

<style scoped>
.verification-loader {
  display: grid;
  justify-items: center;
  gap: 1rem;
  padding: 1.5rem 1rem;
  text-align: center;
}

.verification-loader__scene {
  position: relative;
  width: 11rem;
  height: 6.5rem;
}

.verification-loader__crowd {
  position: absolute;
  inset: auto 0 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 0.45rem;
  height: 3.25rem;
}

.verification-loader__person {
  width: 0.75rem;
  height: calc(1.4rem + var(--i) * 0.15rem);
  border-radius: 999px 999px 0.25rem 0.25rem;
  background: color-mix(in srgb, var(--color-ink) 18%, white);
  animation: person-pulse 2.4s ease-in-out infinite;
  animation-delay: calc(var(--i) * 0.12s);
}

.verification-loader__magnifier {
  position: absolute;
  left: 0.5rem;
  top: 0.75rem;
  width: 3.25rem;
  height: 3.25rem;
  color: var(--color-primary);
  animation: magnifier-scan 2.8s ease-in-out infinite;
}

.verification-loader__heart {
  position: absolute;
  right: 1rem;
  top: 0.25rem;
  width: 2.25rem;
  height: 2.25rem;
  color: var(--color-primary);
  animation: heart-beat 1.1s ease-in-out infinite;
  filter: drop-shadow(0 4px 10px rgb(237 20 125 / 0.25));
}

.verification-loader__message {
  margin: 0;
  max-width: 18rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-muted);
  line-height: 1.5;
  animation: message-fade 2.4s ease-in-out infinite;
}

.verification-loader__dots {
  display: inline-flex;
  gap: 0.35rem;
}

.verification-loader__dots span {
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 50%;
  background: var(--color-primary);
  animation: dot-bounce 1.2s ease-in-out infinite;
}

.verification-loader__dots span:nth-child(2) {
  animation-delay: 0.15s;
}

.verification-loader__dots span:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes heart-beat {
  0%,
  100% {
    transform: scale(1);
  }
  14% {
    transform: scale(1.18);
  }
  28% {
    transform: scale(1);
  }
  42% {
    transform: scale(1.12);
  }
  70% {
    transform: scale(1);
  }
}

@keyframes magnifier-scan {
  0%,
  100% {
    transform: translate(0, 0) rotate(-8deg);
  }
  50% {
    transform: translate(4.5rem, 0.35rem) rotate(12deg);
  }
}

@keyframes person-pulse {
  0%,
  100% {
    opacity: 0.45;
    transform: translateY(0);
  }
  50% {
    opacity: 1;
    transform: translateY(-0.2rem);
  }
}

@keyframes dot-bounce {
  0%,
  80%,
  100% {
    transform: translateY(0);
    opacity: 0.45;
  }
  40% {
    transform: translateY(-0.35rem);
    opacity: 1;
  }
}

@keyframes message-fade {
  0%,
  100% {
    opacity: 0.75;
  }
  50% {
    opacity: 1;
  }
}
</style>
