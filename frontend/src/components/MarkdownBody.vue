<template>
  <div class="md-body" v-html="html"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps<{ source?: string }>()

const html = computed(() => {
  const src = (props.source || '').trim()
  if (!src) return ''
  try {
    return marked.parse(src, { gfm: true, breaks: true }) as string
  } catch (e) {
    return src
  }
})
</script>
