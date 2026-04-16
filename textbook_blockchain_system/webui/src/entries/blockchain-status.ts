import { createApp } from 'vue'
import BlockchainStatusIsland from '@/islands/BlockchainStatusIsland.vue'

function getJsonFromScriptTag<T>(id: string): T | null {
  const el = document.getElementById(id)
  if (!el) return null
  const text = el.textContent || ''
  if (!text.trim()) return null
  try {
    return JSON.parse(text) as T
  } catch {
    return null
  }
}

const mountEl = document.getElementById('blockchain-status-app')
if (mountEl) {
  const legacy = document.getElementById('blockchain-status-legacy')
  if (legacy) legacy.style.display = 'none'
  const initial = getJsonFromScriptTag<Record<string, unknown>>(
    '__INITIAL_STATE__'
  )
  createApp(BlockchainStatusIsland, { initial }).mount(mountEl)
}
