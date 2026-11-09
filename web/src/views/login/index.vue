<template>
  <AppPage :show-footer="true" bg-cover :style="{ backgroundImage: 'url(' + bgImg + ')' }">
    <div
      class="m-auto max-w-1500 min-w-345 f-c-c rounded-10 bg-white bg-opacity-60 p-15 card-shadow"
      dark:bg-dark
    >
      <div hidden w-380 px-20 py-35 md:block>
        <icon-custom-front-page pt-10 text-300 color-primary />
      </div>
      <div w-320 flex-col px-20 py-35>
        <h5 f-c-c text-24 font-normal>
          <icon-custom-logo mr-10 text-50 color-primary />{{ $t('app_name') }}
        </h5>
        <n-form
          ref="formRef"
          mt-30
          :model="form"
          :rules="rules"
          :disabled="loading"
          @submit.prevent="handleLogin"
        >
          <n-form-item path="username" :label="t('auth.username')">
            <n-input
              v-model:value="form.username"
              autocomplete="username"
              :placeholder="t('auth.username')"
            />
          </n-form-item>
          <n-form-item path="password" :label="t('auth.password')">
            <n-input
              v-model:value="form.password"
              type="password"
              autocomplete="current-password"
              show-password-on="click"
              :placeholder="t('auth.password')"
            />
          </n-form-item>
          <n-alert v-if="errorMessage" type="error" mb-15>{{ errorMessage }}</n-alert>
          <n-button attr-type="submit" type="primary" block :loading="loading" :disabled="loading">
            {{ t('views.login.text_login') }}
          </n-button>
        </n-form>
        <n-button text mt-15 type="primary" :disabled="loading" @click="router.push('/register')">
          {{ t('auth.registerLink') }}
        </n-button>
      </div>
    </div>
  </AppPage>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { lStorage, setToken } from '@/utils'
import { clearLegacyPassword } from '@/utils/auth/forms'
import { getSafeRedirect } from '@/utils/auth/business'
import bgImg from '@/assets/images/login_bg.webp'
import api from '@/api'
import { useUserStore } from '@/store'
import { addDynamicRoutes } from '@/router'
import {
  captureSession,
  assertCurrentSession,
  isCurrentSession,
  invalidateSession,
} from '@/utils/auth/session'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const userStore = useUserStore()
clearLegacyPassword(lStorage)
const prefill = typeof route.query.username === 'string' ? route.query.username : ''
const form = reactive({ username: prefill, password: '' })
const formRef = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const rules = computed(() => ({
  username: {
    required: true,
    whitespace: true,
    message: t('auth.required'),
    trigger: ['blur', 'input'],
  },
  password: { required: true, message: t('auth.required'), trigger: ['blur', 'input'] },
}))

async function handleLogin() {
  if (loading.value) return
  loading.value = true
  errorMessage.value = ''
  let tokenReceived = false
  let session = captureSession()
  try {
    await formRef.value.validate()
    const res = await api.login({ username: form.username.trim(), password: form.password })
    assertCurrentSession(session)
    if (typeof res.data?.access_token !== 'string' || !res.data.access_token) {
      throw new Error(t('auth.loginFailed'))
    }
    invalidateSession()
    setToken(res.data.access_token)
    tokenReceived = true
    session = captureSession()
    await addDynamicRoutes()
    assertCurrentSession(session)
    const target =
      getSafeRedirect(route.query.redirect, router, userStore.userInfo) || userStore.defaultPath
    form.password = ''
    await router.replace(target)
    $message.success(t('views.login.message_login_success'))
  } catch (error) {
    if (tokenReceived && isCurrentSession(session)) await userStore.logout({ redirect: false })
    if (!Array.isArray(error)) {
      errorMessage.value = ['SESSION_CHANGED', 'USER_INFO_UNAVAILABLE'].includes(error?.message)
        ? t('auth.loginFailed')
        : error?.message || t('auth.loginFailed')
    }
  } finally {
    loading.value = false
  }
}
</script>
