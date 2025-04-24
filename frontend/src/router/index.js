import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: '/',
    component: () => import('@/layouts/BasicLayout.vue'),
    redirect: '/dashboard',
    meta: {
      requiresAuth: true
    },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: {
          title: '仪表盘',
          icon: 'dashboard'
        }
      },
      {
        path: 'jobs',
        name: 'Jobs',
        component: () => import('@/views/jobs/index.vue'),
        meta: {
          title: '任务管理',
          icon: 'schedule'
        }
      },
      {
        path: 'jobs/create',
        name: 'JobCreate',
        component: () => import('@/views/jobs/form.vue'),
        meta: {
          title: '创建任务',
          hideInMenu: true
        }
      },
      {
        path: 'jobs/edit/:id',
        name: 'JobEdit',
        component: () => import('@/views/jobs/form.vue'),
        meta: {
          title: '编辑任务',
          hideInMenu: true
        }
      },
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('@/views/logs/index.vue'),
        meta: {
          title: '日志管理',
          icon: 'file-text'
        }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/users/index.vue'),
        meta: {
          title: '用户管理',
          icon: 'user'
        }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/index.vue'),
        meta: {
          title: '系统设置',
          icon: 'setting'
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: {
      title: '404',
      hideInMenu: true
    }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - APScheduler管理系统` : 'APScheduler管理系统'
  
  // 检查是否需要认证
  if (to.meta.requiresAuth !== false) {
    const userStore = useUserStore()
    if (!userStore.token) {
      // 未登录，重定向到登录页
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }
  
  next()
})

export default router
