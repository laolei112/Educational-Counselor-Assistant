// src/utils/opencc.ts
/**
 * 使用 OpenCC 进行简繁体转换
 * OpenCC 是业界标准的简繁转换库，支持多种转换模式
 */

// 注意：这里使用 CDN 方式引入，实际项目中建议使用 npm 安装
// npm install opencc

interface OpenCCConverter {
  convertPromise(text: string): Promise<string>
}

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
  private converters: Map<string, OpenCCConverter> = new Map()
  private isLoaded = false

  /**
   * 初始化 OpenCC
   */
  async init(): Promise<void> {
    if (this.isLoaded) return

    try {
      // 动态加载 OpenCC
      const OpenCC = await import('opencc')
      
      // 预加载常用转换器
      const commonModes = [
        ConversionMode.S2T,
        ConversionMode.T2S,
        ConversionMode.S2TW,
        ConversionMode.TW2S
      ]

      for (const mode of commonModes) {
        try {
          const converter = new OpenCC.default(`${mode}.json`)
          this.converters.set(mode, converter)
        } catch (error) {
          console.warn(`Failed to load OpenCC converter for ${mode}:`, error)
        }
      }

      this.isLoaded = true
    } catch (error) {
      console.error('Failed to load OpenCC:', error)
      throw new Error('OpenCC 加载失败')
    }
  }

  /**
   * 获取转换器
   */
  private async getConverter(mode: ConversionMode): Promise<OpenCCConverter> {
    if (!this.isLoaded) {
      await this.init()
    }

    let converter = this.converters.get(mode)
    if (!converter) {
      try {
        const OpenCC = await import('opencc')
        converter = new OpenCC.default(`${mode}.json`)
        this.converters.set(mode, converter)
      } catch (error) {
        console.error(`Failed to create converter for ${mode}:`, error)
        throw new Error(`转换器 ${mode} 创建失败`)
      }
    }

    return converter
  }

  /**
   * 简体转繁体
   */
  async simplifiedToTraditional(text: string): Promise<string> {
    if (!text) return text
    const converter = await this.getConverter(ConversionMode.S2T)
    return await converter.convertPromise(text)
  }

  /**
   * 繁体转简体
   */
  async traditionalToSimplified(text: string): Promise<string> {
    if (!text) return text
    const converter = await this.getConverter(ConversionMode.T2S)
    return await converter.convertPromise(text)
  }

  /**
   * 简体转台湾繁体
   */
  async simplifiedToTaiwanTraditional(text: string): Promise<string> {
    if (!text) return text
    const converter = await this.getConverter(ConversionMode.S2TW)
    return await converter.convertPromise(text)
  }

  /**
   * 台湾繁体转简体
   */
  async taiwanTraditionalToSimplified(text: string): Promise<string> {
    if (!text) return text
    const converter = await this.getConverter(ConversionMode.TW2S)
    return await converter.convertPromise(text)
  }

  /**
   * 简体转香港繁体
   */
  async simplifiedToHongKongTraditional(text: string): Promise<string> {
    if (!text) return text
    const converter = await this.getConverter(ConversionMode.S2HK)
    return await converter.convertPromise(text)
  }

  /**
   * 香港繁体转简体
   */
  async hongKongTraditionalToSimplified(text: string): Promise<string> {
    if (!text) return text
    const converter = await this.getConverter(ConversionMode.HK2S)
    return await converter.convertPromise(text)
  }

  /**
   * 通用转换方法
   */
  async convert(text: string, from: 'zh-CN' | 'zh-TW' | 'zh-HK', to: 'zh-CN' | 'zh-TW' | 'zh-HK'): Promise<string> {
    if (!text || from === to) return text

    const conversionMap: Record<string, ConversionMode> = {
      'zh-CN-zh-TW': ConversionMode.S2TW,
      'zh-TW-zh-CN': ConversionMode.TW2S,
      'zh-CN-zh-HK': ConversionMode.S2HK,
      'zh-HK-zh-CN': ConversionMode.HK2S
      // 注：zh-TW <-> zh-HK 直连模式不在 opencc 标准配置中，若需精细转换可分两步：TW→T→HK 或 HK→T→TW
    }

    const key = `${from}-${to}`
    const mode = conversionMap[key]
    
    if (!mode) {
      console.warn(`Unsupported conversion from ${from} to ${to}`)
      return text
    }

    const converter = await this.getConverter(mode)
    return await converter.convertPromise(text)
  }

  /**
   * 检测文本语言
   */
  async detectLanguage(text: string): Promise<'zh-CN' | 'zh-TW' | 'zh-HK' | 'unknown'> {
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
