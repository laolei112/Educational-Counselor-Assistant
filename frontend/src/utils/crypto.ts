/**
 * 加密和签名工具类
 * 用于前后端通信加密和防爬取
 */

// API密钥（实际使用时应该从环境变量读取）
const API_SECRET = import.meta.env.VITE_API_SECRET || 'your-secret-key-change-in-production'
const API_KEY = import.meta.env.VITE_API_KEY || 'web-client-v1'

/**
 * SHA256 哈希函数
 */
async function sha256(message: string): Promise<string> {
  const msgBuffer = new TextEncoder().encode(message)
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
  return hashHex
}

/**
 * 生成随机字符串
 */
function generateNonce(length: number = 16): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  const randomValues = new Uint8Array(length)
  crypto.getRandomValues(randomValues)
  
  for (let i = 0; i < length; i++) {
    result += chars[randomValues[i] % chars.length]
  }
  
  return result
}

/**
 * 生成时间戳（秒级）
 */
function getTimestamp(): number {
  return Math.floor(Date.now() / 1000)
}

/**
 * 对对象的键进行排序并序列化
 */
function sortAndStringify(obj: Record<string, any>): string {
  const sortedKeys = Object.keys(obj).sort()
  const pairs: string[] = []
  
  for (const key of sortedKeys) {
    const value = obj[key]
    if (value !== undefined && value !== null) {
      pairs.push(`${key}=${String(value)}`)
    }
  }
  
  return pairs.join('&')
}

/**
 * 生成请求签名
 * 签名算法：SHA256(timestamp + nonce + apiKey + sortedParams + apiSecret)
 */
export async function generateSignature(
  params: Record<string, any> = {},
  body?: any
): Promise<{
  timestamp: number
  nonce: string
  apiKey: string
  signature: string
}> {
  const timestamp = getTimestamp()
  const nonce = generateNonce()
  
  // 构建签名字符串
  let signString = `${timestamp}${nonce}${API_KEY}`
  
  // 添加查询参数
  if (params && Object.keys(params).length > 0) {
    signString += sortAndStringify(params)
  }
  
  // 添加请求体
  if (body) {
    const bodyStr = typeof body === 'string' ? body : JSON.stringify(body)
    signString += bodyStr
  }
  
  // 添加密钥
  signString += API_SECRET
  
  // 生成签名
  const signature = await sha256(signString)
  
  return {
    timestamp,
    nonce,
    apiKey: API_KEY,
    signature
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

