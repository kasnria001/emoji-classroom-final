<template>
  <AppPage :show-footer="true">
    <n-card class="m-auto max-w-460 rounded-10" :title="t('auth.register')">
      <n-alert v-if="!ready" type="info" mb-20 :title="t('auth.pendingTitle')">{{
        t('auth.registrationPending')
      }}</n-alert>
      <n-form
        ref="formRef"
        :model="form"
        :rules="rules"
        :disabled="loading"
        @submit.prevent="handleRegister"
      >
        <n-form-item path="username" :label="t('auth.username')">
          <n-input v-model:value="form.username" autocomplete="username" :maxlength="20" />
        </n-form-item>
        <n-form-item path="email" :label="t('auth.email')">
          <n-input v-model:value="form.email" autocomplete="email" :maxlength="255" />
        </n-form-item>
        <n-form-item path="password" :label="t('auth.password')">
          <n-input
            v-model:value="form.password"
            type="password"
            autocomplete="new-password"
            show-password-on="click"
          />
        </n-form-item>
        <n-form-item path="confirmation" :label="t('views.profile.label_confirm_password')">
          <n-input
            v-model:value="form.confirmation"
            type="password"
            autocomplete="new-password"
            show-password-on="click"
          />
        </n-form-item>
        <p mb-15 op-60>密码长度为 8–128 个字符。注册账号由服务端固定为学生。</p>
        <n-alert v-if="errorMessage" type="error" mb-15>{{ errorMessage }}</n-alert>
        <n-button
          attr-type="submit"
          block
          type="primary"
          :loading="loading"
          :disabled="loading || !ready"
          >{{ t('auth.register') }}</n-button
        >
      </n-form>
      <n-button text mt-15 type="primary" :disabled="loading" @click="router.push('/login')">{{
        t('auth.backToLogin')
      }}</n-button>
    </n-card>
  </AppPage>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import api from '@/api'
import { registrationReady, studentRegistrationContract } from '@/api/auth-contract'
import { samePassword, validEmail } from '@/utils/auth/forms'

const { t } = useI18n()
const router = useRouter()
const ready = registrationReady()
const formRef = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const form = reactive({ username: '', email: '', password: '', confirmation: '' })
const rules = computed(() => ({
  username: {
    required: true,
    whitespace: true,
    message: t('auth.required'),
    trigger: ['blur', 'input'],
  },
  email: [
    { required: true, message: t('auth.required'), trigger: ['blur', 'input'] },
    {
      validator: (_, value) => validEmail(value),
      message: t('auth.invalidEmail'),
      trigger: ['blur', 'input'],
    },
  ],
  password: [
    { required: true, message: t('auth.required'), trigger: ['blur', 'input'] },
    {
      validator: (_, value) =>
        !studentRegistrationContract.passwordValidator ||
        studentRegistrationContract.passwordValidator(value),
      message: t('auth.registrationPasswordPolicy'),
      trigger: ['blur', 'input'],
    },
  ],
  confirmation: [
    { required: true, message: t('auth.required'), trigger: ['blur', 'input'] },
    {
      validator: (_, value) => samePassword(form.password, value),
      message: t('auth.passwordMismatch'),
      trigger: ['blur', 'input'],
    },
  ],
}))
watch(
  () => form.password,
  () => formRef.value?.restoreValidation()
)

async function handleRegister() {
  if (loading.value) return
  errorMessage.value = ''
  if (!ready) {
    errorMessage.value = t('auth.registrationPending')
    return
  }
  loading.value = true
  try {
    await formRef.value.validate()
    await api.registerStudent(form)
    const username = form.username.trim()
    form.password = ''
    form.confirmation = ''
    $message.success(t('auth.registered'))
    await router.replace({ path: '/login', query: { username } })
  } catch (error) {
    // Axios exposes the backend message (including account/email conflicts).
    if (!Array.isArray(error)) errorMessage.value = error?.message || t('auth.requestFailed')
  } finally {
    loading.value = false
  }
}
</script>
