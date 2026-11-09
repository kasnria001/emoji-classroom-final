import { getToken, isNullOrWhitespace } from '@/utils'
import { useUserStore } from '@/store'
import { canAccessBusinessRoute, getRouteBusinessRole } from '@/utils/auth/business'

const WHITE_LIST = ['/login', '/register', '/404']
export function createAuthGuard(router) {
  router.beforeEach((to) => {
    const userStore = useUserStore()
    if (isNullOrWhitespace(getToken())) {
      if (WHITE_LIST.includes(to.path)) return true
      return { path: '/login', query: { redirect: to.fullPath } }
    }
    if (['/login', '/register'].includes(to.path)) return userStore.defaultPath
    if (
      !canAccessBusinessRoute(to, userStore.userInfo) ||
      !to.matched.every((route) => canAccessBusinessRoute(route, userStore.userInfo))
    ) {
      return { path: '/403', replace: true }
    }
    const role = getRouteBusinessRole(to)
    if (role) userStore.switchBusinessRole(role)
    return true
  })
}
