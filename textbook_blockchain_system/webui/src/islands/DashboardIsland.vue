<script setup lang="ts">
import { computed, ref } from 'vue'
import DashboardAccountCard from '@/islands/dashboard/DashboardAccountCard.vue'
import DashboardBuyerTxCard from '@/islands/dashboard/DashboardBuyerTxCard.vue'
import DashboardPendingTxCard from '@/islands/dashboard/DashboardPendingTxCard.vue'
import DashboardTextbookListCard from '@/islands/dashboard/DashboardTextbookListCard.vue'
import ToastHost from '@/islands/shared/ToastHost.vue'

type TextbookItem = {
  textbook_id: string
  created_at?: string
  location?: string
  description?: string
  photos?: string
}

type PendingTxItem = {
  transaction_id: string
  textbook_id: string
  textbook_description?: string
  buyer_name?: string
  buyer_contact?: string
  offer_price?: number
  status?: string
  blockchain_hash?: string
}

type BuyerTxItem = {
  transaction_id: string
  textbook_id: string
  textbook_description?: string
  offer_price?: number
  status?: string
  created_at?: string
  updated_at?: string
  seller_name?: string
  seller_contact?: string
}

type InitialState = {
  user?: { id?: string; name?: string }
  textbooks?: TextbookItem[]
  pending_transactions?: PendingTxItem[]
  buyer_transactions?: BuyerTxItem[]
}

const props = defineProps<{ initial?: Record<string, unknown> | null }>()

const state = computed<InitialState>(() => {
  const raw = (props.initial ?? {}) as InitialState
  return {
    user: raw.user ?? {},
    textbooks: raw.textbooks ?? [],
    pending_transactions: raw.pending_transactions ?? [],
    buyer_transactions: raw.buyer_transactions ?? [],
  }
})

const toast = ref<string | null>(null)

function showToast(message: string) {
  toast.value = message
}

async function copy(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    showToast('复制成功')
  } catch {
    showToast('复制失败，请手动复制')
  }
}

function photosOf(tb: TextbookItem) {
  const raw = tb.photos || ''
  return raw
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
}
</script>

<template>
  <div class="v-scope">
    <ToastHost v-model="toast" />

    <DashboardAccountCard :user-id="state.user?.id" @copy="copy" />

    <div class="v-grid">
      <DashboardTextbookListCard :textbooks="state.textbooks" :photos-of="photosOf" />
      <DashboardPendingTxCard :pending-transactions="state.pending_transactions" />
      <DashboardBuyerTxCard :buyer-transactions="state.buyer_transactions" />
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

.v-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 992px) {
  .v-grid {
    grid-template-columns: 1fr;
  }
}
</style>

