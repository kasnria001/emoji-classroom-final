<script setup>
import { h, onMounted, ref } from 'vue'
import { NButton, NInput, NInputNumber, NSelect, NTag } from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

import { formatDate, renderIcon } from '@/utils'
import api from '@/api'

defineOptions({ name: 'Emoji 数据' })

const EMOJI_MAP = {
  HAPPY: '😊',
  SAD: '😢',
  ANGRY: '😠',
  SURPRISED: '😲',
  NEUTRAL: '😐',
}

const emojiTypeOptions = Object.keys(EMOJI_MAP).map((key) => ({ label: `${EMOJI_MAP[key]} ${key}`, value: key }))
const sourceOptions = [
  { label: '手动 MANUAL', value: 'MANUAL' },
  { label: 'AI 推理', value: 'AI' },
]

const $table = ref(null)
const queryItems = ref({})
const exporting = ref(false)

onMounted(() => {
  $table.value?.handleSearch()
})

const columns = [
  { title: 'ID', key: 'id', width: 60, align: 'center' },
  { title: '用户', key: 'username', width: 120, align: 'center', render: (row) => row.username || '匿名' },
  { title: '课程', key: 'course_name', align: 'center', ellipsis: { tooltip: true } },
  { title: '班级', key: 'class_name', width: 120, align: 'center', ellipsis: { tooltip: true } },
  {
    title: '情绪',
    key: 'emoji_type',
    width: 110,
    align: 'center',
    render(row) {
      return h(
        NTag,
        { type: 'info' },
        { default: () => `${EMOJI_MAP[row.emoji_type] || ''} ${row.emoji_type}` }
      )
    },
  },
  {
    title: '来源',
    key: 'source',
    width: 90,
    align: 'center',
    render(row) {
      return h(NTag, { type: row.source === 'AI' ? 'warning' : 'success' }, { default: () => row.source })
    },
  },
  { title: '置信度', key: 'confidence', width: 90, align: 'center', render: (row) => (row.confidence ?? '') },
  { title: '设备来源', key: 'device_source', width: 110, align: 'center', ellipsis: { tooltip: true } },
  {
    title: '记录时间',
    key: 'timestamp',
    width: 180,
    align: 'center',
    render(row) {
      return formatDate(row.timestamp)
    },
  },
]

async function handleExport() {
  const params = {}
  Object.entries(queryItems.value).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      params[key] = value
    }
  })
  exporting.value = true
  try {
    const blob = await api.exportEmoji(params)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'emoji_records.csv'
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
    $message.success('导出成功')
  } catch (error) {
    $message.error(error.message || '导出失败')
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <CommonPage show-footer title="Emoji 数据">
    <template #action>
      <NButton type="primary" :loading="exporting" @click="handleExport">
        <TheIcon icon="material-symbols:download" :size="18" class="mr-5" />导出 CSV
      </NButton>
    </template>

    <CrudTable ref="$table" v-model:query-items="queryItems" :columns="columns" :get-data="api.getEmojiList">
      <template #queryBar>
        <QueryBarItem label="课堂ID" :label-width="60">
          <NInputNumber v-model:value="queryItems.session_id" clearable placeholder="课堂ID" />
        </QueryBarItem>
        <QueryBarItem label="用户ID" :label-width="60">
          <NInputNumber v-model:value="queryItems.user_id" clearable placeholder="用户ID" />
        </QueryBarItem>
        <QueryBarItem label="情绪" :label-width="60">
          <NSelect v-model:value="queryItems.emoji_type" clearable :options="emojiTypeOptions" placeholder="全部" />
        </QueryBarItem>
        <QueryBarItem label="来源" :label-width="60">
          <NSelect v-model:value="queryItems.source" clearable :options="sourceOptions" placeholder="全部" />
        </QueryBarItem>
      </template>
    </CrudTable>
  </CommonPage>
</template>
