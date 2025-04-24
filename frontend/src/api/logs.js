import request from '@/utils/request'

/**
 * 获取日志列表
 * @param {Object} params - 查询参数
 * @returns {Promise} - 返回日志列表
 */
export function getLogs(params) {
  return request({
    url: '/api/v1/logs',
    method: 'get',
    params
  })
}

/**
 * 获取日志详情
 * @param {number} id - 日志ID
 * @returns {Promise} - 返回日志详情
 */
export function getLog(id) {
  return request({
    url: `/api/v1/logs/${id}`,
    method: 'get'
  })
}

/**
 * 删除日志
 * @param {number} id - 日志ID
 * @returns {Promise} - 返回删除结果
 */
export function deleteLog(id) {
  return request({
    url: `/api/v1/logs/${id}`,
    method: 'delete'
  })
}

/**
 * 删除任务的所有日志
 * @param {number} jobId - 任务ID
 * @returns {Promise} - 返回删除结果
 */
export function deleteJobLogs(jobId) {
  return request({
    url: `/api/v1/logs/job/${jobId}`,
    method: 'delete'
  })
}
