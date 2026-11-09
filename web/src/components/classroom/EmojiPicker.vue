<template>
  <n-space>
    <n-button
      v-for="item in EMOTIONS"
      :key="item.value"
      :type="modelValue === item.value ? 'primary' : 'default'"
      :aria-pressed="modelValue === item.value"
      :disabled="disabled"
      @click="$emit('update:modelValue', item.value)"
    >
      {{ item.symbol }} {{ t('history.emotions.' + item.value)
      }}{{ modelValue === item.value ? ' ✓' : '' }}
    </n-button>
  </n-space>
</template>
<script setup>
import { EMOTIONS } from '@/utils/emoji'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
defineProps({ modelValue: { type: String, default: '' }, disabled: Boolean })
defineEmits(['update:modelValue'])
</script>
