<template>
  <div class="dashboard-container">
    <div class="page-header">
      <h2>仪表盘</h2>
      <a-button type="primary" @click="refreshData">
        <reload-outlined /> 刷新数据
      </a-button>
    </div>
    
    <!-- 统计卡片 -->
    <a-row :gutter="16" class="stat-cards">
      <a-col :span="6">
        <a-card>
          <template #title>
            <schedule-outlined /> 任务总数
          </template>
          <a-statistic :value="stats.totalJobs" :loading="loading" />
          <template #extra>
            <a-button type="link" @click="$router.push('/jobs')">查看详情</a-button>
          </template>
        </a-card>
      </a-col>
      
      <a-col :span="6">
        <a-card>
          <template #title>
            <play-circle-outlined /> 运行中任务
          </template>
          <a-statistic :value="stats.runningJobs" :loading="loading" />
          <template #extra>
            <a-button type="link" @click="$router.push('/jobs?status=running')">查看详情</a-button>
          </template>
        </a-card>
      </a-col>
      
      <a-col :span="6">
        <a-card>
          <template #title>
            <pause-circle-outlined /> 已暂停任务
          </template>
          <a-statistic :value="stats.pausedJobs" :loading="loading" />
          <template #extra>
            <a-button type="link" @click="$router.push('/jobs?status=paused')">查看详情</a-button>
          </template>
        </a-card>
      </a-col>
      
      <a-col :span="6">
        <a-card>
          <template #title>
            <file-text-outlined /> 日志总数
          </template>
          <a-statistic :value="stats.totalLogs" :loading="loading" />
          <template #extra>
            <a-button type="link" @click="$router.push('/logs')">查看详情</a-button>
          </template>
        </a-card>
      </a-col>
    </a-row>
    
    <!-- 任务执行情况 -->
    <a-row :gutter="16" class="charts-row">
      <a-col :span="12">
        <a-card title="任务状态分布">
          <div class="chart-container" ref="statusChartRef"></div>
        </a-card>
      </a-col>
      
      <a-col :span="12">
        <a-card title="任务执行结果统计">
          <div class="chart-container" ref="resultChartRef"></div>
        </a-card>
      </a-col>
    </a-row>
    
    <!-- 最近任务执行日志 -->
    <a-card title="最近任务执行日志" class="recent-logs">
      <a-table
        :columns="logColumns"
        :data-source="recentLogs"
        :loading="loading"
        :pagination="false"
        size="small"
      >
        <!-- 任务ID列 -->
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'job_id'">
            <a @click="$router.push(`/jobs/edit/${record.job_id}`)">{{ record.job_id }}</a>
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
          
          <!-- 执行时长列 -->
          <template v-else-if="column.key === 'duration'">
            {{ record.duration ? `${record.duration.toFixed(2)}秒` : '-' }}
          </template>
          
          <!-- 操作列 -->
          <template v-else-if="column.key === 'action'">
            <a-button type="link" size="small" @click="$router.push('/logs')">
              查看详情
            </a-button>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { message } from 'ant-design-vue'
import { 
  ReloadOutlined, 
  ScheduleOutlined, 
  PlayCircleOutlined, 
  PauseCircleOutlined, 
  FileTextOutlined 
} from '@ant-design/icons-vue'
import { getJobs } from '@/api/jobs'
import { getLogs } from '@/api/logs'
import dayjs from 'dayjs'
import * as echarts from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { 
  TitleComponent, 
  TooltipComponent, 
  LegendComponent 
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// 注册 ECharts 组件
echarts.use([
  TitleComponent, 
  TooltipComponent, 
  LegendComponent, 
  PieChart, 
  CanvasRenderer
])

// 图表引用
const statusChartRef = ref(null)
const resultChartRef = ref(null)
let statusChart = null
let resultChart = null

// 加载状态
const loading = ref(false)

// 统计数据
const stats = reactive({
  totalJobs: 0,
  runningJobs: 0,
  pausedJobs: 0,
  totalLogs: 0
})

// 最近日志
const recentLogs = ref([])

// 日志表格列定义
const logColumns = [
  {
    title: '日志ID',
    dataIndex: 'id',
    key: 'id'
  },
  {
    title: '任务ID',
    dataIndex: 'job_id',
    key: 'job_id'
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status'
  },
  {
    title: '开始时间',
    dataIndex: 'start_time',
    key: 'start_time'
  },
  {
    title: '执行时长(秒)',
    dataIndex: 'duration',
    key: 'duration'
  },
  {
    title: '操作',
    key: 'action'
  }
]

// 获取仪表盘数据
const fetchDashboardData = async () => {
  try {
    loading.value = true
    
    // 获取任务数据
    let jobs = [];
    try {
      const jobsResponse = await getJobs({ limit: 1000 });
      console.log('获取到的任务数据:', jobsResponse);
      
      // 确保 jobs 是数组
      if (jobsResponse && jobsResponse.items && Array.isArray(jobsResponse.items)) {
        jobs = jobsResponse.items;
      } else if (Array.isArray(jobsResponse)) {
        jobs = jobsResponse;
      } else {
        console.error('任务数据格式不正确:', jobsResponse);
        jobs = [];
      }
    } catch (jobError) {
      console.error('获取任务数据失败:', jobError);
      jobs = [];
    }
    
    // 计算任务统计
    stats.totalJobs = jobs.length;
    stats.runningJobs = jobs.filter(job => job && job.status === 'running').length;
    stats.pausedJobs = jobs.filter(job => job && job.status === 'paused').length;
    
    // 获取日志数据
    let logs = [];
    try {
      const logsResponse = await getLogs({ limit: 10 });
      console.log('获取到的日志数据:', logsResponse);
      
      // 确保 logs 是数组
      if (logsResponse && logsResponse.items && Array.isArray(logsResponse.items)) {
        logs = logsResponse.items;
        stats.totalLogs = logsResponse.total || logs.length;
      } else if (Array.isArray(logsResponse)) {
        logs = logsResponse;
        stats.totalLogs = logs.length;
      } else {
        console.error('日志数据格式不正确:', logsResponse);
        logs = [];
        stats.totalLogs = 0;
      }
    } catch (logError) {
      console.error('获取日志数据失败:', logError);
      logs = [];
      stats.totalLogs = 0;
    }
    
    // 更新最近日志
    recentLogs.value = logs;
    
    // 更新图表
    updateCharts(jobs, logs);
  } catch (error) {
    console.error('获取仪表盘数据失败:', error);
    message.error('获取仪表盘数据失败');
  } finally {
    loading.value = false;
  }
};

// 刷新数据
const refreshData = () => {
  fetchDashboardData()
}

// 更新图表
const updateCharts = (jobs, logs) => {
  // 更新任务状态分布图表
  if (statusChart) {
    const statusData = [
      { value: stats.runningJobs, name: '运行中' },
      { value: stats.pausedJobs, name: '已暂停' },
      { value: stats.totalJobs - stats.runningJobs - stats.pausedJobs, name: '其他' }
    ]
    
    statusChart.setOption({
      series: [{
        data: statusData
      }]
    })
  }
  
  // 更新任务执行结果统计图表
  if (resultChart) {
    const successLogs = logs.filter(log => log.status === 'success').length
    const failedLogs = logs.filter(log => log.status === 'failed').length
    
    const resultData = [
      { value: successLogs, name: '成功' },
      { value: failedLogs, name: '失败' }
    ]
    
    resultChart.setOption({
      series: [{
        data: resultData
      }]
    })
  }
}

// 初始化图表
const initCharts = () => {
  // 初始化任务状态分布图表
  if (statusChartRef.value) {
    statusChart = echarts.init(statusChartRef.value)
    
    statusChart.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        data: ['运行中', '已暂停', '其他']
      },
      series: [
        {
          name: '任务状态',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '18',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: [
            { value: 0, name: '运行中' },
            { value: 0, name: '已暂停' },
            { value: 0, name: '其他' }
          ]
        }
      ]
    })
  }
  
  // 初始化任务执行结果统计图表
  if (resultChartRef.value) {
    resultChart = echarts.init(resultChartRef.value)
    
    resultChart.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        data: ['成功', '失败']
      },
      series: [
        {
          name: '执行结果',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '18',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: [
            { value: 0, name: '成功' },
            { value: 0, name: '失败' }
          ]
        }
      ]
    })
  }
}

// 格式化日期时间
const formatDateTime = (dateTime) => {
  return dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss')
}

// 窗口大小变化时重新调整图表大小
const handleResize = () => {
  if (statusChart) {
    statusChart.resize()
  }
  if (resultChart) {
    resultChart.resize()
  }
}

// 组件挂载时初始化图表并获取数据
onMounted(() => {
  initCharts()
  fetchDashboardData()
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理资源
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (statusChart) {
    statusChart.dispose()
    statusChart = null
  }
  if (resultChart) {
    resultChart.dispose()
    resultChart = null
  }
})
</script>

<style scoped>
.dashboard-container {
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

.stat-cards {
  margin-bottom: 16px;
}

.charts-row {
  margin-bottom: 16px;
}

.chart-container {
  height: 300px;
}

.recent-logs {
  margin-bottom: 16px;
}
</style>
