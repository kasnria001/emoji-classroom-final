import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router'
import { setupRouterGuard } from './guard'
import { basicRoutes, EMPTY_ROUTE, NOT_FOUND_ROUTE } from './routes'
import { getToken, isNullOrWhitespace } from '@/utils'
import { useUserStore, usePermissionStore } from '@/store'
import { BUSINESS_HOMES } from '@/utils/auth/business'
import { initializeSessionAccess } from '@/utils/auth/session'

const isHash = import.meta.env.VITE_USE_HASH === 'true'
export const router = createRouter({
  history: isHash ? createWebHashHistory('/') : createWebHistory('/'),
  routes: basicRoutes,
  scrollBehavior: () => ({ left: 0, top: 0 }),
})

export async function setupRouter(app) {
  try {
    await addDynamicRoutes()
  } catch {
    // Still mount the login page when restoring an expired session or offline.
  }
  setupRouterGuard(router)
  app.use(router)
}

export function resetRouter() {
  const basicRouteNames = getRouteNames(basicRoutes)
  router.getRoutes().forEach((route) => {
    const name = route.name
    if (!basicRouteNames.includes(name)) {
      router.removeRoute(name)
    }
  })
}

export async function addDynamicRoutes() {
  const token = getToken()

  // 未登录时只保留基础路由，避免提前请求用户菜单。
  if (isNullOrWhitespace(token)) {
    router.addRoute(EMPTY_ROUTE)
    return
  }
  // 登录后从后端加载菜单和 API 权限，再转换为动态路由。
  const userStore = useUserStore()
  const permissionStore = usePermissionStore()
  return initializeSessionAccess(userStore, permissionStore, (accessRoutes) => {
    accessRoutes.forEach((route) => {
      // A backend menu for a B entry must not replace its guarded static route.
      if (Object.values(BUSINESS_HOMES).includes(route.path)) return
      !router.hasRoute(route.name) && router.addRoute(route)
    })
    router.hasRoute(EMPTY_ROUTE.name) && router.removeRoute(EMPTY_ROUTE.name)
    router.addRoute(NOT_FOUND_ROUTE)
  })
}

export function getRouteNames(routes) {
  return routes.map((route) => getRouteName(route)).flat(1)
}

function getRouteName(route) {
  const names = [route.name]
  if (route.children && route.children.length) {
    names.push(...route.children.map((item) => getRouteName(item)).flat(1))
  }
  return names
}
