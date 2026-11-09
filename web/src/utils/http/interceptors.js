import { getToken } from '@/utils'
import { resolveResError } from './helpers'
import { useUserStore } from '@/store'

// Never allow logout/notification failures to turn a failed request into success.
function rejectResponse(code, message, config = {}, status) {
  if ((code === 401 || status === 401) && !config.noNeedToken) {
    const requestToken = config.headers?.token
    if (!requestToken || requestToken === getToken()) {
      try {
        Promise.resolve(useUserStore().logout()).catch(() => {})
      } catch {
        // The caller still receives the original request error.
      }
    }
  }
  const resolvedMessage = resolveResError(code, message)
  try {
    window.$message?.error(resolvedMessage, { keepAliveOnHover: true })
  } catch {
    // Toast availability must not change the request outcome.
  }
  // Do not retain Axios config/request bodies containing passwords in errors.
  return Promise.reject({ code, message: resolvedMessage })
}

export function reqResolve(config) {
  if (config.noNeedToken) return config
  const token = getToken()
  if (token) {
    config.headers = config.headers || {}
    config.headers.token = config.headers.token || token
  }
  return config
}

export function reqReject(error) {
  return Promise.reject(error)
}

export function resResolve(response) {
  const { data, status, statusText, config } = response
  // 文件下载（blob）响应直接透传，不做业务码解析。
  if (config?.responseType === 'blob' || data instanceof Blob) {
    return Promise.resolve(data)
  }
  if (data?.code !== 200) {
    return rejectResponse(data?.code ?? status, data?.msg ?? statusText, config, status)
  }
  return Promise.resolve(data)
}

export function resReject(error) {
  if (!error?.response) {
    return rejectResponse(error?.code, error?.message, error?.config)
  }
  const { data, status } = error.response
  return rejectResponse(data?.code ?? status, data?.msg ?? error.message, error.config, status)
}
