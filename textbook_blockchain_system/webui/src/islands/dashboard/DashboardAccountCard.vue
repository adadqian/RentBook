<script setup lang="ts">
defineProps<{ userId?: string }>()
const emit = defineEmits<{ (e: 'copy', text: string): void }>()
</script>

<template>
  <section class="v-card">
    <div class="v-cardHeader">
      <div>
        <div class="v-title">我的账号</div>
        <div class="v-sub">该ID用于在链下数据库中标识买家/卖家</div>
      </div>
    </div>

    <div class="v-row">
      <div class="v-kv">
        <div class="v-k">用户ID</div>
        <div class="v-vMono">{{ userId || '-' }}</div>
      </div>
      <button
        class="v-btn v-btnSecondary"
        type="button"
        :disabled="!userId"
        @click="emit('copy', userId || '')"
      >
        复制
      </button>
    </div>
  </section>
</template>

<style scoped>
.v-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 16px;
  margin-bottom: 16px;
}

.v-cardHeader {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 12px;
}

.v-title {
  font-weight: 700;
  font-size: 16px;
}

.v-sub {
  color: var(--muted);
  font-size: 13px;
  margin-top: 4px;
}

.v-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.v-kv {
  flex: 1;
}

.v-k {
  color: var(--muted);
  font-size: 12px;
}

.v-vMono {
  margin-top: 6px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  background: #f3f4f6;
  border: 1px solid var(--border);
  padding: 6px 10px;
  border-radius: 10px;
}

.v-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid transparent;
  color: #fff;
  cursor: pointer;
  transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
}

.v-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.v-btnSecondary {
  background: #111827;
}

.v-btnSecondary:hover {
  background: #0b1220;
  transform: translateY(-1px);
}
</style>

