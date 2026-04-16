<script setup lang="ts">
import { watch } from 'vue'

const model = defineModel<string | null>({ default: null })

let timer: number | null = null

watch(
  () => model.value,
  (v) => {
    if (!v) return
    if (timer) window.clearTimeout(timer)
    timer = window.setTimeout(() => {
      model.value = null
    }, 1800)
  }
)
</script>

<template>
  <div v-if="model" class="v-toast" role="status" aria-live="polite">
    {{ model }}
  </div>
</template>

<style scoped>
.v-toast {
  position: sticky;
  top: 12px;
  z-index: 50;
  margin: 0 auto 12px;
  max-width: 1200px;
  background: rgba(17, 24, 39, 0.92);
  color: white;
  padding: 10px 12px;
  border-radius: 10px;
  box-shadow: var(--shadow);
}
</style>

