import { API_CONFIG } from './config'
import type { ApiResponse } from './types'
// import { tokenManager } from '../utils/token'  // 移除：不再需要 JWT
import { securityManager } from '../utils/security'
import { getDeviceFingerprint } from '../utils/crypto'

// HTTP请求错误类
export class HttpError extends Error {
  constructor(
    public status: number,
    message: string,
    public data?: any
  ) {
    super(message)
    this.name = 'HttpError'
  }
}

// 请求配置接口
interface RequestConfig {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  headers?: Record<string, string>
  body?: any
  timeout?: number
  skipSignature?: boolean  // 是否跳过Token
}

// 构建完整URL
function buildUrl(path: string, params?: Record<string, any>): string {
  let url = `${API_CONFIG.BASE_URL}${path}`
  
  if (params) {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value))
      }
    })
    const queryString = searchParams.toString()
    if (queryString) {
      url += `?${queryString}`
    }
  }
  
  return url
}

// 通用请求函数
async function request<T = any>(
  path: string,
  config: RequestConfig = {},
  params?: Record<string, any>
): Promise<ApiResponse<T>> {
  const {
    method = 'GET',
    headers = {},
    body,
    timeout = API_CONFIG.TIMEOUT,
    skipSignature = false
  } = config

  const url = buildUrl(path, method === 'GET' ? params : undefined)
  
  const requestHeaders: Record<string, string> = {
    ...API_CONFIG.HEADERS,
    ...headers
  }
  
  if (!skipSignature) {
    try {
      // 1. JWT 认证 (已移除：无登录功能)
      // const token = await tokenManager.getToken()
      // requestHeaders['Authorization'] = `Bearer ${token}`
      
      // 2. 设备指纹
      requestHeaders['X-Device-Id'] = getDeviceFingerprint()

      // 3. 动态反爬 Token
      // 仅对数据接口添加
      if (path.includes('/schools/') || path.includes('/primary/') || path.includes('/secondary/')) {
         const dynamicToken = await securityManager.getToken()
         requestHeaders['X-Request-Token'] = dynamicToken
      }

    } catch (err) {
      console.error('获取凭证失败:', err)
      // 即使失败也尝试请求，可能是未登录访问公开接口
    }
  }
  
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)
  
  try {
    const response = await fetch(url, {
      method,
      headers: requestHeaders,
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal
    })
    
    clearTimeout(timeoutId)
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      
      // 处理 401 JWT 过期 (已移除)
      // if (response.status === 401 && !skipSignature) { ... }

      // 处理 403 动态 Token 过期
      if (response.status === 403 && errorData.message?.includes('Token')) {
          console.log('动态Token失效，尝试刷新...')
          securityManager.clearToken()
          const newToken = await securityManager.getToken()
          requestHeaders['X-Request-Token'] = newToken
          
          // 重试
          const retryResponse = await fetch(url, {
              method,
              headers: requestHeaders,
              body: body ? JSON.stringify(body) : undefined,
              signal: controller.signal
          })
          
          if (retryResponse.ok) {
             const retryRawData = await retryResponse.json()
             // 解密重试后的数据
             if (retryRawData.data && retryRawData.data.encrypted) {
                 retryRawData.data = securityManager.decryptData(retryRawData.data)
             }
             return retryRawData
          }
      }
      
      throw new HttpError(
        response.status,
        errorData.message || `HTTP Error: ${response.status}`,
        errorData
      )
    }
    
    // 解析响应数据
    const rawData = await response.json()

    // 自动解密数据
    // 检查 data 字段是否为加密结构
    if (rawData.data && rawData.data.encrypted) {
        try {
            // 替换为解密后的数据
            rawData.data = securityManager.decryptData(rawData.data)
        } catch (e) {
            console.error('数据解密失败', e)
            // 如果解密失败，可能是数据已经被篡改或密钥不对，但不应阻塞流程
        }
    }
    
    return rawData
    
  } catch (error) {
    clearTimeout(timeoutId)
    
    if (error instanceof HttpError) {
      throw error
    }
    
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new HttpError(408, '请求超时')
      }
      throw new HttpError(0, error.message)
    }
    
    throw new HttpError(0, '未知错误')
  }
}

// 导出具体的HTTP方法
export const http = {
  get: <T = any>(path: string, params?: Record<string, any>) =>
    request<T>(path, { method: 'GET' }, params),
    
  post: <T = any>(path: string, data?: any, params?: Record<string, any>) =>
    request<T>(path, { method: 'POST', body: data }, params),
    
  put: <T = any>(path: string, data?: any, params?: Record<string, any>) =>
    request<T>(path, { method: 'PUT', body: data }, params),
    
  delete: <T = any>(path: string, params?: Record<string, any>) =>
    request<T>(path, { method: 'DELETE' }, params)
}
