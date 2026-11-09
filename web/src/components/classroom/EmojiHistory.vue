<template>
  <n-spin :show="loading">
    <n-alert v-if="error" type="error">{{ error }}</n-alert>
    <n-empty
      v-else-if="!loading && !rows.length"
      :description="t(filtered ? 'history.noMatches' : 'history.noRecords')"
    />
    <n-table v-else :single-line="false" style="display: block; overflow-x: auto">
      <thead>
        <tr>
          <th>{{ t('history.emotion') }}</th>
          <th>{{ t('history.time') }}</th>
          <th v-if="showClassroom">{{ t('history.classroom') }}</th>
          <th>{{ t('history.source') }}</th>
          <th v-if="showUser">{{ t('history.student') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.id">
          <td><EmojiBadge :value="row.emoji_type" /></td>
          <td>{{ row.timestamp || '—' }}</td>
          <td v-if="showClassroom">
            {{ classroomNames[row.session_id] || t('history.classroomId', { id: row.session_id }) }}
          </td>
          <td>
            {{
              t(
                row.source === 'MANUAL'
                  ? 'history.manual'
                  : row.source === 'AI'
                  ? 'history.ai'
                  : 'history.unknown'
              )
            }}
          </td>
          <td v-if="showUser">
            {{
              row.user_id == null
                ? t('history.anonymous')
                : row.username || t('history.userId', { id: row.user_id })
            }}
          </td>
        </tr>
      </tbody>
    </n-table>
  </n-spin>
</template>
<script setup>
import { useI18n } from 'vue-i18n'
import EmojiBadge from './EmojiBadge.vue'
const { t } = useI18n()
defineProps({
  rows: { type: Array, default: () => [] },
  loading: Boolean,
  error: { type: String, default: '' },
  showUser: Boolean,
  showClassroom: Boolean,
  filtered: Boolean,
  classroomNames: { type: Object, default: () => ({}) },
})
</script>
