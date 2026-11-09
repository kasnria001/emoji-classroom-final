<template>
  <n-dropdown :options="options" @select="handleSelect">
    <div flex cursor-pointer items-center>
      <span>{{ userStore.name }}</span>
    </div>
  </n-dropdown>
</template>

<script setup>
import { useUserStore } from '@/store'
import { renderIcon } from '@/utils'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const router = useRouter()

const userStore = useUserStore()

const options = computed(() => [
  {
    label: t('header.label_profile'),
    key: 'profile',
    icon: renderIcon('mdi-account-arrow-right-outline', { size: '14px' }),
  },
  {
    label: t('header.label_logout'),
    key: 'logout',
    icon: renderIcon('mdi:exit-to-app', { size: '14px' }),
  },
])

async function handleSelect(key) {
  try {
    if (key === 'profile') {
      await router.push('/profile')
    } else if (key === 'logout') {
      $dialog.confirm({
        title: t('header.label_logout_dialog_title'),
        type: 'warning',
        content: t('header.text_logout_confirm'),
        async confirm() {
          try {
            await userStore.logout()
            $message.success(t('header.text_logout_success'))
          } catch {
            $message.error(t('auth.requestFailed'))
          }
        },
      })
    }
  } catch {
    $message.error(t('auth.requestFailed'))
  }
}
</script>
