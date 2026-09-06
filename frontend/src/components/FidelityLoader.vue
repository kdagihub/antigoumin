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
    'Surveillance du rythme en cours…',
    'Analyse du signal cardiaque…',
    'Préparation du test de fidélité…',
    'Encore quelques battements…',
  ],
  payment: [
    'Préparation du paiement sécurisé…',
    'Connexion à Mobile Money…',
  ],
  history: [
    'Chargement de vos tests…',
    'Récupération de l’historique…',
  ],
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
  <div class="fidelity-loader" role="status" aria-live="polite">
    <div class="fidelity-loader__monitor" aria-hidden="true">
      <div class="fidelity-loader__grid" />
      <svg class="fidelity-loader__ecg" viewBox="0 0 320 80" preserveAspectRatio="none">
        <path
          class="fidelity-loader__ecg-line"
          d="M0 40 H40 L48 40 L52 18 L56 62 L60 40 H100 L108 40 L112 28 L116 52 L120 40 H160 L168 40 L172 22 L176 58 L180 40 H220 L228 40 L232 16 L236 64 L240 40 H280 L288 40 L292 30 L296 50 L300 40 H640"
        />
      </svg>
      <div class="fidelity-loader__pulse-dot" />
      <div class="fidelity-loader__heart-wrap">
        <svg class="fidelity-loader__heart" viewBox="0 0 24 24" fill="currentColor">
          <path
            d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
          />
        </svg>
      </div>
    </div>
    <p class="fidelity-loader__message">{{ currentMessage }}</p>
    <div class="fidelity-loader__vitals" aria-hidden="true">
      <span>BPM <strong>72</strong></span>
      <span>SpO₂ <strong>98%</strong></span>
    </div>
  </div>
</template>

<style scoped>
.fidelity-loader {
  display: grid;
  justify-items: center;
  gap: 0.875rem;
  padding: 1.25rem 1rem;
  text-align: center;
}

.fidelity-loader__monitor {
  position: relative;
  width: min(100%, 18rem);
  height: 6.5rem;
  border-radius: 0.875rem;
  overflow: hidden;
  background: linear-gradient(180deg, #0f172a 0%, #1e3a5f 100%);
  border: 1px solid rgb(59 130 246 / 0.35);
  box-shadow:
    inset 0 0 24px rgb(59 130 246 / 0.08),
    0 8px 24px rgb(30 58 95 / 0.25);
}

.fidelity-loader__grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgb(59 130 246 / 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgb(59 130 246 / 0.08) 1px, transparent 1px);
  background-size: 16px 16px;
  opacity: 0.7;
}

.fidelity-loader__ecg {
  position: absolute;
  inset: 0;
  width: 200%;
  height: 100%;
  animation: ecg-scroll 2.4s linear infinite;
}

.fidelity-loader__ecg-line {
  fill: none;
  stroke: #38bdf8;
  stroke-width: 2.5;
  stroke-linecap: round;
  stroke-linejoin: round;
  filter: drop-shadow(0 0 6px rgb(56 189 248 / 0.75));
}

.fidelity-loader__pulse-dot {
  position: absolute;
  top: 0.5rem;
  right: 0.625rem;
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: #38bdf8;
  animation: pulse-dot 1s ease-in-out infinite;
  box-shadow: 0 0 8px rgb(56 189 248 / 0.8);
}

.fidelity-loader__heart-wrap {
  position: absolute;
  left: 0.625rem;
  bottom: 0.5rem;
  color: #3b82f6;
  filter: drop-shadow(0 0 8px rgb(59 130 246 / 0.6));
  animation: heart-monitor 1.1s ease-in-out infinite;
}

.fidelity-loader__heart {
  width: 1.375rem;
  height: 1.375rem;
}

.fidelity-loader__message {
  margin: 0;
  max-width: 18rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #1e40af;
  line-height: 1.5;
}

.fidelity-loader__vitals {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #64748b;
  font-variant-numeric: tabular-nums;
}

.fidelity-loader__vitals strong {
  color: #2563eb;
  font-weight: 800;
}

@keyframes ecg-scroll {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

@keyframes pulse-dot {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.45;
    transform: scale(0.85);
  }
}

@keyframes heart-monitor {
  0%,
  100% {
    transform: scale(1);
  }
  14% {
    transform: scale(1.14);
  }
  28% {
    transform: scale(1);
  }
  42% {
    transform: scale(1.08);
  }
  70% {
    transform: scale(1);
  }
}
</style>
