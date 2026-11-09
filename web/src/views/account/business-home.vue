<template>
  <CommonPage :title="t(isStudent ? 'auth.studentEntry' : 'auth.teacherEntry')">
    <n-alert type="info" :title="t('auth.pendingTitle')">{{
      t(isStudent ? 'auth.studentPending' : 'auth.teacherPending')
    }}</n-alert>
    <n-space mt-20>
      <n-button @click="router.push('/account')">{{ t('auth.switchEntry') }}</n-button>
      <n-button @click="router.push('/profile')">{{
        t('views.profile.label_change_password')
      }}</n-button>
    </n-space>
  </CommonPage>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import CommonPage from '@/components/page/CommonPage.vue'
const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const isStudent = computed(() => route.meta.businessRole === 'STUDENT')
</script>
