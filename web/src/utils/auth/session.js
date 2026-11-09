import { getToken } from '@/utils'

let generation = 0

export function captureSession() {
  return { generation, token: getToken() }
}

export function invalidateSession() {
  generation++
}

export function isCurrentSession(snapshot) {
  return snapshot.generation === generation && snapshot.token === getToken()
}

export function assertCurrentSession(snapshot) {
  if (!isCurrentSession(snapshot)) throw new Error('SESSION_CHANGED')
}

// Shared by the production router and tests; commit access only to its owning session.
export async function initializeSessionAccess(user, permission, install) {
  const session = captureSession()
  try {
    await user.getUserInfo()
    assertCurrentSession(session)
    const routes = await permission.generateRoutes()
    assertCurrentSession(session)
    await permission.getAccessApis()
    assertCurrentSession(session)
    install(routes)
  } catch (error) {
    if (isCurrentSession(session)) await user.logout({ redirect: false })
    throw error
  }
}
