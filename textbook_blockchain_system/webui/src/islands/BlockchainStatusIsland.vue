<script setup lang="ts">
import { computed } from 'vue'
import ChainPager from '@/islands/blockchain/ChainPager.vue'
import ChainSummaryCard from '@/islands/blockchain/ChainSummaryCard.vue'
import BlockList from '@/islands/blockchain/BlockList.vue'

type TxItem = {
  type?: string
  hash?: string
  textbook_description?: string
  textbook_id?: string
  isbn?: string
  version?: string
  condition?: string
  buyer_name?: string
  offer_price?: number
  price_label?: string
  status?: string
}

type BlockItem = {
  index: number
  timestamp: string
  previous_hash: string
  hash: string
  transactions: TxItem[]
}

type InitialState = {
  chain?: BlockItem[]
  chain_length?: number
  is_valid?: boolean
  page?: number
  total_pages?: number
}

const props = defineProps<{ initial?: Record<string, unknown> | null }>()

const state = computed<InitialState>(() => {
  const raw = (props.initial ?? {}) as InitialState
  return {
    chain: raw.chain ?? [],
    chain_length: raw.chain_length ?? 0,
    is_valid: raw.is_valid ?? false,
    page: raw.page ?? 1,
    total_pages: raw.total_pages ?? 1,
  }
})
</script>

<template>
  <div class="v-scope">
    <ChainSummaryCard
      :chain-length="state.chain_length"
      :is-valid="state.is_valid"
    />

    <div class="v-card">
      <div class="v-cardHeader">
        <div>
          <div class="v-title">区块详情</div>
          <div class="v-sub">支持分页浏览历史区块</div>
        </div>
        <ChainPager :page="state.page" :total-pages="state.total_pages" />
      </div>

      <BlockList :blocks="state.chain" />

      <div class="v-footerPager">
        <ChainPager :page="state.page" :total-pages="state.total_pages" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.v-scope {
  --bg: #f5f5f5;
  --card: #ffffff;
  --primary: #4caf50;
  --primaryHover: #45a049;
  --text: #111827;
  --muted: #6b7280;
  --border: #e5e7eb;
  --shadow: 0 6px 18px rgba(16, 24, 40, 0.08);
  color: var(--text);
}

.v-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 16px;
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

.v-footerPager {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

@media (max-width: 992px) {
  .v-cardHeader {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>

