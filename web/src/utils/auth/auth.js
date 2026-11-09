import { router } from '@/router'

export function toLogin() {
  const currentRoute = unref(router.currentRoute)
  const needRedirect = !['/404', '/403', '/login', '/register'].includes(currentRoute.path)
  return router.replace({
    path: '/login',
    query: needRedirect ? { redirect: currentRoute.fullPath } : {},
  })
}

export function toFourZeroFour() {
  router.replace({
    path: '/404',
  })
}
