export const EMOTIONS = [
  { value: 'HAPPY', symbol: '😀', label: '开心' },
  { value: 'SAD', symbol: '😢', label: '难过' },
  { value: 'ANGRY', symbol: '😠', label: '生气' },
  { value: 'SURPRISED', symbol: '😮', label: '惊讶' },
  { value: 'NEUTRAL', symbol: '😐', label: '平静' },
]

export function emotionLabel(value) {
  const item = EMOTIONS.find((emotion) => emotion.value === value)
  return item ? item.symbol + ' ' + item.label : '未知情绪（' + String(value) + '）'
}

export function manualEmojiPayload(sessionId, emojiType) {
  if (
    !Number.isSafeInteger(sessionId) ||
    sessionId <= 0 ||
    !EMOTIONS.some((item) => item.value === emojiType)
  )
    throw new Error('请选择有效课堂和情绪')
  return { session_id: sessionId, emoji_type: emojiType, source: 'MANUAL' }
}

export function parseSessionId(value) {
  if (typeof value !== 'string' || !/^[1-9][0-9]*$/.test(value)) return null
  const id = Number(value)
  return Number.isSafeInteger(id) ? id : null
}

export function recordUserLabel(record) {
  return record.user_id == null ? '匿名' : record.username || '用户 #' + record.user_id
}
