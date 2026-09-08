<template>
  <div class="md-body" v-html="html"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ source?: string }>()

function escapeHtml(s: string) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function inlineFmt(s: string) {
  let t = escapeHtml(s)
  t = t.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  t = t.replace(/`([^`]+)`/g, '<code>$1</code>')
  return t
}

const html = computed(() => {
  const src = (props.source || '').replace(/\r\n/g, '\n')
  if (!src.trim()) return ''
  const lines = src.split('\n')
  let out = ''
  let list: 'ul' | 'ol' | '' = ''
  const close = () => {
    if (list) {
      out += list === 'ul' ? '</ul>' : '</ol>'
      list = ''
    }
  }
  for (const raw of lines) {
    const line = raw.trimEnd()
    if (!line.trim()) {
      close()
      continue
    }
    if (line.startsWith('### ')) {
      close()
      out += `<h4>${inlineFmt(line.slice(4))}</h4>`
      continue
    }
    if (line.startsWith('## ')) {
      close()
      out += `<h3>${inlineFmt(line.slice(3))}</h3>`
      continue
    }
    if (line.startsWith('# ')) {
      close()
      out += `<h3>${inlineFmt(line.slice(2))}</h3>`
      continue
    }
    const ul = line.match(/^[-*•]\s+(.*)$/)
    if (ul) {
      if (list !== 'ul') {
        close()
        out += '<ul>'
        list = 'ul'
      }
      out += `<li>${inlineFmt(ul[1])}</li>`
      continue
    }
    const ol = line.match(/^\d+[.\、]\s*(.*)$/)
    if (ol) {
      if (list !== 'ol') {
        close()
        out += '<ol>'
        list = 'ol'
      }
      out += `<li>${inlineFmt(ol[1])}</li>`
      continue
    }
    close()
    out += `<p>${inlineFmt(line)}</p>`
  }
  close()
  return out
})
</script>
