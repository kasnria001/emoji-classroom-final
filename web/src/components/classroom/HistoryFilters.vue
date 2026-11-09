<template>
  <n-space vertical>
    <n-space align="center" wrap>
      <n-date-picker
        :formatted-value="modelValue.range"
        type="datetimerange"
        value-format="yyyy-MM-dd HH:mm:ss"
        clearable
        :start-placeholder="t('history.from')"
        :end-placeholder="t('history.to')"
        @update:formatted-value="set('range', $event)"
      />
      <n-input-number
        v-if="teacher"
        :value="modelValue.user_id"
        :min="1"
        :precision="0"
        clearable
        :placeholder="t('history.studentId')"
        @update:value="set('user_id', $event)"
      />
      <n-select
        v-if="teacher"
        style="min-width: 180px"
        :value="modelValue.source"
        :options="sources"
        :placeholder="t('history.allSources')"
        clearable
        @update:value="set('source', $event)"
      />
      <n-button type="primary" @click="$emit('apply')">{{ t('history.search') }}</n-button>
      <n-button @click="$emit('reset')">{{ t('history.reset') }}</n-button>
    </n-space>
    <p>{{ t('history.rangeHint') }}</p>
  </n-space>
</template>
<script setup>
import { useI18n } from 'vue-i18n'
const props = defineProps({ modelValue: { type: Object, required: true }, teacher: Boolean })
const emit = defineEmits(['update:modelValue', 'apply', 'reset'])
const { t } = useI18n()
const sources = computed(() => [
  { label: t('history.manual'), value: 'MANUAL' },
  { label: t('history.ai'), value: 'AI' },
])
function set(key, value) {
  emit('update:modelValue', { ...props.modelValue, [key]: value })
}
</script>
