<template>
  <div class="job-form-container">
    <div class="page-header">
      <h2>{{ isEdit ? '编辑任务' : '创建任务' }}</h2>
      <a-button @click="$router.push('/jobs')">
        <arrow-left-outlined /> 返回列表
      </a-button>
    </div>
    
    <a-form
      :model="jobForm"
      :rules="rules"
      ref="jobFormRef"
      layout="vertical"
      @finish="handleSubmit"
    >
      <!-- 基本信息 -->
      <a-divider>基本信息</a-divider>
      
      <a-row :gutter="16">
        <a-col :span="12">
          <a-form-item label="任务名称" name="name">
            <a-input v-model:value="jobForm.name" placeholder="请输入任务名称" />
          </a-form-item>
        </a-col>
        
        <a-col :span="12">
          <a-form-item label="任务函数" name="func">
            <a-input v-model:value="jobForm.func" placeholder="请输入任务函数路径，例如：app.tasks.send_email" />
          </a-form-item>
        </a-col>
      </a-row>
      
      <a-row :gutter="16">
        <a-col :span="24">
          <a-form-item label="任务描述" name="description">
            <a-textarea v-model:value="jobForm.description" placeholder="请输入任务描述" :rows="3" />
          </a-form-item>
        </a-col>
      </a-row>
      
      <!-- 触发器配置 -->
      <a-divider>触发器配置</a-divider>
      
      <a-row :gutter="16">
        <a-col :span="12">
          <a-form-item label="触发器类型" name="trigger">
            <a-select v-model:value="jobForm.trigger" placeholder="请选择触发器类型" @change="handleTriggerChange">
              <a-select-option value="cron">Cron 表达式</a-select-option>
              <a-select-option value="interval">时间间隔</a-select-option>
              <a-select-option value="date">指定日期</a-select-option>
            </a-select>
          </a-form-item>
        </a-col>
      </a-row>
      
      <!-- Cron 触发器配置 -->
      <template v-if="jobForm.trigger === 'cron'">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="Cron 表达式" name="cronExpression">
              <a-input v-model:value="triggerArgs.cronExpression" placeholder="请输入 Cron 表达式，例如：0 0 * * *" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="时区" name="timezone">
              <a-input v-model:value="triggerArgs.timezone" placeholder="请输入时区，例如：Asia/Shanghai" />
            </a-form-item>
          </a-col>
        </a-row>
      </template>
      
      <!-- 间隔触发器配置 -->
      <template v-if="jobForm.trigger === 'interval'">
        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="间隔天数" name="days">
              <a-input-number v-model:value="triggerArgs.days" :min="0" placeholder="天" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="间隔小时" name="hours">
              <a-input-number v-model:value="triggerArgs.hours" :min="0" placeholder="小时" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="间隔分钟" name="minutes">
              <a-input-number v-model:value="triggerArgs.minutes" :min="0" placeholder="分钟" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="间隔秒数" name="seconds">
              <a-input-number v-model:value="triggerArgs.seconds" :min="0" placeholder="秒" />
            </a-form-item>
          </a-col>
          <a-col :span="16">
            <a-form-item label="开始时间" name="start_date">
              <a-date-picker 
                v-model:value="triggerArgs.start_date" 
                show-time 
                format="YYYY-MM-DD HH:mm:ss" 
                placeholder="请选择开始时间"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>
      </template>
      
      <!-- 日期触发器配置 -->
      <template v-if="jobForm.trigger === 'date'">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="执行时间" name="run_date">
              <a-date-picker 
                v-model:value="triggerArgs.run_date" 
                show-time 
                format="YYYY-MM-DD HH:mm:ss" 
                placeholder="请选择执行时间"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="时区" name="timezone">
              <a-input v-model:value="triggerArgs.timezone" placeholder="请输入时区，例如：Asia/Shanghai" />
            </a-form-item>
          </a-col>
        </a-row>
      </template>
      
      <!-- 高级配置 -->
      <a-divider>高级配置</a-divider>
      
      <a-row :gutter="16">
        <a-col :span="8">
          <a-form-item label="最大实例数" name="max_instances">
            <a-input-number v-model:value="jobForm.max_instances" :min="1" :max="100" />
          </a-form-item>
        </a-col>
        <a-col :span="8">
          <a-form-item label="错过执行时间的宽限期(秒)" name="misfire_grace_time">
            <a-input-number v-model:value="jobForm.misfire_grace_time" :min="1" />
          </a-form-item>
        </a-col>
        <a-col :span="8">
          <a-form-item label="合并执行" name="coalesce">
            <a-switch v-model:checked="jobForm.coalesce" />
          </a-form-item>
        </a-col>
      </a-row>
      
      <a-row :gutter="16">
        <a-col :span="24">
          <a-form-item label="参数 (JSON 格式)" name="args">
            <a-textarea v-model:value="argsJson" placeholder="请输入参数，例如：[1, 2, 3]" :rows="3" />
          </a-form-item>
        </a-col>
      </a-row>
      
      <a-row :gutter="16">
        <a-col :span="24">
          <a-form-item label="关键字参数 (JSON 格式)" name="kwargs">
            <a-textarea v-model:value="kwargsJson" placeholder="请输入关键字参数，例如：{&quot;name&quot;: &quot;value&quot;}" :rows="3" />
          </a-form-item>
        </a-col>
      </a-row>
      
      <!-- 提交按钮 -->
      <a-form-item>
        <a-button type="primary" html-type="submit" :loading="loading">
          {{ isEdit ? '保存修改' : '创建任务' }}
        </a-button>
        <a-button style="margin-left: 8px" @click="$router.push('/jobs')">
          取消
        </a-button>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { ArrowLeftOutlined } from '@ant-design/icons-vue'
import { getJob, createJob, updateJob } from '@/api/jobs'
import dayjs from 'dayjs'

// 路由
const route = useRoute()
const router = useRouter()

// 表单引用
const jobFormRef = ref(null)

// 加载状态
const loading = ref(false)

// 是否为编辑模式
const isEdit = computed(() => !!route.params.id)

// 任务表单数据
const jobForm = reactive({
  name: '',
  func: '',
  description: '',
  trigger: 'cron',
  max_instances: 1,
  misfire_grace_time: 60,
  coalesce: false
})

// 触发器参数
const triggerArgs = reactive({
  // Cron 触发器参数
  cronExpression: '',
  timezone: 'Asia/Shanghai',
  
  // 间隔触发器参数
  days: 0,
  hours: 0,
  minutes: 0,
  seconds: 0,
  start_date: null,
  
  // 日期触发器参数
  run_date: null
})

// 参数和关键字参数的 JSON 字符串
const argsJson = ref('[]')
const kwargsJson = ref('{}')

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' }
  ],
  func: [
    { required: true, message: '请输入任务函数', trigger: 'blur' }
  ],
  trigger: [
    { required: true, message: '请选择触发器类型', trigger: 'change' }
  ]
}

// 处理触发器类型变更
const handleTriggerChange = () => {
  // 重置触发器参数
  if (jobForm.trigger === 'cron') {
    triggerArgs.cronExpression = ''
    triggerArgs.timezone = 'Asia/Shanghai'
  } else if (jobForm.trigger === 'interval') {
    triggerArgs.days = 0
    triggerArgs.hours = 0
    triggerArgs.minutes = 0
    triggerArgs.seconds = 0
    triggerArgs.start_date = null
  } else if (jobForm.trigger === 'date') {
    triggerArgs.run_date = null
    triggerArgs.timezone = 'Asia/Shanghai'
  }
}

// 获取触发器参数
const getTriggerArgs = () => {
  if (jobForm.trigger === 'cron') {
    return {
      year: null,
      month: null,
      day: null,
      week: null,
      day_of_week: null,
      hour: null,
      minute: null,
      second: null,
      start_date: null,
      end_date: null,
      timezone: triggerArgs.timezone,
      jitter: null,
      ...parseCronExpression(triggerArgs.cronExpression)
    }
  } else if (jobForm.trigger === 'interval') {
    return {
      weeks: 0,
      days: triggerArgs.days || 0,
      hours: triggerArgs.hours || 0,
      minutes: triggerArgs.minutes || 0,
      seconds: triggerArgs.seconds || 0,
      start_date: triggerArgs.start_date ? dayjs(triggerArgs.start_date).format('YYYY-MM-DD HH:mm:ss') : null,
      end_date: null,
      timezone: null,
      jitter: null
    }
  } else if (jobForm.trigger === 'date') {
    return {
      run_date: triggerArgs.run_date ? dayjs(triggerArgs.run_date).format('YYYY-MM-DD HH:mm:ss') : null,
      timezone: triggerArgs.timezone
    }
  }
  return {}
}

// 解析 Cron 表达式（简化版）
const parseCronExpression = (cronExpression) => {
  // 这里简化处理，实际项目中应该有更完善的 Cron 表达式解析
  const parts = cronExpression.split(' ')
  if (parts.length >= 5) {
    return {
      minute: parts[0],
      hour: parts[1],
      day: parts[2],
      month: parts[3],
      day_of_week: parts[4]
    }
  }
  return {}
}

// 设置触发器参数
const setTriggerArgs = (args) => {
  if (!args) return
  
  if (jobForm.trigger === 'cron') {
    // 简化处理，实际项目中应该有更完善的 Cron 表达式生成
    const minute = args.minute || '*'
    const hour = args.hour || '*'
    const day = args.day || '*'
    const month = args.month || '*'
    const day_of_week = args.day_of_week || '*'
    triggerArgs.cronExpression = `${minute} ${hour} ${day} ${month} ${day_of_week}`
    triggerArgs.timezone = args.timezone || 'Asia/Shanghai'
  } else if (jobForm.trigger === 'interval') {
    triggerArgs.days = args.days || 0
    triggerArgs.hours = args.hours || 0
    triggerArgs.minutes = args.minutes || 0
    triggerArgs.seconds = args.seconds || 0
    triggerArgs.start_date = args.start_date ? dayjs(args.start_date) : null
  } else if (jobForm.trigger === 'date') {
    triggerArgs.run_date = args.run_date ? dayjs(args.run_date) : null
    triggerArgs.timezone = args.timezone || 'Asia/Shanghai'
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    loading.value = true
    
    // 解析参数和关键字参数
    let args = []
    let kwargs = {}
    
    try {
      args = JSON.parse(argsJson.value)
      kwargs = JSON.parse(kwargsJson.value)
    } catch (error) {
      message.error('参数或关键字参数格式错误，请检查 JSON 格式')
      loading.value = false
      return
    }
    
    // 构建提交数据
    const data = {
      name: jobForm.name,
      func: jobForm.func,
      args,
      kwargs,
      trigger: jobForm.trigger,
      trigger_args: getTriggerArgs(),
      max_instances: jobForm.max_instances,
      misfire_grace_time: jobForm.misfire_grace_time,
      coalesce: jobForm.coalesce,
      description: jobForm.description
    }
    
    // 提交数据
    if (isEdit.value) {
      await updateJob(route.params.id, data)
      message.success('任务更新成功')
    } else {
      await createJob(data)
      message.success('任务创建成功')
    }
    
    // 返回列表页
    router.push('/jobs')
  } catch (error) {
    console.error('提交任务失败:', error)
    message.error('提交任务失败: ' + (error.response?.data?.detail || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 获取任务详情
const fetchJobDetail = async (id) => {
  try {
    loading.value = true
    
    const data = await getJob(id)
    
    // 设置表单数据
    jobForm.name = data.name
    jobForm.func = data.func
    jobForm.description = data.description || ''
    jobForm.trigger = data.trigger
    jobForm.max_instances = data.max_instances
    jobForm.misfire_grace_time = data.misfire_grace_time
    jobForm.coalesce = data.coalesce
    
    // 设置触发器参数
    setTriggerArgs(data.trigger_args)
    
    // 设置参数和关键字参数
    argsJson.value = JSON.stringify(data.args || [], null, 2)
    kwargsJson.value = JSON.stringify(data.kwargs || {}, null, 2)
  } catch (error) {
    console.error('获取任务详情失败:', error)
    message.error('获取任务详情失败')
    router.push('/jobs')
  } finally {
    loading.value = false
  }
}

// 组件挂载时获取任务详情
onMounted(() => {
  if (isEdit.value) {
    fetchJobDetail(route.params.id)
  }
})
</script>

<style scoped>
.job-form-container {
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
