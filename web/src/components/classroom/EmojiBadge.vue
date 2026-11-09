<template>
  <n-tag
    >{{ emotion?.symbol }} {{ emotion ? t('history.emotions.' + value) : t('history.unknown') }} ({{
      value
    }})</n-tag
  >
</template>
<script setup>
import { EMOTIONS } from '@/utils/emoji'
import { useI18n } from 'vue-i18n'
const props = defineProps({ value: { type: String, default: '' } })
const { t } = useI18n()
const emotion = computed(() => EMOTIONS.find((item) => item.value === props.value))
</script>
