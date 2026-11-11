<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { NAlert, NButton, NCard, NInput, NModal, NSpace, NTag, NPopconfirm } from 'naive-ui'
import CommonPage from '@/components/page/CommonPage.vue'
import { captureSession, isCurrentSession } from '@/utils/auth/session'
import { aiState, teacherIds } from '@/utils/ai'
import api from '@/api'
defineOptions({ name: 'AI设备' })
const devices = ref([])
const grants = ref({})
const name = ref('')
const alias = ref('')
const teachers = ref('')
const loading = ref(false)
const error = ref('')
const secret = ref('')
const secretVisible = ref(false)
let sequence = 0
onBeforeUnmount(() => { sequence++; secret.value = ''; secretVisible.value = false })

async function operation(fn) {
  if (loading.value) return
  const ticket = ++sequence
  const session = captureSession()
  const current = () => ticket === sequence && isCurrentSession(session)
  loading.value = true
  error.value = ''
  secret.value = ''
  secretVisible.value = false
  try {
    const result = fn ? await fn() : null
    if (!current()) return
    if (result?.data?.token) {
      secret.value = result.data.token
      secretVisible.value = true
    }
    const response = await api.getAIDevices()
    if (!current()) return
    devices.value = response.data || []
    grants.value = Object.fromEntries(devices.value.map((d) => [d.id, d.teacher_ids.join(',')]))
  } catch (err) {
    if (current()) error.value = err.message || '设备操作失败'
  } finally {
    if (current()) loading.value = false
  }
}
function create() {
  return operation(() => {
    if (!name.value.trim() || !/^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$/.test(alias.value))
      throw new Error('设备名称必填，source alias 仅允许字母、数字、点、下划线、连字符')
    return api.createAIDevice({ name: name.value.trim(), source_alias: alias.value, teacher_ids: teacherIds(teachers.value) })
  })
}
function save(device, enabled = device.enabled) {
  return operation(() => api.updateAIDevice(device.id, { enabled, teacher_ids: teacherIds(grants.value[device.id]) }))
}
onMounted(() => operation())
</script>
<template>
  <CommonPage title="AI 采集设备">
    <NSpace vertical :size="16">
      <NAlert type="info">管理员签发设备身份，教师只控制获准设备。source alias 对应节点本地输入，不在此填写含密码的摄像头 URL。</NAlert>
      <NAlert v-if="error" type="error">{{ error }}</NAlert>
      <NCard title="注册设备" size="small">
        <NSpace>
          <NInput v-model:value="name" placeholder="设备名称" :maxlength="80" :disabled="loading" />
          <NInput v-model:value="alias" placeholder="source alias，例如 camera-1" :maxlength="64" :disabled="loading" />
          <NInput v-model:value="teachers" placeholder="获准教师 ID，逗号分隔" :disabled="loading" />
          <NButton type="primary" :loading="loading" @click="create">注册</NButton>
          <NButton :disabled="loading" @click="operation()">刷新</NButton>
        </NSpace>
      </NCard>
      <NCard v-for="device in devices" :key="device.id" :title="`#${device.id} ${device.name} · ${device.source_alias}`" size="small">
        <NSpace vertical>
          <NSpace>
            <NTag :type="device.online ? 'success' : 'warning'">{{ device.online ? '在线' : '离线' }} · {{ device.enabled ? '启用' : '禁用' }}</NTag>
            <span>{{ aiState[device.health] || device.health }} · {{ device.profiles.join(', ') || '模型未准备' }} · {{ device.last_seen || '未连接' }}</span>
          </NSpace>
          <NSpace>
            <NInput v-model:value="grants[device.id]" placeholder="获准教师 ID" :disabled="loading" style="width: 220px" />
            <NButton :disabled="loading" @click="save(device)">保存授权</NButton>
            <NPopconfirm @positive-click="save(device, !device.enabled)">
              <template #trigger><NButton :disabled="loading">{{ device.enabled ? '禁用' : '启用' }}</NButton></template>
              禁用或移除教师授权会终止活动任务，确认修改？
            </NPopconfirm>
            <NPopconfirm @positive-click="operation(() => api.issueAICredential(device.id))">
              <template #trigger><NButton type="primary" :disabled="loading || !device.enabled">签发 / 轮换凭证</NButton></template>
              原凭证与活动任务会失效，新凭证仅显示一次，确认？
            </NPopconfirm>
            <NPopconfirm @positive-click="operation(() => api.revokeAICredential(device.id))">
              <template #trigger><NButton type="error" :disabled="loading">撤销凭证</NButton></template>
              所有凭证与活动租约立即失效，确认撤销？
            </NPopconfirm>
          </NSpace>
        </NSpace>
      </NCard>
    </NSpace>
    <NModal v-model:show="secretVisible" preset="card" title="一次性设备凭证" style="width: min(640px, 95vw)" @update:show="secret = ''">
      <NAlert type="info">仅此一次显示。保存到节点受限 secret 文件；关闭后无法再次读取，丢失请轮换。</NAlert>
      <pre style="white-space: pre-wrap; overflow-wrap: anywhere" data-testid="device-secret">{{ secret }}</pre>
      <NButton @click="secretVisible = false; secret = ''">已保存，关闭并清除</NButton>
    </NModal>
  </CommonPage>
</template>
