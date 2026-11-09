import i18n from '~/i18n'
import { useUserStore } from '@/store/modules/user'
const { t } = i18n.global

const Layout = () => import('@/layout/index.vue')

export const basicRoutes = [
  {
    name: 'Account',
    path: '/account',
    component: Layout,
    isHidden: true,
    children: [
      { path: '', name: 'AccountHome', component: () => import('@/views/account/index.vue') },
    ],
  },
  ...['STUDENT', 'TEACHER'].map((role) => ({
    name: 'Business-' + role,
    path: role === 'STUDENT' ? '/student/classroom' : '/teacher/classroom',
    component: Layout,
    meta: {
      title: t(role === 'STUDENT' ? 'auth.studentEntry' : 'auth.teacherEntry'),
      businessRole: role,
      icon: 'mdi:school-outline',
      order: 2,
    },
    children: [
      {
        path: '',
        name: 'BusinessHome-' + role,
        component:
          role === 'STUDENT'
            ? () => import('@/views/student/classroom/index.vue')
            : () => import('@/views/teacher/classroom/index.vue'),
        meta: { businessRole: role },
      },
    ],
  })),
  ...[
    {
      name: 'StudentHistory',
      path: '/student/history',
      role: 'STUDENT',
      component: () => import('@/views/student/history/index.vue'),
    },
    {
      name: 'TeacherClassroomDetail',
      path: '/teacher/classroom/detail',
      role: 'TEACHER',
      component: () => import('@/views/teacher/classroom-detail/index.vue'),
    },
  ].map((item) => ({
    name: item.name + 'Layout',
    path: item.path,
    component: Layout,
    isHidden: true,
    meta: { businessRole: item.role },
    children: [
      { path: '', name: item.name, component: item.component, meta: { businessRole: item.role } },
    ],
  })),
  {
    path: '/',
    redirect: () => useUserStore().defaultPath,
    meta: { order: 0 },
  },
  {
    name: t('views.workbench.label_workbench'),
    path: '/workbench',
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/workbench/index.vue'),
        name: `${t('views.workbench.label_workbench')}Default`,
        meta: {
          title: t('views.workbench.label_workbench'),
          icon: 'icon-park-outline:workbench',
          affix: true,
        },
      },
    ],
    meta: { order: 1 },
  },
  {
    name: t('views.profile.label_profile'),
    path: '/profile',
    component: Layout,
    isHidden: true,
    children: [
      {
        path: '',
        component: () => import('@/views/profile/index.vue'),
        name: `${t('views.profile.label_profile')}Default`,
        meta: {
          title: t('views.profile.label_profile'),
          icon: 'user',
          affix: true,
        },
      },
    ],
    meta: { order: 99 },
  },
  {
    name: 'ErrorPage',
    path: '/error-page',
    component: Layout,
    redirect: '/error-page/404',
    meta: {
      title: t('views.errors.label_error'),
      icon: 'mdi:alert-circle-outline',
      order: 99,
    },
    children: [
      {
        name: 'ERROR-401',
        path: '401',
        component: () => import('@/views/error-page/401.vue'),
        meta: {
          title: '401',
          icon: 'material-symbols:authenticator',
        },
      },
      {
        name: 'ERROR-403',
        path: '403',
        component: () => import('@/views/error-page/403.vue'),
        meta: {
          title: '403',
          icon: 'solar:forbidden-circle-line-duotone',
        },
      },
      {
        name: 'ERROR-404',
        path: '404',
        component: () => import('@/views/error-page/404.vue'),
        meta: {
          title: '404',
          icon: 'tabler:error-404',
        },
      },
      {
        name: 'ERROR-500',
        path: '500',
        component: () => import('@/views/error-page/500.vue'),
        meta: {
          title: '500',
          icon: 'clarity:rack-server-outline-alerted',
        },
      },
    ],
  },
  {
    name: '403',
    path: '/403',
    component: () => import('@/views/error-page/403.vue'),
    isHidden: true,
  },
  {
    name: '404',
    path: '/404',
    component: () => import('@/views/error-page/404.vue'),
    isHidden: true,
  },
  {
    name: 'Login',
    path: '/login',
    component: () => import('@/views/login/index.vue'),
    isHidden: true,
    meta: {
      title: '登录页',
    },
  },
  {
    name: 'Register',
    path: '/register',
    component: () => import('@/views/register/index.vue'),
    isHidden: true,
    meta: { title: t('auth.register') },
  },
]

export const NOT_FOUND_ROUTE = {
  name: 'NotFound',
  path: '/:pathMatch(.*)*',
  redirect: '/404',
  isHidden: true,
}

export const EMPTY_ROUTE = {
  name: 'Empty',
  path: '/:pathMatch(.*)*',
  component: null,
}

const modules = import.meta.glob('@/views/**/route.js', { eager: true })
const asyncRoutes = []
Object.keys(modules).forEach((key) => {
  asyncRoutes.push(modules[key].default)
})

// 加载 views 下每个模块的 index.vue 文件
const vueModules = import.meta.glob('@/views/**/index.vue')

export { asyncRoutes, vueModules }
