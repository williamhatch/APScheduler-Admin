<template>
  <div class="jobs-container">
    <div class="page-header">
      <h2>任务管理</h2>
      <a-button type="primary" @click="$router.push('/jobs/create')">
        <plus-outlined /> 创建任务
      </a-button>
    </div>
    
    <div class="search-bar">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="任务名称">
          <a-input v-model:value="searchForm.name" placeholder="请输入任务名称" />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="searchForm.status" style="width: 120px" placeholder="请选择状态">
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="running">运行中</a-select-option>
            <a-select-option value="paused">已暂停</a-select-option>
            <a-select-option value="error">错误</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="fetchJobs">
            <search-outlined /> 搜索
          </a-button>
          <a-button style="margin-left: 8px" @click="resetSearch">
            重置
          </a-button>
        </a-form-item>
      </a-form>
    </div>
    
    <a-table
      :columns="columns"
      :data-source="jobs"
      :loading="loading"
      :pagination="pagination"
      @change="handleTableChange"
      row-key="id"
    >
      <!-- 任务名称列 -->
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'name'">
          <a @click="$router.push(`/jobs/edit/${record.id}`)">{{ record.name }}</a>
        </template>
        
        <!-- 触发器列 -->
        <template v-else-if="column.key === 'trigger'">
          <a-tag :color="getTriggerColor(record.trigger)">{{ record.trigger }}</a-tag>
          <a-tooltip :title="formatTriggerArgs(record.trigger_args)">
            <info-circle-outlined />
          </a-tooltip>
        </template>
        
        <!-- 下次运行时间列 -->
        <template v-else-if="column.key === 'next_run_time'">
          <span v-if="record.next_run_time">{{ formatDateTime(record.next_run_time) }}</span>
          <a-tag v-else color="red">未调度</a-tag>
        </template>
        
        <!-- 状态列 -->
        <template v-else-if="column.key === 'status'">
          <a-tag :color="getStatusColor(record.status)">{{ getStatusText(record.status) }}</a-tag>
        </template>
        
        <!-- 操作列 -->
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button v-if="record.status === 'running'" type="primary" size="small" @click="pauseJob(record.id)">
              <pause-outlined /> 暂停
            </a-button>
            <a-button v-else-if="record.status === 'paused'" type="primary" size="small" @click="resumeJob(record.id)">
              <play-circle-outlined /> 恢复
            </a-button>
            <a-button type="primary" size="small" @click="executeJob(record.id)">
              <thunderbolt-outlined /> 执行
            </a-button>
            <a-button type="primary" size="small" @click="$router.push(`/jobs/edit/${record.id}`)">
              <edit-outlined /> 编辑
            </a-button>
            <a-popconfirm
              title="确定要删除此任务吗？"
              ok-text="确定"
              cancel-text="取消"
              @confirm="deleteJob(record.id)"
            >
              <a-button type="primary" danger size="small">
                <delete-outlined /> 删除
              </a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { 
  PlusOutlined, 
  SearchOutlined, 
  PauseOutlined, 
  PlayCircleOutlined, 
  ThunderboltOutlined, 
  EditOutlined, 
  DeleteOutlined,
  InfoCircleOutlined
} from '@ant-design/icons-vue'
import { getJobs, updateJobStatus, executeJob as execJob, deleteJob as delJob } from '@/api/jobs'
import dayjs from 'dayjs'

// 表格列定义
const columns = [
  {
    title: '任务名称',
    dataIndex: 'name',
    key: 'name',
    sorter: true
  },
  {
    title: '触发器',
    dataIndex: 'trigger',
    key: 'trigger',
    filters: [
      { text: 'cron', value: 'cron' },
      { text: 'interval', value: 'interval' },
      { text: 'date', value: 'date' }
    ]
  },
  {
    title: '下次运行时间',
    dataIndex: 'next_run_time',
    key: 'next_run_time',
    sorter: true
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    filters: [
      { text: '运行中', value: 'running' },
      { text: '已暂停', value: 'paused' },
      { text: '错误', value: 'error' }
    ]
  },
  {
    title: '操作',
    key: 'action'
  }
]

// 任务数据
const jobs = ref([])
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  name: '',
  status: ''
})

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条记录`
})

// 获取任务列表
const fetchJobs = async (params = {}) => {
  try {
    loading.value = true
    
    // 构建查询参数
    const queryParams = {
      skip: ((pagination.current - 1) * pagination.pageSize),
      limit: pagination.pageSize,
      ...params
    }
    
    // 添加搜索条件
    if (searchForm.name) {
      queryParams.name = searchForm.name
    }
    if (searchForm.status) {
      queryParams.status = searchForm.status
    }
    
    // 调用API获取任务列表
    const data = await getJobs(queryParams)
    
    // 更新数据
    jobs.value = data
    pagination.total = data.length // 实际项目中应该从API响应中获取总数
  } catch (error) {
    console.error('获取任务列表失败:', error)
    message.error('获取任务列表失败')
  } finally {
    loading.value = false
  }
}

// 重置搜索条件
const resetSearch = () => {
  searchForm.name = ''
  searchForm.status = ''
  pagination.current = 1
  fetchJobs()
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
  if (filters.trigger) {
    params.trigger = filters.trigger
  }
  if (filters.status) {
    params.status = filters.status
  }
  
  fetchJobs(params)
}

// 暂停任务
const pauseJob = async (id) => {
  try {
    await updateJobStatus(id, 'paused')
    message.success('任务已暂停')
    fetchJobs()
  } catch (error) {
    console.error('暂停任务失败:', error)
    message.error('暂停任务失败')
  }
}

// 恢复任务
const resumeJob = async (id) => {
  try {
    await updateJobStatus(id, 'running')
    message.success('任务已恢复')
    fetchJobs()
  } catch (error) {
    console.error('恢复任务失败:', error)
    message.error('恢复任务失败')
  }
}

// 执行任务
const executeJob = async (id) => {
  try {
    await execJob(id)
    message.success('任务执行成功')
  } catch (error) {
    console.error('执行任务失败:', error)
    message.error('执行任务失败')
  }
}

// 删除任务
const deleteJob = async (id) => {
  try {
    await delJob(id)
    message.success('任务删除成功')
    fetchJobs()
  } catch (error) {
    console.error('删除任务失败:', error)
    message.error('删除任务失败')
  }
}

// 格式化日期时间
const formatDateTime = (dateTime) => {
  return dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss')
}

// 获取触发器颜色
const getTriggerColor = (trigger) => {
  const colors = {
    cron: 'blue',
    interval: 'green',
    date: 'orange'
  }
  return colors[trigger] || 'default'
}

// 获取状态颜色
const getStatusColor = (status) => {
  const colors = {
    running: 'green',
    paused: 'orange',
    error: 'red'
  }
  return colors[status] || 'default'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    running: '运行中',
    paused: '已暂停',
    error: '错误'
  }
  return texts[status] || status
}

// 格式化触发器参数
const formatTriggerArgs = (args) => {
  if (!args) return ''
  
  try {
    if (typeof args === 'string') {
      args = JSON.parse(args)
    }
    
    return Object.entries(args)
      .map(([key, value]) => `${key}: ${value}`)
      .join('\n')
  } catch (error) {
    return JSON.stringify(args)
  }
}

// 组件挂载时获取任务列表
onMounted(() => {
  fetchJobs()
})
</script>

<style scoped>
.jobs-container {
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

.search-bar {
  margin-bottom: 16px;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 4px;
}
</style>
