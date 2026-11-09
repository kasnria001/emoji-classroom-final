import { ref, getCurrentInstance, onBeforeUnmount } from 'vue'
import { captureSession, isCurrentSession } from '@/utils/auth/session'

// Requests are read-only. Only the latest request in the same session can update the UI.
export function useBusinessList(fetcher) {
  const rows = ref([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref('')
  let sequence = 0
  function clear() {
    sequence++
    rows.value = []
    total.value = 0
    error.value = ''
    loading.value = false
  }
  if (getCurrentInstance())
    onBeforeUnmount(() => {
      sequence++
    })
  async function load(params = {}) {
    const request = ++sequence
    const session = captureSession()
    loading.value = true
    error.value = ''
    rows.value = []
    total.value = 0
    const current = () => request === sequence && isCurrentSession(session)
    try {
      const res = await fetcher(params)
      if (!current()) return
      if (!Array.isArray(res.data) || !Number.isInteger(res.total) || res.total < 0) {
        throw new Error('列表响应格式不符合契约')
      }
      rows.value = res.data
      total.value = res.total
    } catch (err) {
      if (current()) error.value = err?.message || '加载失败，请手动重试'
    } finally {
      if (request === sequence) loading.value = false
    }
  }
  return { rows, total, loading, error, load, clear }
}
