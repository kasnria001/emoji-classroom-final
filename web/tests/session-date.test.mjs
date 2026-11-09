// 功能测试：课堂与历史日期选择器的时间格式及编辑绑定。
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'

const require = createRequire(import.meta.url)
const { format, parse } = createRequire(require.resolve('naive-ui'))('date-fns')
const { parse: parseVue, compileScript } = require('vue/compiler-sfc')
const source = readFileSync(
  new URL('../src/views/classroom/session/index.vue', import.meta.url),
  'utf8'
)
const { descriptor } = parseVue(source)
const patterns = [...descriptor.template.content.matchAll(/value-format="([^"]+)"/g)].map(
  (match) => match[1]
)

test('both actual classroom picker formats preserve a literal T, with no epoch milliseconds', () => {
  assert.equal(patterns.length, 2)
  const date = new Date(2026, 10, 8, 22, 52, 38)
  for (const pattern of patterns) {
    const value = format(date, pattern)
    assert.equal(value, '2026-11-08T22:52:38')
    assert.equal(format(parse(value, pattern, new Date()), pattern), value)
  }
})

test('classroom edit action is bound by script setup', () => {
  const script = compileScript(descriptor, { id: 'classroom-date-test' })
  assert.ok(script.bindings.modalAction)
})

test('actual history range picker formats both endpoints as Shanghai wall-clock strings', () => {
  const source = readFileSync(
    new URL('../src/components/classroom/HistoryFilters.vue', import.meta.url),
    'utf8'
  )
  const { descriptor } = parseVue(source)
  const pattern = descriptor.template.content.match(/value-format="([^"]+)"/)[1]
  for (const [date, expected] of [
    [new Date(2026, 10, 9, 0, 0, 0), '2026-11-09 00:00:00'],
    [new Date(2026, 10, 9, 23, 59, 59), '2026-11-09 23:59:59'],
  ]) {
    const value = format(date, pattern)
    assert.equal(value, expected)
    assert.equal(format(parse(value, pattern, new Date()), pattern), value)
  }
})
