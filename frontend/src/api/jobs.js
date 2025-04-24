import request from '@/utils/request'

/**
 * 获取任务列表
 * @param {Object} params - 查询参数
 * @returns {Promise} - 返回任务列表
 */
export function getJobs(params) {
  return request({
    url: '/api/v1/jobs',
    method: 'get',
    params
  })
}

/**
 * 获取任务详情
 * @param {number} id - 任务ID
 * @returns {Promise} - 返回任务详情
 */
export function getJob(id) {
  return request({
    url: `/api/v1/jobs/${id}`,
    method: 'get'
  })
}

/**
 * 创建任务
 * @param {Object} data - 任务数据
 * @returns {Promise} - 返回创建结果
 */
export function createJob(data) {
  return request({
    url: '/api/v1/jobs',
    method: 'post',
    data
  })
}

/**
 * 更新任务
 * @param {number} id - 任务ID
 * @param {Object} data - 任务数据
 * @returns {Promise} - 返回更新结果
 */
export function updateJob(id, data) {
  return request({
    url: `/api/v1/jobs/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除任务
 * @param {number} id - 任务ID
 * @returns {Promise} - 返回删除结果
 */
export function deleteJob(id) {
  return request({
    url: `/api/v1/jobs/${id}`,
    method: 'delete'
  })
}

/**
 * 更新任务状态
 * @param {number} id - 任务ID
 * @param {string} status - 任务状态
 * @returns {Promise} - 返回更新结果
 */
export function updateJobStatus(id, status) {
  return request({
    url: `/api/v1/jobs/${id}/status`,
    method: 'post',
    data: { status }
  })
}

/**
 * 立即执行任务
 * @param {number} id - 任务ID
 * @returns {Promise} - 返回执行结果
 */
export function executeJob(id) {
  return request({
    url: `/api/v1/jobs/${id}/execute`,
    method: 'post'
  })
}
