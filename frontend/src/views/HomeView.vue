<script setup lang="ts">
import FaqSection from '@/components/landing/FaqSection.vue'
import HeroSection from '@/components/landing/HeroSection.vue'
import LandingFooter from '@/components/landing/LandingFooter.vue'
import LandingHeader from '@/components/landing/LandingHeader.vue'
import PricingSection from '@/components/landing/PricingSection.vue'
import ServicesSection from '@/components/landing/ServicesSection.vue'
</script>

<template>
  <div class="landing min-h-dvh bg-white text-slate-900">
    <LandingHeader />
    <main>
      <HeroSection />
      <ServicesSection />
      <PricingSection />
      <FaqSection />
    </main>
    <LandingFooter />
  </div>
</template>

<style scoped>
.landing {
  font-family: 'Figtree', system-ui, sans-serif;
}
</style>
