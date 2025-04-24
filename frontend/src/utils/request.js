import axios from 'axios'
import { message } from 'ant-design-vue'
import { getToken } from '@/utils/auth'
import { useUserStore } from '@/store/user'

// 创建axios实例
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 15000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 添加token到请求头
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    // 处理错误响应
    console.error('响应错误:', error)
    
    let errorMessage = '请求失败'
    
    if (error.response) {
      const { status, data } = error.response
      
      // 处理不同状态码
      switch (status) {
        case 400:
          errorMessage = data.detail || '请求参数错误'
          break
        case 401:
          errorMessage = '未授权，请重新登录'
          // 清除用户信息并跳转到登录页
          const userStore = useUserStore()
          userStore.logout()
          window.location.href = '/login'
          break
        case 403:
          errorMessage = '拒绝访问'
          break
        case 404:
          errorMessage = '请求的资源不存在'
          break
        case 500:
          errorMessage = '服务器内部错误'
          break
        default:
          errorMessage = `请求失败(${status})`
      }
      
      // 显示错误消息
      message.error(errorMessage)
    } else if (error.request) {
      // 请求已发送但没有收到响应
      errorMessage = '服务器无响应'
      message.error(errorMessage)
    } else {
      // 请求配置有误
      errorMessage = error.message
      message.error(errorMessage)
    }
    
    return Promise.reject(error)
  }
)

export default service
