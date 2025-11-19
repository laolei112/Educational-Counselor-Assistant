/**
 * 前端安全工具类
 * 负责：
 * 1. 动态Token管理
 * 2. 响应数据解密
 */

import CryptoJS from 'crypto-js';

// 密钥（必须与后端一致）
// 注意：虽然这在前端是可见的，但它增加了通过F12直接查看API响应的难度
// 爬虫必须执行JS逻辑才能拿到数据
const DECRYPTION_KEY = CryptoJS.enc.Utf8.parse('Educational_Counselor_Secret_K'.padEnd(32, '\0').slice(0, 32));

export interface TokenData {
  token: string;
  expires_in: number;
}

class SecurityManager {
  private token: string | null = null;
  private tokenExpiry: number = 0;
  private refreshPromise: Promise<string> | null = null;

  /**
   * 获取有效Token
   */
  async getToken(): Promise<string> {
    if (this.token && Date.now() < this.tokenExpiry) {
      return this.token;
    }

    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = this.requestNewToken();
    try {
      const token = await this.refreshPromise;
      return token;
    } finally {
      this.refreshPromise = null;
    }
  }

  private async requestNewToken(): Promise<string> {
    try {
      // 注意：Token获取接口不需要Token
      const response = await fetch('/api/auth/request-token', {
        method: 'GET',
        headers: {
           // 标记这是一个普通浏览器请求
          'X-Device-Type': 'Browser'
        }
      });
      
      const result = await response.json();
      if (result.success && result.data) {
        this.token = result.data.token;
        // 提前5秒过期
        this.tokenExpiry = Date.now() + (result.data.expires_in - 5) * 1000;
        return this.token;
      }
      throw new Error('Token获取失败');
    } catch (e) {
      console.error('Security Token Error:', e);
      throw e;
    }
  }

  /**
   * 解密API响应数据
   * @param encryptedData 后端返回的加密结构 { iv: string, payload: string }
   */
  decryptData(encryptedData: any): any {
    try {
      if (!encryptedData || !encryptedData.iv || !encryptedData.payload) {
        return encryptedData;
      }

      const iv = CryptoJS.enc.Base64.parse(encryptedData.iv);
      const payload = encryptedData.payload;

      const decrypted = CryptoJS.AES.decrypt(payload, DECRYPTION_KEY, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
      });

      const jsonStr = decrypted.toString(CryptoJS.enc.Utf8);
      return JSON.parse(jsonStr);
    } catch (e) {
      console.error('Decryption Failed:', e);
      // 解密失败可能是因为数据本身没有加密（比如是SEO模式）
      return encryptedData;
    }
  }
  
  clearToken() {
    this.token = null;
    this.tokenExpiry = 0;
  }
}

export const securityManager = new SecurityManager();

