<template>
  <div class="logs-container">
    <div class="page-header">
      <h2>日志管理</h2>
    </div>
    
    <div class="search-bar">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="任务ID">
          <a-input-number v-model:value="searchForm.job_id" placeholder="请输入任务ID" />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="searchForm.status" style="width: 120px" placeholder="请选择状态">
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="success">成功</a-select-option>
            <a-select-option value="failed">失败</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="时间范围">
          <a-range-picker 
            v-model:value="searchForm.dateRange" 
            format="YYYY-MM-DD HH:mm:ss"
            show-time
          />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="fetchLogs">
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
      :data-source="logs"
      :loading="loading"
      :pagination="pagination"
      @change="handleTableChange"
      row-key="id"
    >
      <!-- 任务ID列 -->
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'job_id'">
          <a-button type="link" @click="$router.push(`/jobs/edit/${record.job_id}`)">
            {{ record.job_id }}
          </a-button>
        </template>
        
        <!-- 状态列 -->
        <template v-else-if="column.key === 'status'">
          <a-tag :color="record.status === 'success' ? 'green' : 'red'">
            {{ record.status === 'success' ? '成功' : '失败' }}
          </a-tag>
        </template>
        
        <!-- 开始时间列 -->
        <template v-else-if="column.key === 'start_time'">
          {{ formatDateTime(record.start_time) }}
        </template>
        
        <!-- 结束时间列 -->
        <template v-else-if="column.key === 'end_time'">
          {{ record.end_time ? formatDateTime(record.end_time) : '-' }}
        </template>
        
        <!-- 执行时长列 -->
        <template v-else-if="column.key === 'duration'">
          {{ record.duration ? `${record.duration.toFixed(2)}秒` : '-' }}
        </template>
        
        <!-- 操作列 -->
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button type="primary" size="small" @click="showLogDetail(record)">
              <eye-outlined /> 查看详情
            </a-button>
            <a-popconfirm
              title="确定要删除此日志吗？"
              ok-text="确定"
              cancel-text="取消"
              @confirm="deleteLog(record.id)"
            >
              <a-button type="primary" danger size="small">
                <delete-outlined /> 删除
              </a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>
    
    <!-- 日志详情弹窗 -->
    <a-modal
      v-model:visible="logDetailVisible"
      title="日志详情"
      width="800px"
      :footer="null"
    >
      <a-descriptions bordered :column="1">
        <a-descriptions-item label="任务ID">{{ currentLog?.job_id }}</a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="currentLog?.status === 'success' ? 'green' : 'red'">
            {{ currentLog?.status === 'success' ? '成功' : '失败' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="开始时间">{{ currentLog?.start_time ? formatDateTime(currentLog.start_time) : '-' }}</a-descriptions-item>
        <a-descriptions-item label="结束时间">{{ currentLog?.end_time ? formatDateTime(currentLog.end_time) : '-' }}</a-descriptions-item>
        <a-descriptions-item label="执行时长">{{ currentLog?.duration ? `${currentLog.duration.toFixed(2)}秒` : '-' }}</a-descriptions-item>
        <a-descriptions-item label="错误信息">
          <a-typography-paragraph v-if="currentLog?.error_message" type="danger" style="margin-bottom: 0;">
            <pre>{{ currentLog.error_message }}</pre>
          </a-typography-paragraph>
          <span v-else>-</span>
        </a-descriptions-item>
        <a-descriptions-item label="输出信息">
          <a-typography-paragraph v-if="currentLog?.output" style="margin-bottom: 0;">
            <pre>{{ currentLog.output }}</pre>
          </a-typography-paragraph>
          <span v-else>-</span>
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { 
  SearchOutlined, 
  EyeOutlined, 
  DeleteOutlined 
} from '@ant-design/icons-vue'
import { getLogs, getLog, deleteLog as delLog } from '@/api/logs'
import dayjs from 'dayjs'

// 表格列定义
const columns = [
  {
    title: '日志ID',
    dataIndex: 'id',
    key: 'id',
    sorter: true
  },
  {
    title: '任务ID',
    dataIndex: 'job_id',
    key: 'job_id',
    sorter: true
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    filters: [
      { text: '成功', value: 'success' },
      { text: '失败', value: 'failed' }
    ]
  },
  {
    title: '开始时间',
    dataIndex: 'start_time',
    key: 'start_time',
    sorter: true
  },
  {
    title: '结束时间',
    dataIndex: 'end_time',
    key: 'end_time',
    sorter: true
  },
  {
    title: '执行时长(秒)',
    dataIndex: 'duration',
    key: 'duration',
    sorter: true
  },
  {
    title: '操作',
    key: 'action'
  }
]

// 日志数据
const logs = ref([])
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  job_id: null,
  status: '',
  dateRange: null
})

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条记录`
})

// 日志详情
const logDetailVisible = ref(false)
const currentLog = ref(null)

// 获取日志列表
const fetchLogs = async (params = {}) => {
  try {
    loading.value = true
    
    // 构建查询参数
    const queryParams = {
      skip: ((pagination.current - 1) * pagination.pageSize),
      limit: pagination.pageSize,
      ...params
    }
    
    // 添加搜索条件
    if (searchForm.job_id) {
      queryParams.job_id = searchForm.job_id
    }
    if (searchForm.status) {
      queryParams.status = searchForm.status
    }
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      queryParams.start_date = dayjs(searchForm.dateRange[0]).format('YYYY-MM-DD HH:mm:ss')
      queryParams.end_date = dayjs(searchForm.dateRange[1]).format('YYYY-MM-DD HH:mm:ss')
    }
    
    // 调用API获取日志列表
    const data = await getLogs(queryParams)
    
    // 更新数据
    logs.value = data
    pagination.total = data.length // 实际项目中应该从API响应中获取总数
  } catch (error) {
    console.error('获取日志列表失败:', error)
    message.error('获取日志列表失败')
  } finally {
    loading.value = false
  }
}

// 重置搜索条件
const resetSearch = () => {
  searchForm.job_id = null
  searchForm.status = ''
  searchForm.dateRange = null
  pagination.current = 1
  fetchLogs()
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
  if (filters.status) {
    params.status = filters.status
  }
  
  fetchLogs(params)
}

// 显示日志详情
const showLogDetail = async (record) => {
  try {
    loading.value = true
    
    // 获取日志详情
    const data = await getLog(record.id)
    
    // 显示日志详情
    currentLog.value = data
    logDetailVisible.value = true
  } catch (error) {
    console.error('获取日志详情失败:', error)
    message.error('获取日志详情失败')
  } finally {
    loading.value = false
  }
}

// 删除日志
const deleteLog = async (id) => {
  try {
    await delLog(id)
    message.success('日志删除成功')
    fetchLogs()
  } catch (error) {
    console.error('删除日志失败:', error)
    message.error('删除日志失败')
  }
}

// 格式化日期时间
const formatDateTime = (dateTime) => {
  return dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss')
}

// 组件挂载时获取日志列表
onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.logs-container {
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

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 300px;
  overflow-y: auto;
  margin: 0;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
}
</style>
