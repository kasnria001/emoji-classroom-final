<template>
  <CommonPage :title="t('history.studentTitle')">
    <n-space vertical :size="18">
      <p>{{ t('history.onlySelf') }}</p>
      <n-select
        v-model:value="selectedClass"
        :options="classOptions"
        clearable
        :placeholder="t('history.allClasses')"
        :loading="classes.loading"
      />
      <n-alert v-if="classes.error" type="warning">{{ classes.error }}</n-alert>
      <n-space align="center">
        <n-button :loading="classes.loading" @click="loadClasses">{{
          t('history.loadClasses')
        }}</n-button>
        <n-pagination
          v-if="classes.total"
          v-model:page="classPage"
          :item-count="classes.total"
          :page-size="20"
          @update:page="loadClasses"
        />
      </n-space>
      <HistoryFilters v-model="draft" @apply="apply" @reset="reset" />
      <n-button :loading="list.loading" @click="load">{{ t('history.refresh') }}</n-button>
      <EmojiHistory
        :rows="list.rows"
        :loading="list.loading"
        :error="filterError || list.error"
        :filtered="filtered"
        :classroom-names="classroomNames"
        show-classroom
      />
      <n-pagination
        v-if="list.total"
        v-model:page="page"
        :item-count="list.total"
        :page-size="20"
        @update:page="load"
      />
    </n-space>
  </CommonPage>
</template>
<script setup>
import { useI18n } from 'vue-i18n'
import CommonPage from '@/components/page/CommonPage.vue'
import EmojiHistory from '@/components/classroom/EmojiHistory.vue'
import HistoryFilters from '@/components/classroom/HistoryFilters.vue'
import { useBusinessList } from '@/composables/useBusinessList'
import { parseSessionId } from '@/utils/emoji'
import { historyRange } from '@/utils/history'
import api from '@/api'
const { t } = useI18n()
const route = useRoute()
const page = ref(1)
const classPage = ref(1)
const selectedClass = ref(null)
const draft = ref({ range: null })
const applied = ref({})
const filterError = ref('')
const list = reactive(useBusinessList(api.getMyEmojiHistory))
const classes = reactive(useBusinessList(api.getMySessions))
const classroomNames = computed(() =>
  Object.fromEntries(
    classes.rows.map((row) => [
      row.id,
      [
        row.course_name || t('history.classroomId', { id: row.id }),
        row.class_name || '—',
        row.start_time || '—',
      ].join(' / '),
    ])
  )
)
const classOptions = computed(() => {
  const options = classes.rows.map((row) => ({
    value: row.id,
    label: classroomNames.value[row.id],
  }))
  if (selectedClass.value && !options.some((item) => item.value === selectedClass.value))
    options.push({
      value: selectedClass.value,
      label: t('history.classroomId', { id: selectedClass.value }),
    })
  return options
})
const filtered = computed(() => Object.keys(applied.value).length > 0)
function loadClasses() {
  return classes.load({ page: classPage.value, page_size: 20 })
}
function load() {
  if (filterError.value) {
    list.clear()
    return
  }
  return list.load({ ...applied.value, page: page.value, page_size: 20 })
}
function apply() {
  list.clear()
  filterError.value = ''
  try {
    const range = historyRange(draft.value.range)
    const id = selectedClass.value == null ? null : parseSessionId(String(selectedClass.value))
    if (selectedClass.value != null && !id) throw new Error('history.invalidClassroom')
    applied.value = { ...range, ...(id ? { session_id: id } : {}) }
    page.value = 1
    return load()
  } catch (err) {
    filterError.value = t(err.message)
  }
}
function reset() {
  selectedClass.value = null
  draft.value = { range: null }
  return apply()
}
watch(
  () => route.query.session_id,
  (value) => {
    selectedClass.value = value == null ? null : parseSessionId(value)
    if (value != null && !selectedClass.value) {
      list.clear()
      filterError.value = t('history.invalidClassroom')
      return
    }
    apply()
  },
  { immediate: true }
)
onMounted(loadClasses)
</script>
