import request from '@/utils/request'

/**
 * 用户登录
 * @param {string} username - 用户名
 * @param {string} password - 密码
 * @returns {Promise} - 返回登录结果
 */
export function login(username, password) {
  // 使用JSON格式发送登录请求
  return request({
    url: '/api/v1/auth/login',
    method: 'post',
    data: {
      username,
      password
    }
  })
}

/**
 * 获取当前用户信息
 * @returns {Promise} - 返回用户信息
 */
export function getUserInfo() {
  return request({
    url: '/api/v1/users/me',
    method: 'get'
  })
}

/**
 * 测试令牌是否有效
 * @returns {Promise} - 返回测试结果
 */
export function testToken() {
  return request({
    url: '/api/v1/auth/test-token',
    method: 'post'
  })
}
