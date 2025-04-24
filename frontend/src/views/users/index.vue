<template>
  <div class="users-container">
    <div class="page-header">
      <h2>用户管理</h2>
      <a-button type="primary" @click="showCreateUserModal">
        <user-add-outlined /> 创建用户
      </a-button>
    </div>
    
    <a-table
      :columns="columns"
      :data-source="users"
      :loading="loading"
      :pagination="pagination"
      @change="handleTableChange"
      row-key="id"
    >
      <!-- 用户名列 -->
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'username'">
          <a @click="showUserDetail(record)">{{ record.username }}</a>
        </template>
        
        <!-- 邮箱列 -->
        <template v-else-if="column.key === 'email'">
          <a :href="`mailto:${record.email}`">{{ record.email }}</a>
        </template>
        
        <!-- 状态列 -->
        <template v-else-if="column.key === 'is_active'">
          <a-tag :color="record.is_active ? 'green' : 'red'">
            {{ record.is_active ? '已激活' : '未激活' }}
          </a-tag>
        </template>
        
        <!-- 角色列 -->
        <template v-else-if="column.key === 'is_superuser'">
          <a-tag :color="record.is_superuser ? 'blue' : ''">
            {{ record.is_superuser ? '超级管理员' : '普通用户' }}
          </a-tag>
        </template>
        
        <!-- 创建时间列 -->
        <template v-else-if="column.key === 'created_at'">
          {{ formatDateTime(record.created_at) }}
        </template>
        
        <!-- 操作列 -->
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button type="primary" size="small" @click="showEditUserModal(record)">
              <edit-outlined /> 编辑
            </a-button>
            <a-popconfirm
              title="确定要删除此用户吗？"
              ok-text="确定"
              cancel-text="取消"
              @confirm="deleteUser(record.id)"
            >
              <a-button type="primary" danger size="small" :disabled="record.id === currentUserId">
                <delete-outlined /> 删除
              </a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>
    
    <!-- 创建/编辑用户弹窗 -->
    <a-modal
      v-model:visible="userModalVisible"
      :title="isEdit ? '编辑用户' : '创建用户'"
      :confirm-loading="submitLoading"
      @ok="handleSubmitUser"
    >
      <a-form
        :model="userForm"
        :rules="rules"
        ref="userFormRef"
        layout="vertical"
      >
        <a-form-item label="用户名" name="username">
          <a-input v-model:value="userForm.username" placeholder="请输入用户名" />
        </a-form-item>
        
        <a-form-item label="邮箱" name="email">
          <a-input v-model:value="userForm.email" placeholder="请输入邮箱" />
        </a-form-item>
        
        <a-form-item label="密码" name="password" v-if="!isEdit">
          <a-input-password v-model:value="userForm.password" placeholder="请输入密码" />
        </a-form-item>
        
        <a-form-item label="新密码" name="password" v-else>
          <a-input-password v-model:value="userForm.password" placeholder="留空表示不修改密码" />
        </a-form-item>
        
        <a-form-item label="状态" name="is_active">
          <a-switch v-model:checked="userForm.is_active" />
          <span style="margin-left: 8px">{{ userForm.is_active ? '已激活' : '未激活' }}</span>
        </a-form-item>
        
        <a-form-item label="角色" name="is_superuser">
          <a-switch v-model:checked="userForm.is_superuser" />
          <span style="margin-left: 8px">{{ userForm.is_superuser ? '超级管理员' : '普通用户' }}</span>
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 用户详情弹窗 -->
    <a-modal
      v-model:visible="userDetailVisible"
      title="用户详情"
      :footer="null"
    >
      <a-descriptions bordered :column="1">
        <a-descriptions-item label="用户ID">{{ currentUser?.id }}</a-descriptions-item>
        <a-descriptions-item label="用户名">{{ currentUser?.username }}</a-descriptions-item>
        <a-descriptions-item label="邮箱">{{ currentUser?.email }}</a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="currentUser?.is_active ? 'green' : 'red'">
            {{ currentUser?.is_active ? '已激活' : '未激活' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="角色">
          <a-tag :color="currentUser?.is_superuser ? 'blue' : ''">
            {{ currentUser?.is_superuser ? '超级管理员' : '普通用户' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">{{ currentUser?.created_at ? formatDateTime(currentUser.created_at) : '-' }}</a-descriptions-item>
        <a-descriptions-item label="更新时间">{{ currentUser?.updated_at ? formatDateTime(currentUser.updated_at) : '-' }}</a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import { 
  UserAddOutlined, 
  EditOutlined, 
  DeleteOutlined 
} from '@ant-design/icons-vue'
import { getUsers, getUser, createUser, updateUser, deleteUser as delUser } from '@/api/users'
import { useUserStore } from '@/store/user'
import dayjs from 'dayjs'

// 用户状态
const userStore = useUserStore()

// 当前用户ID
const currentUserId = computed(() => userStore.userInfo?.id)

// 表格列定义
const columns = [
  {
    title: '用户ID',
    dataIndex: 'id',
    key: 'id',
    sorter: true
  },
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username',
    sorter: true
  },
  {
    title: '邮箱',
    dataIndex: 'email',
    key: 'email'
  },
  {
    title: '状态',
    dataIndex: 'is_active',
    key: 'is_active',
    filters: [
      { text: '已激活', value: true },
      { text: '未激活', value: false }
    ]
  },
  {
    title: '角色',
    dataIndex: 'is_superuser',
    key: 'is_superuser',
    filters: [
      { text: '超级管理员', value: true },
      { text: '普通用户', value: false }
    ]
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    sorter: true
  },
  {
    title: '操作',
    key: 'action'
  }
]

// 用户数据
const users = ref([])
const loading = ref(false)
const submitLoading = ref(false)

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条记录`
})

// 用户表单
const userFormRef = ref(null)
const userModalVisible = ref(false)
const isEdit = ref(false)
const userForm = reactive({
  username: '',
  email: '',
  password: '',
  is_active: true,
  is_superuser: false
})

// 用户详情
const userDetailVisible = ref(false)
const currentUser = ref(null)

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 32, message: '用户名长度必须在3-32个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: (form) => !isEdit.value, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ]
}

// 获取用户列表
const fetchUsers = async (params = {}) => {
  try {
    loading.value = true
    
    // 构建查询参数
    const queryParams = {
      skip: ((pagination.current - 1) * pagination.pageSize),
      limit: pagination.pageSize,
      ...params
    }
    
    // 调用API获取用户列表
    const data = await getUsers(queryParams)
    
    // 更新数据
    users.value = data
    pagination.total = data.length // 实际项目中应该从API响应中获取总数
  } catch (error) {
    console.error('获取用户列表失败:', error)
    message.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 表格变化处理
const handleTableChange = (pag, filters, sorter) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  
  const params = {}
  
  // 处理排序
  if (sorter.field) {
    params.sortField = sorter.field
    params.sortOrder = sorter.order
  }
  
  // 处理筛选
  if (filters.is_active) {
    params.is_active = filters.is_active
  }
  if (filters.is_superuser) {
    params.is_superuser = filters.is_superuser
  }
  
  fetchUsers(params)
}

// 显示创建用户弹窗
const showCreateUserModal = () => {
  isEdit.value = false
  
  // 重置表单
  Object.assign(userForm, {
    username: '',
    email: '',
    password: '',
    is_active: true,
    is_superuser: false
  })
  
  // 显示弹窗
  userModalVisible.value = true
}

// 显示编辑用户弹窗
const showEditUserModal = (record) => {
  isEdit.value = true
  
  // 设置表单数据
  Object.assign(userForm, {
    id: record.id,
    username: record.username,
    email: record.email,
    password: '',
    is_active: record.is_active,
    is_superuser: record.is_superuser
  })
  
  // 显示弹窗
  userModalVisible.value = true
}

// 显示用户详情
const showUserDetail = async (record) => {
  try {
    loading.value = true
    
    // 获取用户详情
    const data = await getUser(record.id)
    
    // 显示用户详情
    currentUser.value = data
    userDetailVisible.value = true
  } catch (error) {
    console.error('获取用户详情失败:', error)
    message.error('获取用户详情失败')
  } finally {
    loading.value = false
  }
}

// 提交用户表单
const handleSubmitUser = async () => {
  try {
    // 表单验证
    await userFormRef.value.validate()
    
    submitLoading.value = true
    
    // 构建提交数据
    const data = {
      username: userForm.username,
      email: userForm.email,
      is_active: userForm.is_active,
      is_superuser: userForm.is_superuser
    }
    
    // 如果有密码，添加到提交数据
    if (userForm.password) {
      data.password = userForm.password
    }
    
    // 提交数据
    if (isEdit.value) {
      await updateUser(userForm.id, data)
      message.success('用户更新成功')
    } else {
      await createUser(data)
      message.success('用户创建成功')
    }
    
    // 关闭弹窗并刷新列表
    userModalVisible.value = false
    fetchUsers()
  } catch (error) {
    console.error('提交用户表单失败:', error)
    message.error('提交用户表单失败: ' + (error.response?.data?.detail || '未知错误'))
  } finally {
    submitLoading.value = false
  }
}

// 删除用户
const deleteUser = async (id) => {
  try {
    // 不能删除自己
    if (id === currentUserId.value) {
      message.error('不能删除当前登录用户')
      return
    }
    
    await delUser(id)
    message.success('用户删除成功')
    fetchUsers()
  } catch (error) {
    console.error('删除用户失败:', error)
    message.error('删除用户失败')
  }
}

// 格式化日期时间
const formatDateTime = (dateTime) => {
  return dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss')
}

// 组件挂载时获取用户列表
onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.users-container {
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
