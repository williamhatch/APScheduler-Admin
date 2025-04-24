import request from '@/utils/request'

/**
 * 获取用户列表
 * @param {Object} params - 查询参数
 * @returns {Promise} - 返回用户列表
 */
export function getUsers(params) {
  return request({
    url: '/api/v1/users',
    method: 'get',
    params
  })
}

/**
 * 获取用户详情
 * @param {number} id - 用户ID
 * @returns {Promise} - 返回用户详情
 */
export function getUser(id) {
  return request({
    url: `/api/v1/users/${id}`,
    method: 'get'
  })
}

/**
 * 创建用户
 * @param {Object} data - 用户数据
 * @returns {Promise} - 返回创建结果
 */
export function createUser(data) {
  return request({
    url: '/api/v1/users',
    method: 'post',
    data
  })
}

/**
 * 更新用户
 * @param {number} id - 用户ID
 * @param {Object} data - 用户数据
 * @returns {Promise} - 返回更新结果
 */
export function updateUser(id, data) {
  return request({
    url: `/api/v1/users/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除用户
 * @param {number} id - 用户ID
 * @returns {Promise} - 返回删除结果
 */
export function deleteUser(id) {
  return request({
    url: `/api/v1/users/${id}`,
    method: 'delete'
  })
}

/**
 * 更新当前用户信息
 * @param {Object} data - 用户数据
 * @returns {Promise} - 返回更新结果
 */
export function updateUserInfo(data) {
  return request({
    url: '/api/v1/users/me',
    method: 'put',
    data
  })
}
