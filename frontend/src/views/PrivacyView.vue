<script setup lang="ts">
import LegalDocumentPage from '@/components/legal/LegalDocumentPage.vue'
import { privacyDocument } from '@/content/privacy'
import LegalShell from '@/layouts/LegalShell.vue'
</script>

<template>
  <LegalShell>
    <LegalDocumentPage :document="privacyDocument" />
  </LegalShell>
</template>
