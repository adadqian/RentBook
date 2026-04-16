<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ page: number; totalPages: number }>()

const prevHref = computed(() => `/blockchain/status?page=${props.page - 1}`)
const nextHref = computed(() => `/blockchain/status?page=${props.page + 1}`)

const prevDisabled = computed(() => props.page <= 1)
const nextDisabled = computed(() => props.page >= props.totalPages)
</script>

<template>
  <div class="v-pager" aria-label="分页">
    <a class="v-link" :class="prevDisabled ? 'v-disabled' : ''" :href="prevHref">上一页</a>
    <div class="v-mid">第 {{ page }} / {{ totalPages }} 页</div>
    <a class="v-link" :class="nextDisabled ? 'v-disabled' : ''" :href="nextHref">下一页</a>
  </div>
</template>

<style scoped>
.v-pager {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.v-mid {
  color: var(--muted);
  font-size: 13px;
}

.v-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border-radius: 10px;
  background: #111827;
  color: #fff;
  text-decoration: none;
  transition: transform 120ms ease, background 120ms ease;
}

.v-link:hover {
  background: #0b1220;
  transform: translateY(-1px);
}

.v-disabled {
  opacity: 0.45;
  pointer-events: none;
  transform: none;
}
</style>

