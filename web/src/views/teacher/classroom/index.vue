<template>
  <CommonPage :title="t('classroom.teacherTitle')">
    <n-space vertical :size="18">
      <n-button :loading="courses.loading" @click="loadCourses">{{
        t('classroom.refreshCourses')
      }}</n-button>
      <n-alert v-if="courses.error" type="error">{{ courses.error }}</n-alert>
      <n-empty
        v-else-if="!courses.loading && !courses.rows.length"
        :description="t('classroom.noCourses')"
      />
      <n-select
        v-model:value="courseId"
        :options="courseOptions"
        :disabled="courses.loading"
        :placeholder="t('classroom.chooseCourse')"
      />
      <n-pagination
        v-if="courses.total"
        v-model:page="coursePage"
        :item-count="courses.total"
        :page-size="20"
        @update:page="loadCourses"
      />
      <n-button v-if="courseId" :loading="sessions.loading" @click="loadSessions">{{
        t('classroom.refresh')
      }}</n-button>
      <n-alert v-if="sessions.error" type="error">{{ sessions.error }}</n-alert>
      <n-empty
        v-else-if="courseId && !sessions.loading && !sessions.rows.length"
        :description="t('classroom.noSessions')"
      />
      <n-card v-for="item in sessions.rows" :key="item.id" size="small" :title="courseName">
        <p>
          {{ item.class_name || t('classroom.noClass') }} /
          {{ item.classroom || t('classroom.noRoom') }}
        </p>
        <p>{{ t('classroom.shanghai') }}: {{ item.start_time }} — {{ item.end_time }}</p>
        <n-button type="primary" text @click="open(item.id)">{{ t('classroom.details') }}</n-button>
      </n-card>
      <n-pagination
        v-if="sessions.total"
        v-model:page="sessionPage"
        :item-count="sessions.total"
        :page-size="20"
        @update:page="loadSessions"
      />
    </n-space>
  </CommonPage>
</template>
<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import CommonPage from '@/components/page/CommonPage.vue'
import { useBusinessList } from '@/composables/useBusinessList'
import api from '@/api'
const router = useRouter()
const courses = reactive(useBusinessList(api.getCourses))
const sessions = reactive(useBusinessList(api.getSessions))
const courseId = ref(null)
const coursePage = ref(1)
const sessionPage = ref(1)
const courseOptions = computed(() =>
  courses.rows.map((item) => ({ value: item.id, label: item.name }))
)
const courseName = computed(
  () => courses.rows.find((item) => item.id === courseId.value)?.name || t('classroom.classroom')
)
async function loadCourses() {
  courseId.value = null
  await courses.load({ page: coursePage.value })
}
function loadSessions() {
  return sessions.load({ course_id: courseId.value, page: sessionPage.value })
}
watch(courseId, (value) => {
  sessionPage.value = 1
  if (value) loadSessions()
  else sessions.clear()
})
async function open(id) {
  try {
    await router.push({ path: '/teacher/classroom/detail', query: { session_id: String(id) } })
  } catch {
    $message.error(t('classroom.navigationFailed'))
  }
}
onMounted(loadCourses)
</script>
