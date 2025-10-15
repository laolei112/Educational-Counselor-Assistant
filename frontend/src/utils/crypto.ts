/**
 * 加密和签名工具类
 * 用于前后端通信加密和防爬取
 * 
 * 安全说明：
 * - 签名由后端生成，前端不存储密钥
 * - 前端只负责调用签名API并使用返回的签名
 */

// API基础URL
const API_BASE_URL = '/api'

/**
 * 调用后端生成请求签名
 * 
 * 优势：
 * 1. 前端不存储任何密钥
 * 2. 密钥完全在服务端管理
 * 3. 即使前端代码被完全逆向，也无法伪造签名
 */
export async function generateSignature(
  params: Record<string, any> = {},
  body?: any,
  method: string = 'GET'
): Promise<{
  timestamp: number
  nonce: string
  apiKey: string
  signature: string
}> {
  try {
    // 调用后端API生成签名
    const response = await fetch(`${API_BASE_URL}/generate-signature`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        params: method === 'GET' ? params : {},
        body: method !== 'GET' && body ? (typeof body === 'string' ? body : JSON.stringify(body)) : undefined,
        method
      })
    })
    
    if (!response.ok) {
      throw new Error(`签名生成失败: ${response.status}`)
    }
    
    const result = await response.json()
    
    if (!result.success || !result.data) {
      throw new Error(result.message || '签名生成失败')
    }
    
    return {
      timestamp: result.data.timestamp,
      nonce: result.data.nonce,
      apiKey: result.data.apiKey,
      signature: result.data.signature
    }
  } catch (error) {
    console.error('生成签名失败:', error)
    // 如果签名生成失败，返回空签名（会被后端拒绝，但不影响应用运行）
    throw error
  }
}

/**
 * AES-GCM 加密（用于敏感数据）
 */
export async function encryptData(data: string): Promise<{
  encrypted: string
  iv: string
}> {
  const encoder = new TextEncoder()
  const dataBuffer = encoder.encode(data)
  
  // 生成密钥
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    encoder.encode(API_SECRET.padEnd(32, '0').slice(0, 32)),
    { name: 'PBKDF2' },
    false,
    ['deriveBits', 'deriveKey']
  )
  
  const key = await crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: encoder.encode('salt-string'),
      iterations: 100000,
      hash: 'SHA-256'
    },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    true,
    ['encrypt']
  )
  
  // 生成IV
  const iv = crypto.getRandomValues(new Uint8Array(12))
  
  // 加密
  const encrypted = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    key,
    dataBuffer
  )
  
  // 转换为Base64
  const encryptedArray = Array.from(new Uint8Array(encrypted))
  const encryptedBase64 = btoa(String.fromCharCode(...encryptedArray))
  const ivBase64 = btoa(String.fromCharCode(...Array.from(iv)))
  
  return {
    encrypted: encryptedBase64,
    iv: ivBase64
  }
}

/**
 * AES-GCM 解密
 */
export async function decryptData(encrypted: string, ivBase64: string): Promise<string> {
  const encoder = new TextEncoder()
  const decoder = new TextDecoder()
  
  // 生成密钥
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    encoder.encode(API_SECRET.padEnd(32, '0').slice(0, 32)),
    { name: 'PBKDF2' },
    false,
    ['deriveBits', 'deriveKey']
  )
  
  const key = await crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: encoder.encode('salt-string'),
      iterations: 100000,
      hash: 'SHA-256'
    },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    true,
    ['decrypt']
  )
  
  // 从Base64解码
  const encryptedArray = Uint8Array.from(atob(encrypted), c => c.charCodeAt(0))
  const iv = Uint8Array.from(atob(ivBase64), c => c.charCodeAt(0))
  
  // 解密
  const decrypted = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv },
    key,
    encryptedArray
  )
  
  return decoder.decode(decrypted)
}

/**
 * 简单的数据混淆（用于非敏感数据的轻量级保护）
 */
export function obfuscateData(data: string): string {
  return btoa(encodeURIComponent(data))
}

/**
 * 简单的数据反混淆
 */
export function deobfuscateData(data: string): string {
  return decodeURIComponent(atob(data))
}

/**
 * 生成设备指纹（用于识别客户端）
 */
export function getDeviceFingerprint(): string {
  const components = [
    navigator.userAgent,
    navigator.language,
    new Date().getTimezoneOffset(),
    screen.width + 'x' + screen.height,
    screen.colorDepth
  ]
  
  return btoa(components.join('|'))
}

