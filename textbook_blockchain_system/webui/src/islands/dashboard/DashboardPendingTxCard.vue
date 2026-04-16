<script setup lang="ts">
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

defineProps<{ pendingTransactions?: PendingTxItem[] }>()
</script>

<template>
  <section class="v-card">
    <div class="v-cardHeader">
      <div>
        <div class="v-title">待确认交易</div>
        <div class="v-sub">只显示你作为卖家、状态为 pending 的交易</div>
      </div>
    </div>

    <div v-if="pendingTransactions?.length" class="v-list">
      <article v-for="tx in pendingTransactions" :key="tx.transaction_id" class="v-item">
        <div class="v-itemTitle">交易ID <span class="v-mono">{{ tx.transaction_id }}</span></div>
        <div class="v-meta">
          教材：{{ tx.textbook_description || '无' }}（<span class="v-mono">{{ tx.textbook_id }}</span>）
        </div>

        <div class="v-kvGrid">
          <div class="v-kv">
            <div class="v-k">买家</div>
            <div class="v-v">{{ tx.buyer_name || '未知' }}（{{ tx.buyer_contact || '无' }}）</div>
          </div>
          <div class="v-kv">
            <div class="v-k">报价</div>
            <div class="v-v">{{ tx.offer_price ?? 0 }} 元</div>
          </div>
          <div class="v-kv">
            <div class="v-k">状态</div>
            <div class="v-v"><span class="v-pill">{{ tx.status || '-' }}</span></div>
          </div>
        </div>

        <div class="v-meta">链上交易哈希：{{ tx.blockchain_hash || '无' }}</div>

        <div class="v-actions">
          <form method="POST" action="/transaction/confirm">
            <input type="hidden" name="textbook_id" :value="tx.textbook_id" />
            <input type="hidden" name="transaction_id" :value="tx.transaction_id" />
            <button class="v-btn" type="submit">确认交易</button>
          </form>

          <form method="POST" action="/transaction/reject">
            <input type="hidden" name="textbook_id" :value="tx.textbook_id" />
            <input type="hidden" name="transaction_id" :value="tx.transaction_id" />
            <button class="v-btn v-btnDanger" type="submit">拒绝</button>
          </form>
        </div>
      </article>
    </div>
    <div v-else class="v-empty">暂无待确认交易</div>
  </section>
</template>

<style scoped>
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

.v-list {
  display: grid;
  gap: 12px;
}

.v-item {
  border: 1px solid var(--border);
  border-radius: 12px;
  background: #fafafa;
  padding: 12px;
}

.v-itemTitle {
  font-weight: 700;
  font-size: 14px;
}

.v-meta {
  color: var(--muted);
  font-size: 13px;
  margin-top: 6px;
}

.v-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  background: #f3f4f6;
  border: 1px solid var(--border);
  padding: 2px 6px;
  border-radius: 8px;
}

.v-kvGrid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 10px;
}

.v-kv {
  border: 1px solid var(--border);
  border-radius: 12px;
  background: #fff;
  padding: 10px;
}

.v-k {
  color: var(--muted);
  font-size: 12px;
}

.v-v {
  margin-top: 6px;
  font-size: 14px;
}

.v-pill {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  background: #e5e7eb;
  color: #111827;
}

.v-actions {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

.v-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid transparent;
  background: var(--primary);
  color: #fff;
  cursor: pointer;
  transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
}

.v-btn:hover {
  background: var(--primaryHover);
  transform: translateY(-1px);
}

.v-btnDanger {
  background: #dc3545;
}

.v-btnDanger:hover {
  background: #b52a37;
}

.v-empty {
  color: var(--muted);
  padding: 12px;
  border: 1px dashed var(--border);
  border-radius: 12px;
  background: #fff;
}

@media (max-width: 992px) {
  .v-kvGrid {
    grid-template-columns: 1fr;
  }
}
</style>

