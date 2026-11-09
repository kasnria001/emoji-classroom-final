import { EMOTIONS } from './emoji'

// Use wall-clock strings, not Date.toISOString(): the server expects Shanghai local time.
export function historyRange(range) {
  if (range == null) return {}
  if (!Array.isArray(range) || range.length !== 2) throw new Error('history.invalidRange')
  const pattern = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/
  const validDate = (value) => {
    if (typeof value !== 'string' || !pattern.test(value)) return false
    const [year, month, day, hour, minute, second] = value.split(/[- :]/).map(Number)
    const date = new Date(0)
    date.setUTCFullYear(year, month - 1, day)
    date.setUTCHours(hour, minute, second, 0)
    return (
      year > 0 &&
      date.getUTCFullYear() === year &&
      date.getUTCMonth() === month - 1 &&
      date.getUTCDate() === day &&
      date.getUTCHours() === hour &&
      date.getUTCMinutes() === minute &&
      date.getUTCSeconds() === second
    )
  }
  if (!range.every(validDate) || range[0] > range[1]) {
    throw new Error('history.invalidRange')
  }
  return { from_time: range[0], to_time: range[1] }
}

export function normalizeStatistics(data) {
  if (!Array.isArray(data)) throw new Error('history.invalidResponse')
  const counts = new Map()
  for (const row of data) {
    if (
      !row ||
      !EMOTIONS.some((item) => item.value === row.emoji_type) ||
      !Number.isSafeInteger(row.count) ||
      row.count < 0 ||
      counts.has(row.emoji_type)
    ) {
      throw new Error('history.invalidResponse')
    }
    counts.set(row.emoji_type, row.count)
  }
  const total = [...counts.values()].reduce((sum, count) => sum + count, 0)
  if (!Number.isSafeInteger(total)) throw new Error('history.invalidResponse')
  return {
    total,
    rows: EMOTIONS.map((item) => {
      const count = counts.get(item.value) || 0
      return { ...item, count, percentage: total ? Math.round((count * 10000) / total) / 100 : 0 }
    }),
  }
}
