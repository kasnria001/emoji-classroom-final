<template>
  <n-spin :show="loading">
    <n-alert v-if="error" type="error">{{ error }}</n-alert>
    <template v-else-if="summary">
      <n-statistic :label="t('history.totalRecords')" :value="summary.total" />
      <p>
        {{
          t(
            source === 'MANUAL'
              ? 'history.manualOnly'
              : source === 'AI'
              ? 'history.aiOnly'
              : 'history.bothSources'
          )
        }}
      </p>
      <n-empty v-if="summary.total === 0" :description="t('history.noStatistics')" />
      <n-space vertical>
        <div v-for="item in summary.rows" :key="item.value">
          <span
            >{{ item.symbol }} {{ t('history.emotions.' + item.value) }}：{{ item.count }}（{{
              item.percentage
            }}%）</span
          >
          <n-progress type="line" :percentage="item.percentage" :show-indicator="false" />
        </div>
      </n-space>
    </template>
  </n-spin>
</template>
<script setup>
import { useI18n } from 'vue-i18n'
defineProps({
  summary: { type: Object, default: null },
  loading: Boolean,
  error: { type: String, default: '' },
  source: { type: String, default: null },
})
const { t } = useI18n()
</script>
