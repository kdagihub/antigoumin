<script setup lang="ts">
import LegalDocumentPage from '@/components/legal/LegalDocumentPage.vue'
import { cguDocument } from '@/content/cgu'
import LegalShell from '@/layouts/LegalShell.vue'
</script>

<template>
  <LegalShell>
    <LegalDocumentPage :document="cguDocument" />
  </LegalShell>
</template>
