<template>
  <a-layout class="layout">
    <!-- 侧边栏 -->
    <a-layout-sider
      v-model:collapsed="collapsed"
      :trigger="null"
      collapsible
      class="sider"
    >
      <div class="logo">
        <h1 v-if="!collapsed">APScheduler 管理系统</h1>
        <h1 v-else>AP</h1>
      </div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="inline"
      >
        <a-menu-item key="dashboard" @click="() => $router.push('/dashboard')">
          <template #icon><dashboard-outlined /></template>
          <span>仪表盘</span>
        </a-menu-item>
        <a-menu-item key="jobs" @click="() => $router.push('/jobs')">
          <template #icon><schedule-outlined /></template>
          <span>任务管理</span>
        </a-menu-item>
        <a-menu-item key="logs" @click="() => $router.push('/logs')">
          <template #icon><file-text-outlined /></template>
          <span>日志管理</span>
        </a-menu-item>
        <a-menu-item key="users" @click="() => $router.push('/users')" v-if="userStore.isSuperuser">
          <template #icon><user-outlined /></template>
          <span>用户管理</span>
        </a-menu-item>
        <a-menu-item key="settings" @click="() => $router.push('/settings')">
          <template #icon><setting-outlined /></template>
          <span>系统设置</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    
    <!-- 内容区 -->
    <a-layout>
      <!-- 头部 -->
      <a-layout-header class="header">
        <div class="header-left">
          <menu-unfold-outlined
            v-if="collapsed"
            class="trigger"
            @click="() => (collapsed = !collapsed)"
          />
          <menu-fold-outlined
            v-else
            class="trigger"
            @click="() => (collapsed = !collapsed)"
          />
        </div>
        <div class="header-right">
          <a-dropdown>
            <a class="user-dropdown" @click.prevent>
              <a-avatar>{{ userStore.userInfo?.username?.charAt(0).toUpperCase() }}</a-avatar>
              <span class="username">{{ userStore.userInfo?.username }}</span>
            </a>
            <template #overlay>
              <a-menu>
                <a-menu-item key="profile" @click="() => $router.push('/settings')">
                  <user-outlined />
                  <span>个人设置</span>
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item key="logout" @click="handleLogout">
                  <logout-outlined />
                  <span>退出登录</span>
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>
      
      <!-- 内容 -->
      <a-layout-content class="content">
        <div class="content-wrapper">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </a-layout-content>
      
      <!-- 页脚 -->
      <a-layout-footer class="footer">
        APScheduler 管理系统 ©{{ new Date().getFullYear() }} Created by Your Company
      </a-layout-footer>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import {
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  DashboardOutlined,
  ScheduleOutlined,
  FileTextOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined
} from '@ant-design/icons-vue'

// 路由和用户状态
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 侧边栏折叠状态
const collapsed = ref(false)

// 当前选中的菜单项
const selectedKeys = ref([route.name])

// 监听路由变化，更新选中的菜单项
watch(
  () => route.name,
  (newVal) => {
    selectedKeys.value = [newVal]
  }
)

// 退出登录
const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

// 组件挂载时获取用户信息
onMounted(async () => {
  if (!userStore.userInfo) {
    try {
      await userStore.getUserInfo()
    } catch (error) {
      console.error('获取用户信息失败:', error)
      userStore.logout()
      router.push('/login')
    }
  }
})
</script>

<style scoped>
.layout {
  min-height: 100vh;
}

.sider {
  box-shadow: 2px 0 6px rgba(0, 21, 41, 0.35);
  z-index: 10;
}

.logo {
  height: 64px;
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #001529;
}

.logo h1 {
  color: white;
  font-size: 18px;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header {
  background: #fff;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  padding-right: 24px;
}

.trigger {
  font-size: 18px;
  line-height: 64px;
  padding: 0 24px;
  cursor: pointer;
  transition: color 0.3s;
}

.trigger:hover {
  color: #1890ff;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 8px;
}

.content {
  margin: 24px 16px;
  padding: 24px;
  background: #fff;
  min-height: 280px;
}

.content-wrapper {
  padding: 24px;
  background: #fff;
  border-radius: 2px;
}

.footer {
  text-align: center;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
