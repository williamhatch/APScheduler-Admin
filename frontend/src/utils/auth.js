// 令牌存储键名
const TOKEN_KEY = 'apscheduler_admin_token'

/**
 * 获取令牌
 * @returns {string} 令牌
 */
export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * 设置令牌
 * @param {string} token - 令牌
 */
export function setToken(token) {
  return localStorage.setItem(TOKEN_KEY, token)
}

/**
 * 移除令牌
 */
export function removeToken() {
  return localStorage.removeItem(TOKEN_KEY)
}
