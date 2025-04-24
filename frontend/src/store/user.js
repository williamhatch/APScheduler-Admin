import { defineStore } from 'pinia'
import { login, getUserInfo } from '@/api/auth'
import { getToken, setToken, removeToken } from '@/utils/auth'

// 用户状态管理
export const useUserStore = defineStore('user', {
  state: () => ({
    token: getToken(),
    userInfo: null,
    roles: []
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    isSuperuser: (state) => state.roles.includes('superuser')
  },
  
  actions: {
    // 登录
    async login(username, password) {
      try {
        const response = await login(username, password)
        const { access_token } = response
        this.token = access_token
        setToken(access_token)
        return access_token
      } catch (error) {
        console.error('登录失败:', error)
        throw error
      }
    },
    
    // 获取用户信息
    async getUserInfo() {
      try {
        const userInfo = await getUserInfo()
        this.userInfo = userInfo
        this.roles = userInfo.is_superuser ? ['superuser'] : ['user']
        return userInfo
      } catch (error) {
        console.error('获取用户信息失败:', error)
        throw error
      }
    },
    
    // 登出
    logout() {
      this.token = null
      this.userInfo = null
      this.roles = []
      removeToken()
    },
    
    // 重置状态
    resetState() {
      this.token = getToken()
      this.userInfo = null
      this.roles = []
    }
  }
})
