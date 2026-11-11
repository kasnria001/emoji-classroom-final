<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { NAlert, NButton, NCard, NEmpty, NInputNumber, NSelect, NSpace, NTag } from 'naive-ui'
import api from '@/api'
import { captureSession, isCurrentSession } from '@/utils/auth/session'
import { aiState, canControlAI } from '@/utils/ai'

const props = defineProps({ sessionId: { type: Number, default: null } })
const jobs = ref([])
const devices = ref([])
const profiles = ref([])
const deviceId = ref(null)
const profile = ref('edge')
const interval = ref(2)
const threshold = ref(0.7)
const loading = ref(false)
const pending = ref(false)
const error = ref('')
let sequence = 0
let timer
let requestId = null
const deviceOptions = computed(() => devices.value.filter((d) => d.enabled).map((d) => ({
  label: `#${d.id} ${d.name} · ${d.online ? '在线' : '离线'} · ${aiState[d.health] || d.health}`,
  value: d.id,
})))
const profileOptions = computed(() => profiles.value.map((p) => ({ label: `${p.id} · ${p.model_version}`, value: p.id })))

async function load() {
  if (loading.value || pending.value) return
  const id = props.sessionId
  const ticket = ++sequence
  const session = captureSession()
  const current = () => ticket === sequence && id === props.sessionId && isCurrentSession(session)
  loading.value = true
  try {
    const [j, d, p] = await Promise.all([api.getAIJobs(id), api.getAIDevices(), api.getAIProfiles()])
    if (!current()) return
    jobs.value = j.data || []
    devices.value = d.data || []
    profiles.value = p.data || []
    error.value = ''
  } catch (err) {
    if (current()) {
      jobs.value = []
      error.value = err.message || 'AI 状态加载失败'
    }
  } finally {
    if (current()) loading.value = false
  }
}

async function act(job, action) {
  if (pending.value || loading.value) return
  const id = props.sessionId
  const session = captureSession()
  pending.value = true
  error.value = ''
  let failure = ''
  try {
    if (job) {
      if (!canControlAI(job, action)) return
      await api.controlAIJob(job, action)
    } else {
      if (!id || !deviceId.value) throw new Error('先选择获准设备')
      // 同一配置失败重试沿用 request UUID，防止不确定的 HTTP 响应重复建任务。
      requestId ||= crypto.randomUUID()
      await api.createAIJob({
        request_id: requestId, session_id: id, device_id: deviceId.value, profile: profile.value,
        threshold: threshold.value, detection_threshold: 0.85,
        sample_interval: interval.value, max_faces: 10,
      })
      requestId = null
    }
  } catch (err) {
    failure = err.message || '操作失败；请刷新状态'
  } finally {
    if (id === props.sessionId && isCurrentSession(session)) {
      pending.value = false
      await load()
      if (id === props.sessionId && isCurrentSession(session) && failure) error.value = failure
    }
  }
}
watch([deviceId, profile, interval, threshold], () => { requestId = null })
watch(() => props.sessionId, () => {
  sequence++
  jobs.value = []
  loading.value = pending.value = false
  error.value = ''
  requestId = null
  if (timer) clearInterval(timer)
  load()
  timer = setInterval(load, 5000)
}, { immediate: true })
onBeforeUnmount(() => { sequence++; clearInterval(timer) })
</script>

<template>
  <NCard title="AI 课堂采集" size="small">
    <NSpace vertical>
      <NAlert type="info" :show-icon="false">
        由教室独立采集节点处理画面，不是学生网页摄像头。只上传匿名表情元数据；观测条数不代表学生人数，无人脸不会记为中性。
      </NAlert>
      <NAlert v-if="error" type="error">{{ error }}</NAlert>
      <NSpace v-if="sessionId" align="center" wrap>
        <NSelect v-model:value="deviceId" :options="deviceOptions" placeholder="选择获准设备" style="width: 280px" :disabled="pending" />
        <NSelect v-model:value="profile" :options="profileOptions" style="width: 240px" :disabled="pending" />
        <span>间隔（秒）</span><NInputNumber v-model:value="interval" :min="0.5" :max="60" :step="0.5" :disabled="pending" style="width: 100px" />
        <span>表情阈值</span><NInputNumber v-model:value="threshold" :min="0" :max="1" :step="0.05" :disabled="pending" style="width: 100px" />
        <NButton type="primary" :disabled="!deviceId || loading || pending" :loading="pending" @click="act(null)">创建 / 预检</NButton>
      </NSpace>
      <NButton :loading="loading" :disabled="pending" @click="load">刷新节点与任务</NButton>
      <NEmpty v-if="!jobs.length && !loading" description="暂无任务；未部署节点时手动反馈仍可使用" />
      <NCard v-for="job in jobs" :key="job.id" size="small" :title="`任务 #${job.id} · 课堂 #${job.session_id} · 设备 #${job.device_id}`">
        <NSpace vertical>
          <NSpace wrap>
            <NTag :type="job.observed === 'running' ? 'success' : 'default'">期望：{{ aiState[job.desired] || job.desired }} / 节点：{{ aiState[job.observed] || job.observed }}</NTag>
            <NTag :type="['no_frame','model_failed','degraded'].includes(job.health) ? 'error' : 'info'">{{ aiState[job.health] || job.health }}</NTag>
            <span>{{ job.profile }} · g{{ job.generation }} · 最近确认 {{ job.last_ack || '尚无' }}</span>
          </NSpace>
          <span>采样 {{ job.metrics?.sampled || 0 }} · 无脸 {{ job.metrics?.no_face || 0 }} · 过滤 {{ job.metrics?.filtered || 0 }} · 发布 {{ job.metrics?.published || 0 }} · 待补交 {{ job.metrics?.queue_size || 0 }} · 丢弃 {{ job.metrics?.dropped || 0 }} · 推理 {{ job.metrics?.inference_ms || 0 }} ms</span>
          <NSpace>
            <NButton :disabled="pending || loading || !canControlAI(job, 'start')" type="success" @click="act(job, 'start')">开始 / 恢复</NButton>
            <NButton :disabled="pending || loading || !canControlAI(job, 'pause')" @click="act(job, 'pause')">暂停</NButton>
            <NButton :disabled="pending || loading || !canControlAI(job, 'stop')" type="error" @click="act(job, 'stop')">停止</NButton>
          </NSpace>
        </NSpace>
      </NCard>
    </NSpace>
  </NCard>
</template>
