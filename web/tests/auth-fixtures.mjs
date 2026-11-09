// 测试辅助：认证状态、路由、存储与 API 请求替身。
import { useUserStore } from '../src/store/modules/user/index.js'
import { initializeSessionAccess } from '../src/utils/auth/session.js'

export { useUserStore }
export const state = {
  token: '',
  navigation: [],
  messages: [],
  calls: [],
  values: new Map(),
  userInfo: { id: 1, username: 'test', is_active: true },
  failUser: false,
  failInit: false,
  postError: null,
  postWait: null,
  resolutions: {},
  resetCount: 0,
  menuResetCount: 0,
  tagResetCount: 0,
}
export function resetFixture() {
  Object.assign(state, {
    token: '',
    navigation: [],
    messages: [],
    calls: [],
    values: new Map(),
    userInfo: { id: 1, username: 'test', is_active: true },
    failUser: false,
    failInit: false,
    postError: null,
    postWait: null,
    resolutions: {},
    resetCount: 0,
    menuResetCount: 0,
    tagResetCount: 0,
  })
  globalThis.window = { $message: { error: (message) => state.messages.push(message) } }
  globalThis.$message = { success: (message) => state.messages.push(message) }
}
export function getToken() {
  return state.token
}
export function setToken(value) {
  state.token = value
}
export function removeToken() {
  state.token = ''
}
export function isNullOrWhitespace(value) {
  return !value || !value.trim()
}
export function toLogin() {
  state.navigation.push('/login')
  return Promise.resolve()
}
export const lStorage = {
  get: (key) => state.values.get(key),
  set: (key, value) => state.values.set(key, value),
  remove: (key) => state.values.delete(key),
}
export const request = {
  get: async (path, config) => {
    state.calls.push({ method: 'get', path })
    if (state.getHandler) return state.getHandler(path, config)
    const data = path === '/base/usermenu' || path === '/base/userapi' ? [] : state.userInfo
    if (state.getWait) await state.getWait
    if (state.failUser) throw new Error('offline')
    return { code: 200, data }
  },
  post: async (path, data, config) => {
    state.calls.push({ method: 'post', path, data, config })
    if (state.postHandler) return state.postHandler(path, data, config)
    if (state.postWait) await state.postWait
    if (state.postError) throw state.postError
    return { code: 200, msg: 'OK', data: { access_token: 'test-jwt' } }
  },
}
export function resetRouter() {
  state.resetCount++
}
export async function addDynamicRoutes() {
  return initializeSessionAccess(
    useUserStore(),
    {
      async generateRoutes() {
        if (state.failInit) throw new Error('menu offline')
        return []
      },
      async getAccessApis() {},
    },
    () => {}
  )
}

export const basicRoutes = []
export const vueModules = {}
export const route = { query: {} }
export const router = {
  push: async (value) => {
    state.navigation.push(value)
  },
  replace: async (value) => {
    state.navigation.push(value)
  },
  resolve: (value) => state.resolutions[value] || { path: value, fullPath: value, matched: [] },
}
export function useRouter() {
  return router
}
export function useRoute() {
  return route
}
export function useI18n() {
  return { t: (key) => key }
}
export function useTagsStore() {
  return {
    resetTags: () => {
      state.tagResetCount++
      if (state.tagError) throw new Error('QuotaExceededError')
    },
  }
}
export function usePermissionStore() {
  return { resetPermission: () => state.menuResetCount++ }
}
export function renderIcon() {
  return () => null
}
