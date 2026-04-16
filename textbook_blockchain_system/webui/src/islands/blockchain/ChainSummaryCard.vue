<script setup lang="ts">
defineProps<{ chainLength: number; isValid: boolean }>()
</script>

<template>
  <section class="v-summary">
    <div class="v-metric">
      <div class="v-k">区块数量</div>
      <div class="v-num">{{ chainLength }}</div>
    </div>

    <div class="v-metric">
      <div class="v-k">区块链有效性</div>
      <div class="v-status" :class="isValid ? 'v-ok' : 'v-bad'">
        {{ isValid ? '有效' : '无效' }}
      </div>
    </div>
  </section>
</template>

<style scoped>
.v-summary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.v-metric {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 16px;
}

.v-k {
  color: var(--muted);
  font-size: 13px;
}

.v-num {
  margin-top: 8px;
  font-weight: 800;
  font-size: 28px;
  letter-spacing: -0.5px;
}

.v-status {
  margin-top: 10px;
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 13px;
  border: 1px solid transparent;
}

.v-ok {
  background: #d4edda;
  border-color: #b7e1c2;
  color: #155724;
}

.v-bad {
  background: #f8d7da;
  border-color: #f1b0b7;
  color: #721c24;
}

@media (max-width: 992px) {
  .v-summary {
    grid-template-columns: 1fr;
  }
}
</style>

