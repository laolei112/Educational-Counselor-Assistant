/**
 * Token管理器
 * 负责Token的获取、存储、刷新等操作
 */

const TOKEN_STORAGE_KEY = 'api_access_token'
const TOKEN_EXPIRY_KEY = 'api_token_expiry'
const API_BASE_URL = '/api'

interface TokenData {
  token: string
  expires_in: number
  token_type: string
}

interface TokenResponse {
  code: number
  success: boolean
  message?: string
  data?: TokenData
}

export class TokenManager {
  private static instance: TokenManager
  private token: string | null = null
  private tokenExpiry: number = 0
  private refreshPromise: Promise<string> | null = null
  
  private constructor() {
    this.loadToken()
  }
  
  /**
   * 获取TokenManager单例
   */
  static getInstance(): TokenManager {
    if (!TokenManager.instance) {
      TokenManager.instance = new TokenManager()
    }
    return TokenManager.instance
  }
  
  /**
   * 从本地存储加载Token
   */
  private loadToken() {
    try {
      this.token = localStorage.getItem(TOKEN_STORAGE_KEY)
      const expiry = localStorage.getItem(TOKEN_EXPIRY_KEY)
      this.tokenExpiry = expiry ? parseInt(expiry) : 0
    } catch (err) {
      console.error('加载Token失败:', err)
    }
  }
  
  /**
   * 保存Token到本地存储
   */
  private saveToken(token: string, expiresIn: number) {
    try {
      this.token = token
      // 计算过期时间戳
      this.tokenExpiry = Date.now() + (expiresIn * 1000)
      
      localStorage.setItem(TOKEN_STORAGE_KEY, token)
      localStorage.setItem(TOKEN_EXPIRY_KEY, String(this.tokenExpiry))
      
      console.log('Token已保存，有效期:', expiresIn, '秒')
    } catch (err) {
      console.error('保存Token失败:', err)
    }
  }
  
  /**
   * 检查Token是否有效
   * 提前5分钟判定为即将过期
   */
  isTokenValid(): boolean {
    if (!this.token) {
      return false
    }
    
    // 提前5分钟刷新Token
    const bufferTime = 5 * 60 * 1000  // 5分钟
    return Date.now() < (this.tokenExpiry - bufferTime)
  }
  
  /**
   * 获取Token（自动处理刷新）
   * 这是主要的公开方法
   */
  async getToken(): Promise<string> {
    // 如果Token有效，直接返回
    if (this.isTokenValid() && this.token) {
      return this.token
    }
    
    // 如果正在刷新，等待刷新完成
    if (this.refreshPromise) {
      return this.refreshPromise
    }
    
    // 否则获取新Token
    this.refreshPromise = this.fetchNewToken()
    
    try {
      const token = await this.refreshPromise
      return token
    } finally {
      this.refreshPromise = null
    }
  }
  
  /**
   * 从服务器获取新Token
   */
  private async fetchNewToken(): Promise<string> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          platform: 'web',
          version: '1.0.0'
        })
      })
      
      if (!response.ok) {
        throw new Error(`获取Token失败: HTTP ${response.status}`)
      }
      
      const result: TokenResponse = await response.json()
      
      if (!result.success || !result.data) {
        throw new Error(result.message || '获取Token失败')
      }
      
      // 保存Token
      this.saveToken(result.data.token, result.data.expires_in)
      
      return result.data.token
    } catch (error) {
      console.error('获取Token失败:', error)
      // 清除无效Token
      this.clearToken()
      throw error
    }
  }
  
  /**
   * 刷新Token
   */
  async refreshToken(): Promise<string> {
    if (!this.token) {
      return this.fetchNewToken()
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`
        }
      })
      
      if (!response.ok) {
        // 如果刷新失败，获取新Token
        return this.fetchNewToken()
      }
      
      const result: TokenResponse = await response.json()
      
      if (!result.success || !result.data) {
        return this.fetchNewToken()
      }
      
      // 保存新Token
      this.saveToken(result.data.token, result.data.expires_in)
      
      return result.data.token
    } catch (error) {
      console.error('刷新Token失败:', error)
      // 刷新失败时获取新Token
      return this.fetchNewToken()
    }
  }
  
  /**
   * 清除Token
   */
  clearToken() {
    this.token = null
    this.tokenExpiry = 0
    
    try {
      localStorage.removeItem(TOKEN_STORAGE_KEY)
      localStorage.removeItem(TOKEN_EXPIRY_KEY)
      console.log('Token已清除')
    } catch (err) {
      console.error('清除Token失败:', err)
    }
  }
  
  /**
   * 撤销Token（注销）
   */
  async revokeToken(): Promise<void> {
    if (!this.token) {
      return
    }
    
    try {
      await fetch(`${API_BASE_URL}/auth/revoke`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      })
    } catch (error) {
      console.error('撤销Token失败:', error)
    } finally {
      this.clearToken()
    }
  }
  
  /**
   * 获取Token信息
   */
  async getTokenInfo() {
    if (!this.token) {
      return null
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/auth/token-info`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      })
      
      if (!response.ok) {
        return null
      }
      
      const result = await response.json()
      return result.success ? result.data : null
    } catch (error) {
      console.error('获取Token信息失败:', error)
      return null
    }
  }
  
  /**
   * 检查Token是否即将过期（用于UI提示）
   */
  isTokenExpiringSoon(): boolean {
    if (!this.token) {
      return false
    }
    
    const bufferTime = 10 * 60 * 1000  // 10分钟
    const now = Date.now()
    
    return now > (this.tokenExpiry - bufferTime) && now < this.tokenExpiry
  }
  
  /**
   * 获取Token剩余时间（秒）
   */
  getTokenRemainingTime(): number {
    if (!this.token) {
      return 0
    }
    
    const remaining = Math.floor((this.tokenExpiry - Date.now()) / 1000)
    return Math.max(0, remaining)
  }
}

// 导出单例实例
export const tokenManager = TokenManager.getInstance()

// 自动刷新Token（可选）
// 每5分钟检查一次Token状态
setInterval(() => {
  if (tokenManager.isTokenExpiringSoon()) {
    console.log('Token即将过期，自动刷新...')
    tokenManager.getToken().catch(err => {
      console.error('自动刷新Token失败:', err)
    })
  }
}, 5 * 60 * 1000)

