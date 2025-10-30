// src/utils/opencc.ts
/**
 * 使用 OpenCC 进行简繁体转换
 * OpenCC 是业界标准的简繁转换库，支持多种转换模式
 */

// 说明：原实现依赖 'opencc' 包进行动态导入，构建时在某些环境无法解析。
// 为保证可构建性与功能可用性，这里改为使用本地的文本转换工具作为后备实现，
// 保持相同的 API（异步 Promise 接口），便于后续无缝切换到真正的 OpenCC。

import { convertTextByLanguage } from '@/utils/textConverter'

// 转换模式枚举
export enum ConversionMode {
  S2T = 's2t', // 简体到繁体
  T2S = 't2s', // 繁体到简体
  S2TW = 's2tw', // 简体到台湾繁体
  TW2S = 'tw2s', // 台湾繁体到简体
  S2HK = 's2hk', // 简体到香港繁体
  HK2S = 'hk2s', // 香港繁体到简体
  S2TWP = 's2twp', // 简体到台湾繁体（短语）
  TW2SP = 'tw2sp', // 台湾繁体到简体（短语）
  T2TW = 't2tw', // 繁体到台湾繁体
  TW2T = 'tw2t', // 台湾繁体到繁体
  T2HK = 't2hk', // 繁体到香港繁体
  HK2T = 'hk2t', // 香港繁体到繁体
  T2JP = 't2jp', // 繁体到日文汉字
  JP2T = 'jp2t', // 日文汉字到繁体
}

class OpenCCManager {
  private isLoaded = false

  /**
   * 初始化 OpenCC
   */
  init(): any {
    if (this.isLoaded) return
    this.isLoaded = true
  }

  /**
   * 获取转换器
   */
  private ensureReady(): any {
    if (!this.isLoaded) this.init()
  }

  /**
   * 简体转繁体
   */
  simplifiedToTraditional(text: string): any {
    this.ensureReady()
    if (!text) return text
    return convertTextByLanguage(text, 'zh-TW')
  }

  /**
   * 繁体转简体
   */
  traditionalToSimplified(text: string): any {
    this.ensureReady()
    if (!text) return text
    return convertTextByLanguage(text, 'zh-CN')
  }

  /**
   * 简体转台湾繁体
   */
  simplifiedToTaiwanTraditional(text: string): any {
    this.ensureReady()
    if (!text) return text
    return convertTextByLanguage(text, 'zh-TW')
  }

  /**
   * 台湾繁体转简体
   */
  taiwanTraditionalToSimplified(text: string): any {
    this.ensureReady()
    if (!text) return text
    return convertTextByLanguage(text, 'zh-CN')
  }

  /**
   * 简体转香港繁体
   */
  simplifiedToHongKongTraditional(text: string): any {
    this.ensureReady()
    if (!text) return text
    return convertTextByLanguage(text, 'zh-TW')
  }

  /**
   * 香港繁体转简体
   */
  hongKongTraditionalToSimplified(text: string): any {
    this.ensureReady()
    if (!text) return text
    return convertTextByLanguage(text, 'zh-CN')
  }

  /**
   * 通用转换方法
   */
  convert(text: string, from: 'zh-CN' | 'zh-TW' | 'zh-HK', to: 'zh-CN' | 'zh-TW' | 'zh-HK'): any {
    this.ensureReady()
    if (!text || from === to) return text
    const target = to === 'zh-CN' ? 'zh-CN' : 'zh-TW'
    return convertTextByLanguage(text, target)
  }

  /**
   * 检测文本语言
   */
  detectLanguage(text: string): any {
    if (!text) return 'unknown'

    // 简单的语言检测逻辑
    const traditionalChars = /[\u4e00-\u9fff]/
    const simplifiedChars = /[\u4e00-\u9fff]/

    // 这里可以实现更复杂的检测逻辑
    // 比如统计简繁体字符的比例
    const hasTraditional = /[繁體簡體學學校聯繫]/g.test(text)
    const hasSimplified = /[简体繁体学学校联系]/g.test(text)

    if (hasTraditional && !hasSimplified) {
      return 'zh-TW'
    } else if (hasSimplified && !hasTraditional) {
      return 'zh-CN'
    }

    return 'unknown'
  }
}

// 创建单例实例
export const openccManager = new OpenCCManager()

// 便捷方法
export const convertText = openccManager.convert.bind(openccManager)
export const detectLanguage = openccManager.detectLanguage.bind(openccManager)
export const simplifiedToTraditional = openccManager.simplifiedToTraditional.bind(openccManager)
export const traditionalToSimplified = openccManager.traditionalToSimplified.bind(openccManager)
