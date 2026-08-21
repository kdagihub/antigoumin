<script setup lang="ts">
import DashboardShell from '@/layouts/DashboardShell.vue'

import ModulePlaceholder from '@/components/dashboard/ModulePlaceholder.vue'
</script>

<template>
  <DashboardShell>
    <ModulePlaceholder
      title="Mes déclarations"
      description="Déclarez et suivez vos relations certifiées."
      icon="pi pi-heart"
    />
  </DashboardShell>
</template>
