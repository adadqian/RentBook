import { createApp } from 'vue'
import DashboardIsland from '@/islands/DashboardIsland.vue'

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

const mountEl = document.getElementById('dashboard-app')
if (mountEl) {
  const legacy = document.getElementById('dashboard-legacy')
  if (legacy) legacy.style.display = 'none'
  const initial = getJsonFromScriptTag<Record<string, unknown>>(
    '__INITIAL_STATE__'
  )
  createApp(DashboardIsland, { initial }).mount(mountEl)
}
