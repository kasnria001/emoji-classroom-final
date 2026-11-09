import { defineStore } from 'pinia'
import { shallowRef } from 'vue'
import { basicRoutes, vueModules } from '@/router/routes'
import Layout from '@/layout/index.vue'
import api from '@/api'
import { useUserStore } from '@/store/modules/user'
import { filterBusinessMenus } from '@/utils/auth/business'
import { captureSession, assertCurrentSession } from '@/utils/auth/session'

// * 后端路由相关函数
// 根据后端传来数据构建出前端路由

function buildRoutes(routes = []) {
  return routes.map((e) => {
    const route = {
      name: e.name,
      path: e.path,
      component: shallowRef(Layout),
      isHidden: e.is_hidden,
      redirect: e.redirect,
      meta: {
        title: e.name,
        icon: e.icon,
        order: e.order,
        keepAlive: e.keepalive,
      },
      children: [],
    }

    if (e.children && e.children.length > 0) {
      // 有子菜单
      route.children = e.children.map((e_child) => ({
        name: e_child.name,
        path: e_child.path,
        component: vueModules[`/src/views${e_child.component}/index.vue`],
        isHidden: e_child.is_hidden,
        meta: {
          title: e_child.name,
          icon: e_child.icon,
          order: e_child.order,
          keepAlive: e_child.keepalive,
        },
      }))
    } else {
      // 没有子菜单，创建一个默认的子路由
      route.children.push({
        name: `${e.name}Default`,
        path: '',
        component: vueModules[`/src/views${e.component}/index.vue`],
        isHidden: true,
        meta: {
          title: e.name,
          icon: e.icon,
          order: e.order,
          keepAlive: e.keepalive,
        },
      })
    }

    return route
  })
}

export const usePermissionStore = defineStore('permission', {
  state() {
    return {
      accessRoutes: [],
      accessApis: [],
    }
  },
  getters: {
    routes() {
      return basicRoutes
        .concat(this.accessRoutes)
        .filter(
          (route, index, routes) => routes.findIndex((item) => item.path === route.path) === index
        )
    },
    menus() {
      const user = useUserStore().userInfo
      return filterBusinessMenus(this.routes, user).filter((route) => route.name && !route.isHidden)
    },
    apis() {
      return this.accessApis
    },
  },
  actions: {
    async generateRoutes() {
      const session = captureSession()
      const res = await api.getUserMenu() // 调用接口获取后端传来的菜单路由
      assertCurrentSession(session)
      if (!Array.isArray(res.data)) throw new Error('INVALID_MENU_RESPONSE')
      this.accessRoutes = buildRoutes(res.data) // 处理成前端路由格式
      return this.accessRoutes
    },
    async getAccessApis() {
      const session = captureSession()
      const res = await api.getUserApi()
      assertCurrentSession(session)
      if (!Array.isArray(res.data)) throw new Error('INVALID_API_RESPONSE')
      this.accessApis = res.data
      return this.accessApis
    },
    resetPermission() {
      this.$reset()
    },
  },
})
