<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed } from 'vue'

import type { LegalDocument } from '@/types/legal'

const props = defineProps<{
  document: LegalDocument
}>()

const activeId = ref<string>(props.document.sections[0]?.id ?? '')
const observer = ref<IntersectionObserver | null>(null)

const tocItems = computed(() =>
  props.document.sections.flatMap((section) => {
    const items = [{ id: section.id, label: section.title, level: 1 }]
    if (section.subsections) {
      for (const sub of section.subsections) {
        items.push({ id: sub.id, label: sub.title, level: 2 })
      }
    }
    return items
  }),
)

function scrollToSection(id: string) {
  const el = document.getElementById(id)
  if (!el) return
  el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  activeId.value = id
  history.replaceState(null, '', `#${id}`)
}

onMounted(() => {
  const ids = tocItems.value.map((item) => item.id)
  observer.value = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)
      if (visible[0]?.target.id) {
        activeId.value = visible[0].target.id
      }
    },
    { rootMargin: '-15% 0px -55% 0px', threshold: [0, 0.25, 0.5, 1] },
  )

  for (const id of ids) {
    const el = document.getElementById(id)
    if (el) observer.value.observe(el)
  }

  const hash = window.location.hash.replace('#', '')
  if (hash && ids.includes(hash)) {
    setTimeout(() => scrollToSection(hash), 100)
  }
})

onUnmounted(() => {
  observer.value?.disconnect()
})
</script>

<template>
  <article class="legal-doc legal-prose">
    <header class="legal-doc__header">
      <h1 class="legal-doc__title font-display">{{ document.title }}</h1>
      <p class="legal-doc__subtitle">{{ document.subtitle }}</p>
      <p class="legal-doc__meta">
        Dernière mise à jour : {{ document.lastUpdated }}
      </p>
      <p class="legal-doc__preamble">{{ document.preamble }}</p>
    </header>

    <nav class="legal-doc__toc" aria-label="Sommaire du document">
      <h2 class="legal-doc__toc-title font-display">Sommaire</h2>
      <ul class="legal-doc__toc-list">
        <li
          v-for="item in tocItems"
          :key="item.id"
          :class="['legal-doc__toc-item', `legal-doc__toc-item--level-${item.level}`]"
        >
          <button
            type="button"
            class="legal-doc__toc-link"
            :class="{ 'legal-doc__toc-link--active': activeId === item.id }"
            :aria-current="activeId === item.id ? 'location' : undefined"
            @click="scrollToSection(item.id)"
          >
            {{ item.label }}
          </button>
        </li>
      </ul>
    </nav>

    <div class="legal-doc__body">
      <section
        v-for="section in document.sections"
        :id="section.id"
        :key="section.id"
        class="legal-doc__section"
      >
        <h2 class="legal-doc__section-title font-display">{{ section.title }}</h2>

        <p v-for="(paragraph, index) in section.paragraphs" :key="index" class="legal-doc__p">
          {{ paragraph }}
        </p>

        <ul v-if="section.list" class="legal-doc__list">
          <li v-for="(item, index) in section.list" :key="index">{{ item }}</li>
        </ul>

        <div
          v-for="sub in section.subsections"
          :id="sub.id"
          :key="sub.id"
          class="legal-doc__subsection"
        >
          <h3 class="legal-doc__subsection-title font-display">{{ sub.title }}</h3>
          <p v-for="(paragraph, index) in sub.paragraphs" :key="index" class="legal-doc__p">
            {{ paragraph }}
          </p>
          <ul v-if="sub.list" class="legal-doc__list">
            <li v-for="(item, index) in sub.list" :key="index">{{ item }}</li>
          </ul>
        </div>
      </section>
    </div>
  </article>
</template>

<style scoped>
.font-display {
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}

.legal-doc__header {
  margin-bottom: 2rem;
}

.legal-doc__title {
  font-size: 2.25rem;
  font-weight: 800;
  color: #172554;
  letter-spacing: -0.025em;
  line-height: 1.2;
}

.legal-doc__subtitle {
  margin-top: 0.75rem;
  font-size: 1.125rem;
  color: #64748b;
  line-height: 1.6;
}

.legal-doc__meta {
  margin-top: 1rem;
  font-size: 0.9375rem;
  color: #64748b;
}

.legal-doc__preamble {
  margin-top: 1.25rem;
  padding: 1.25rem 1.5rem;
  background-color: #fff1f5;
  border: 1px solid #fecdd3;
  border-radius: 1rem;
  font-size: 1.0625rem;
  line-height: 1.7;
  color: #1e293b;
}

.legal-doc__toc {
  position: sticky;
  top: 5rem;
  z-index: 5;
  margin-bottom: 2rem;
  padding: 1.25rem 1.5rem;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 1rem;
  max-height: 45vh;
  overflow-y: auto;
}

.legal-doc__toc-title {
  font-size: 1rem;
  font-weight: 700;
  color: #172554;
  margin-bottom: 1rem;
}

.legal-doc__toc-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.legal-doc__toc-item--level-2 {
  padding-left: 1rem;
}

.legal-doc__toc-link {
  width: 100%;
  text-align: left;
  padding: 0.5rem 0.625rem;
  border: none;
  border-radius: 0.5rem;
  background: transparent;
  font-size: 0.9375rem;
  line-height: 1.45;
  color: #64748b;
  cursor: pointer;
  border-left: 3px solid transparent;
}

.legal-doc__toc-link:hover {
  background-color: #fff;
  color: #ed147d;
}

.legal-doc__toc-link--active {
  color: #ed147d;
  font-weight: 600;
  background-color: #fff;
  border-left-color: #ed147d;
}

.legal-doc__section {
  scroll-margin-top: 6rem;
  margin-bottom: 2.5rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e2e8f0;
}

.legal-doc__section:last-child {
  border-bottom: none;
}

.legal-doc__section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #172554;
  margin-bottom: 1rem;
}

.legal-doc__subsection {
  scroll-margin-top: 6rem;
  margin-top: 1.5rem;
  padding-left: 1rem;
  border-left: 4px solid #fecdd3;
}

.legal-doc__subsection-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #172554;
  margin-bottom: 0.75rem;
}

.legal-doc__p {
  font-size: 1.0625rem;
  line-height: 1.75;
  color: #334155;
  margin-bottom: 1rem;
}

.legal-doc__list {
  margin: 0 0 1rem 1.5rem;
  padding: 0;
  font-size: 1.0625rem;
  line-height: 1.75;
  color: #334155;
  list-style-type: disc;
}

.legal-doc__list li {
  margin-bottom: 0.5rem;
  padding-left: 0.25rem;
}

@media (min-width: 1024px) {
  .legal-doc {
    display: grid;
    grid-template-columns: 280px 1fr;
    gap: 3rem;
    align-items: start;
  }

  .legal-doc__header,
  .legal-doc__body {
    grid-column: 2;
  }

  .legal-doc__toc {
    grid-column: 1;
    grid-row: 1 / span 2;
    top: 6rem;
    max-height: calc(100vh - 8rem);
  }

  .legal-doc__header {
    grid-row: 1;
  }

  .legal-doc__body {
    grid-row: 2;
  }
}
</style>
