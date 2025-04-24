<template>
  <div class="settings-container">
    <div class="page-header">
      <h2>系统设置</h2>
    </div>
    
    <a-tabs v-model:activeKey="activeTabKey">
      <!-- 个人信息设置 -->
      <a-tab-pane key="profile" tab="个人信息">
        <a-card>
          <a-form
            :model="profileForm"
            :rules="profileRules"
            ref="profileFormRef"
            layout="vertical"
            @finish="handleUpdateProfile"
          >
            <a-form-item label="用户名" name="username">
              <a-input v-model:value="profileForm.username" placeholder="请输入用户名" />
            </a-form-item>
            
            <a-form-item label="邮箱" name="email">
              <a-input v-model:value="profileForm.email" placeholder="请输入邮箱" />
            </a-form-item>
            
            <a-form-item label="新密码" name="password">
              <a-input-password v-model:value="profileForm.password" placeholder="留空表示不修改密码" />
            </a-form-item>
            
            <a-form-item>
              <a-button type="primary" html-type="submit" :loading="profileLoading">
                保存修改
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-tab-pane>
      
      <!-- 系统配置设置 -->
      <a-tab-pane key="system" tab="系统配置" v-if="userStore.isSuperuser">
        <a-card>
          <a-form
            :model="systemForm"
            ref="systemFormRef"
            layout="vertical"
            @finish="handleUpdateSystem"
          >
            <a-divider>数据库配置</a-divider>
            
            <a-form-item label="数据库类型" name="database_type">
              <a-select v-model:value="systemForm.database_type" placeholder="请选择数据库类型">
                <a-select-option value="mysql">MySQL</a-select-option>
                <a-select-option value="postgresql">PostgreSQL</a-select-option>
              </a-select>
            </a-form-item>
            
            <a-row :gutter="16" v-if="systemForm.database_type === 'mysql'">
              <a-col :span="12">
                <a-form-item label="MySQL 服务器" name="mysql_server">
                  <a-input v-model:value="systemForm.mysql_server" placeholder="请输入MySQL服务器地址" />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="MySQL 端口" name="mysql_port">
                  <a-input-number v-model:value="systemForm.mysql_port" :min="1" :max="65535" style="width: 100%" />
                </a-form-item>
              </a-col>
            </a-row>
            
            <a-row :gutter="16" v-if="systemForm.database_type === 'mysql'">
              <a-col :span="8">
                <a-form-item label="MySQL 用户名" name="mysql_user">
                  <a-input v-model:value="systemForm.mysql_user" placeholder="请输入MySQL用户名" />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="MySQL 密码" name="mysql_password">
                  <a-input-password v-model:value="systemForm.mysql_password" placeholder="请输入MySQL密码" />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="MySQL 数据库" name="mysql_db">
                  <a-input v-model:value="systemForm.mysql_db" placeholder="请输入MySQL数据库名" />
                </a-form-item>
              </a-col>
            </a-row>
            
            <a-row :gutter="16" v-if="systemForm.database_type === 'postgresql'">
              <a-col :span="12">
                <a-form-item label="PostgreSQL 服务器" name="postgres_server">
                  <a-input v-model:value="systemForm.postgres_server" placeholder="请输入PostgreSQL服务器地址" />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="PostgreSQL 端口" name="postgres_port">
                  <a-input-number v-model:value="systemForm.postgres_port" :min="1" :max="65535" style="width: 100%" />
                </a-form-item>
              </a-col>
            </a-row>
            
            <a-row :gutter="16" v-if="systemForm.database_type === 'postgresql'">
              <a-col :span="8">
                <a-form-item label="PostgreSQL 用户名" name="postgres_user">
                  <a-input v-model:value="systemForm.postgres_user" placeholder="请输入PostgreSQL用户名" />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="PostgreSQL 密码" name="postgres_password">
                  <a-input-password v-model:value="systemForm.postgres_password" placeholder="请输入PostgreSQL密码" />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="PostgreSQL 数据库" name="postgres_db">
                  <a-input v-model:value="systemForm.postgres_db" placeholder="请输入PostgreSQL数据库名" />
                </a-form-item>
              </a-col>
            </a-row>
            
            <a-divider>APScheduler 配置</a-divider>
            
            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="任务存储" name="apscheduler_jobstores">
                  <a-select v-model:value="systemForm.apscheduler_jobstores" placeholder="请选择任务存储">
                    <a-select-option value="default">默认 (SQLAlchemy)</a-select-option>
                    <a-select-option value="memory">内存</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="执行器" name="apscheduler_executors">
                  <a-select v-model:value="systemForm.apscheduler_executors" placeholder="请选择执行器">
                    <a-select-option value="default">默认 (ThreadPool)</a-select-option>
                    <a-select-option value="processpool">进程池</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>
            
            <a-row :gutter="16">
              <a-col :span="8">
                <a-form-item label="合并执行" name="job_coalesce">
                  <a-switch v-model:checked="systemForm.job_coalesce" />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="最大实例数" name="job_max_instances">
                  <a-input-number v-model:value="systemForm.job_max_instances" :min="1" :max="100" />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="线程池大小" name="threadpool_size">
                  <a-input-number v-model:value="systemForm.threadpool_size" :min="1" :max="100" />
                </a-form-item>
              </a-col>
            </a-row>
            
            <a-divider>系统安全配置</a-divider>
            
            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="JWT 密钥" name="secret_key">
                  <a-input-password v-model:value="systemForm.secret_key" placeholder="请输入JWT密钥" />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="令牌过期时间(分钟)" name="access_token_expire_minutes">
                  <a-input-number v-model:value="systemForm.access_token_expire_minutes" :min="1" :max="1440" style="width: 100%" />
                </a-form-item>
              </a-col>
            </a-row>
            
            <a-form-item>
              <a-button type="primary" html-type="submit" :loading="systemLoading">
                保存系统配置
              </a-button>
              <a-button style="margin-left: 8px" @click="resetSystemForm">
                重置
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-tab-pane>
      
      <!-- 关于系统 -->
      <a-tab-pane key="about" tab="关于系统">
        <a-card>
          <a-descriptions title="系统信息" bordered :column="1">
            <a-descriptions-item label="系统名称">APScheduler 管理系统</a-descriptions-item>
            <a-descriptions-item label="版本">1.0.0</a-descriptions-item>
            <a-descriptions-item label="后端框架">FastAPI</a-descriptions-item>
            <a-descriptions-item label="前端框架">Vue 3 + Ant Design Vue</a-descriptions-item>
            <a-descriptions-item label="任务调度库">APScheduler</a-descriptions-item>
            <a-descriptions-item label="数据库">MySQL / PostgreSQL</a-descriptions-item>
            <a-descriptions-item label="开源协议">MIT</a-descriptions-item>
            <a-descriptions-item label="项目地址">
              <a href="https://github.com/williamhatch/APScheduler-Admin" target="_blank">
                https://github.com/williamhatch/APScheduler-Admin
              </a>
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { useUserStore } from '@/store/user'
import { updateUserInfo } from '@/api/users'

// 用户状态
const userStore = useUserStore()

// 当前激活的标签页
const activeTabKey = ref('profile')

// 个人信息表单
const profileFormRef = ref(null)
const profileLoading = ref(false)
const profileForm = reactive({
  username: '',
  email: '',
  password: ''
})

// 个人信息表单验证规则
const profileRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 32, message: '用户名长度必须在3-32个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ]
}

// 系统配置表单
const systemFormRef = ref(null)
const systemLoading = ref(false)
const systemForm = reactive({
  database_type: 'mysql',
  mysql_server: 'localhost',
  mysql_port: 3306,
  mysql_user: 'root',
  mysql_password: '',
  mysql_db: 'apscheduler_admin',
  postgres_server: 'localhost',
  postgres_port: 5432,
  postgres_user: 'postgres',
  postgres_password: '',
  postgres_db: 'apscheduler_admin',
  apscheduler_jobstores: 'default',
  apscheduler_executors: 'default',
  job_coalesce: false,
  job_max_instances: 3,
  threadpool_size: 20,
  secret_key: '',
  access_token_expire_minutes: 60
})

// 初始化个人信息表单
const initProfileForm = () => {
  if (userStore.userInfo) {
    profileForm.username = userStore.userInfo.username
    profileForm.email = userStore.userInfo.email
    profileForm.password = ''
  }
}

// 更新个人信息
const handleUpdateProfile = async () => {
  try {
    profileLoading.value = true
    
    // 构建提交数据
    const data = {
      username: profileForm.username,
      email: profileForm.email
    }
    
    // 如果有密码，添加到提交数据
    if (profileForm.password) {
      data.password = profileForm.password
    }
    
    // 提交数据
    await updateUserInfo(data)
    
    // 更新用户信息
    await userStore.getUserInfo()
    
    message.success('个人信息更新成功')
  } catch (error) {
    console.error('更新个人信息失败:', error)
    message.error('更新个人信息失败: ' + (error.response?.data?.detail || '未知错误'))
  } finally {
    profileLoading.value = false
  }
}

// 更新系统配置
const handleUpdateSystem = async () => {
  try {
    systemLoading.value = true
    
    // 在实际项目中，这里应该调用API更新系统配置
    // 由于这是一个演示项目，这里只是模拟成功
    
    message.success('系统配置更新成功')
    
    // 提示需要重启服务器
    message.warning('部分配置需要重启服务器才能生效')
  } catch (error) {
    console.error('更新系统配置失败:', error)
    message.error('更新系统配置失败')
  } finally {
    systemLoading.value = false
  }
}

// 重置系统配置表单
const resetSystemForm = () => {
  // 重置为默认值
  Object.assign(systemForm, {
    database_type: 'mysql',
    mysql_server: 'localhost',
    mysql_port: 3306,
    mysql_user: 'root',
    mysql_password: '',
    mysql_db: 'apscheduler_admin',
    postgres_server: 'localhost',
    postgres_port: 5432,
    postgres_user: 'postgres',
    postgres_password: '',
    postgres_db: 'apscheduler_admin',
    apscheduler_jobstores: 'default',
    apscheduler_executors: 'default',
    job_coalesce: false,
    job_max_instances: 3,
    threadpool_size: 20,
    secret_key: '',
    access_token_expire_minutes: 60
  })
}

// 组件挂载时初始化表单
onMounted(() => {
  initProfileForm()
})
</script>

<style scoped>
.settings-container {
  padding: 0 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
}
</style>
