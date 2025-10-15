import { API_CONFIG } from './config'
import type { ApiResponse } from './types'
import { generateSignature, getDeviceFingerprint } from '../utils/crypto'

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
  skipSignature?: boolean  // 是否跳过签名（用于某些不需要签名的请求）
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
  
  // 生成请求签名（用于防爬取）
  const requestHeaders: Record<string, string> = {
    ...API_CONFIG.HEADERS,
    ...headers
  }
  
  if (!skipSignature) {
    try {
      const signatureData = await generateSignature(
        method === 'GET' ? params : {},
        method !== 'GET' ? body : undefined,
        method  // 传递HTTP方法
      )
      
      // 添加签名相关的请求头
      requestHeaders['X-Api-Key'] = signatureData.apiKey
      requestHeaders['X-Timestamp'] = String(signatureData.timestamp)
      requestHeaders['X-Nonce'] = signatureData.nonce
      requestHeaders['X-Signature'] = signatureData.signature
      requestHeaders['X-Device-Id'] = getDeviceFingerprint()
    } catch (err) {
      console.error('生成签名失败:', err)
      // 签名失败时抛出错误，不继续请求
      throw new HttpError(0, '无法生成请求签名，请检查网络连接')
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
      throw new HttpError(
        response.status,
        errorData.message || `HTTP Error: ${response.status}`,
        errorData
      )
    }
    
    const data = await response.json()
    return data
    
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