<script setup lang="ts">
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

defineProps<{ blocks: BlockItem[] }>()
</script>

<template>
  <div v-if="blocks.length" class="v-list">
    <article v-for="b in blocks" :key="b.index" class="v-block">
      <div class="v-blockHead">
        <div class="v-blockTitle">区块 #{{ b.index }}</div>
        <div class="v-badge">交易 {{ b.transactions?.length || 0 }}</div>
      </div>

      <dl class="v-dl">
        <div class="v-dlRow">
          <dt>时间戳</dt>
          <dd>{{ b.timestamp }}</dd>
        </div>
        <div class="v-dlRow">
          <dt>前一区块哈希</dt>
          <dd class="v-hash">{{ b.previous_hash }}</dd>
        </div>
        <div class="v-dlRow">
          <dt>当前区块哈希</dt>
          <dd class="v-hash">{{ b.hash }}</dd>
        </div>
      </dl>

      <div v-if="b.transactions?.length" class="v-txList">
        <div class="v-txTitle">交易</div>
        <div class="v-txGrid">
          <div v-for="(tx, idx) in b.transactions" :key="`${b.index}-${idx}`" class="v-tx">
            <div class="v-txRow" v-if="tx.type"><span class="v-k">类型</span><span class="v-v">{{ tx.type }}</span></div>
            <div class="v-txRow" v-if="tx.textbook_description"><span class="v-k">教材</span><span class="v-v">{{ tx.textbook_description }}</span></div>
            <div class="v-txRow" v-if="tx.textbook_id"><span class="v-k">教材ID</span><span class="v-v v-mono">{{ tx.textbook_id }}</span></div>
            <div class="v-txRow" v-if="tx.isbn"><span class="v-k">ISBN</span><span class="v-v">{{ tx.isbn }}</span></div>
            <div class="v-txRow" v-if="tx.version"><span class="v-k">版本</span><span class="v-v">{{ tx.version }}</span></div>
            <div class="v-txRow" v-if="tx.condition"><span class="v-k">品相</span><span class="v-v">{{ tx.condition }}</span></div>
            <div class="v-txRow" v-if="tx.buyer_name"><span class="v-k">买家</span><span class="v-v">{{ tx.buyer_name }}</span></div>
            <div class="v-txRow" v-if="tx.offer_price !== undefined && tx.offer_price !== null">
              <span class="v-k">{{ tx.price_label || '金额' }}</span><span class="v-v">{{ tx.offer_price }} 元</span>
            </div>
            <div class="v-txRow" v-if="tx.status"><span class="v-k">状态</span><span class="v-v"><span class="v-pill">{{ tx.status }}</span></span></div>
            <div class="v-txRow"><span class="v-k">交易哈希</span><span class="v-v v-hash">{{ tx.hash || '-' }}</span></div>
          </div>
        </div>
      </div>
    </article>
  </div>
  <div v-else class="v-empty">区块链为空</div>
</template>

<style scoped>
.v-list {
  display: grid;
  gap: 14px;
}

.v-block {
  border: 1px solid var(--border);
  border-radius: 12px;
  background: #fafafa;
  padding: 14px;
}

.v-blockHead {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.v-blockTitle {
  font-weight: 800;
  font-size: 15px;
}

.v-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 999px;
  background: #e5e7eb;
  color: #111827;
  font-size: 12px;
  font-weight: 700;
}

.v-dl {
  margin-top: 10px;
  display: grid;
  gap: 8px;
}

.v-dlRow {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 10px;
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: #fff;
}

dt {
  color: var(--muted);
  font-size: 12px;
}

dd {
  margin: 0;
  font-size: 13px;
}

.v-hash {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  word-break: break-all;
}

.v-txList {
  margin-top: 12px;
}

.v-txTitle {
  font-weight: 800;
  font-size: 14px;
}

.v-txGrid {
  margin-top: 10px;
  display: grid;
  gap: 10px;
}

.v-tx {
  border: 1px solid var(--border);
  border-radius: 12px;
  background: #fff;
  padding: 12px;
}

.v-txRow {
  display: grid;
  grid-template-columns: 90px 1fr;
  gap: 10px;
  padding: 4px 0;
}

.v-k {
  color: var(--muted);
  font-size: 12px;
}

.v-v {
  font-size: 13px;
}

.v-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
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

.v-empty {
  color: var(--muted);
  padding: 12px;
  border: 1px dashed var(--border);
  border-radius: 12px;
  background: #fff;
}

@media (max-width: 992px) {
  .v-dlRow {
    grid-template-columns: 1fr;
  }
  .v-txRow {
    grid-template-columns: 1fr;
  }
}
</style>

