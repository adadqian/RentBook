<script setup lang="ts">
type TextbookItem = {
  textbook_id: string
  created_at?: string
  location?: string
  description?: string
  photos?: string
}

defineProps<{
  textbooks?: TextbookItem[]
  photosOf: (tb: TextbookItem) => string[]
}>()
</script>

<template>
  <section class="v-card">
    <div class="v-cardHeader">
      <div>
        <div class="v-title">我发布的教材</div>
        <div class="v-sub">管理你发布的二手教材</div>
      </div>
      <a class="v-btn" href="/textbook/register">发布新教材</a>
    </div>

    <div v-if="textbooks?.length" class="v-list">
      <article v-for="tb in textbooks" :key="tb.textbook_id" class="v-item">
        <div class="v-itemTop">
          <div>
            <div class="v-itemTitle">
              教材ID <span class="v-mono">{{ tb.textbook_id }}</span>
            </div>
            <div class="v-meta">创建时间：{{ tb.created_at || '-' }}</div>
          </div>
          <a class="v-btn v-btnSecondary" :href="`/textbook/${tb.textbook_id}`">查看详情</a>
        </div>

        <div class="v-kvGrid">
          <div class="v-kv">
            <div class="v-k">位置</div>
            <div class="v-v">{{ tb.location || '无' }}</div>
          </div>
          <div class="v-kv">
            <div class="v-k">描述</div>
            <div class="v-v">{{ tb.description || '无' }}</div>
          </div>
        </div>

        <div v-if="photosOf(tb).length" class="v-photos" aria-label="教材照片">
          <img
            v-for="p in photosOf(tb)"
            :key="p"
            class="v-photo"
            :src="`/uploads/${p}`"
            alt="教材照片"
          />
        </div>
      </article>
    </div>
    <div v-else class="v-empty">暂无发布记录</div>
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

.v-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid transparent;
  background: var(--primary);
  color: #fff;
  text-decoration: none;
  cursor: pointer;
  transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
}

.v-btn:hover {
  background: var(--primaryHover);
  transform: translateY(-1px);
}

.v-btnSecondary {
  background: #111827;
}

.v-btnSecondary:hover {
  background: #0b1220;
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

.v-itemTop {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
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

.v-photos {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  margin-top: 10px;
  padding-bottom: 4px;
}

.v-photo {
  width: 96px;
  height: 96px;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: #fff;
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

