<script setup lang="ts">
import DashboardShell from '@/layouts/DashboardShell.vue'

import ModulePlaceholder from '@/components/dashboard/ModulePlaceholder.vue'
</script>

<template>
  <DashboardShell>
    <ModulePlaceholder
      title="Tests de fidélité"
      description="Demandez ou répondez à une demande de transparence."
      icon="pi pi-search"
    />
  </DashboardShell>
</template>
