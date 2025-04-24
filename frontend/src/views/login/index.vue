<template>
  <div class="login-container">
    <div class="login-form-wrapper">
      <div class="login-header">
        <h1>APScheduler 管理系统</h1>
        <p>基于 APScheduler 的任务调度管理系统</p>
      </div>
      
      <a-form
        :model="loginForm"
        :rules="rules"
        ref="loginFormRef"
        class="login-form"
        @finish="handleSubmit"
      >
        <a-form-item name="username">
          <a-input
            v-model:value="loginForm.username"
            placeholder="用户名"
            size="large"
          >
            <template #prefix>
              <user-outlined />
            </template>
          </a-input>
        </a-form-item>
        
        <a-form-item name="password">
          <a-input-password
            v-model:value="loginForm.password"
            placeholder="密码"
            size="large"
          >
            <template #prefix>
              <lock-outlined />
            </template>
          </a-input-password>
        </a-form-item>
        
        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            size="large"
            :loading="loading"
            block
          >
            登录
          </a-button>
        </a-form-item>
        
        <div class="login-tip">
          <span>默认管理员账号: admin / admin</span>
        </div>
      </a-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { useUserStore } from '@/store/user'

// 路由和用户状态
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 表单引用
const loginFormRef = ref(null)

// 加载状态
const loading = ref(false)

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

// 提交表单
const handleSubmit = async (values) => {
  try {
    loading.value = true
    
    // 调用登录接口
    await userStore.login(values.username, values.password)
    
    // 获取用户信息
    await userStore.getUserInfo()
    
    message.success('登录成功')
    
    // 跳转到首页或重定向页面
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (error) {
    console.error('登录失败:', error)
    message.error('登录失败: ' + (error.response?.data?.detail || '用户名或密码错误'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
  background-image: url('https://gw.alipayobjects.com/zos/rmsportal/TVYTbAXWheQpRcWDaDMu.svg');
  background-repeat: no-repeat;
  background-position: center 110px;
  background-size: 100%;
}

.login-form-wrapper {
  width: 368px;
  margin: 0 auto;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h1 {
  font-size: 33px;
  color: rgba(0, 0, 0, 0.85);
  font-weight: 600;
  margin-bottom: 12px;
}

.login-header p {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.45);
  margin-bottom: 40px;
}

.login-form {
  width: 100%;
}

.login-tip {
  text-align: center;
  margin-top: 16px;
  color: rgba(0, 0, 0, 0.45);
}
</style>
