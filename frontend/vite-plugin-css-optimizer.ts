import type { Plugin } from 'vite'
import { readFileSync, writeFileSync, existsSync } from 'fs'
import { join } from 'path'

/**
 * Vite插件：优化CSS加载性能
 * 1. 内联关键CSS到HTML
 * 2. 异步加载非关键CSS
 */
export function cssOptimizer(): Plugin {
  return {
    name: 'css-optimizer',
    apply: 'build',
    enforce: 'post',
    writeBundle(options, bundle) {
      // 在写入文件后处理HTML
      if (!options.dir) return

      const htmlPath = join(options.dir, 'index.html')
      if (!existsSync(htmlPath)) return

      try {
        let html = readFileSync(htmlPath, 'utf-8')

        // 查找CSS文件链接
        const cssLinkRegex = /<link\s+rel="stylesheet"\s+href="([^"]+\.css)">/g
        const cssMatches = Array.from(html.matchAll(cssLinkRegex))

        if (cssMatches.length === 0) return

        // 读取第一个CSS文件内容（通常是主要的CSS文件）
        const cssHref = cssMatches[0][1].startsWith('/') 
          ? cssMatches[0][1].substring(1) 
          : cssMatches[0][1]
        const cssPath = join(options.dir, cssHref)

        if (!existsSync(cssPath)) {
          console.warn(`CSS文件不存在: ${cssPath}`)
          return
        }

        const cssContent = readFileSync(cssPath, 'utf-8')

        // 提取关键CSS（前2KB，包含基础样式）
        const criticalCSS = extractCriticalCSS(cssContent)

        // 内联关键CSS到HTML head
        const inlineStyle = `<style id="critical-css">${criticalCSS}</style>`
        html = html.replace('</head>', `${inlineStyle}\n</head>`)

        // 将CSS链接改为异步加载
        let loadCSSAdded = false
        html = html.replace(cssLinkRegex, (match, href) => {
          // 使用preload + 异步加载
          const preloadLink = `<link rel="preload" href="${href}" as="style" onload="this.onload=null;this.rel='stylesheet'">`
          const noscriptFallback = `<noscript><link rel="stylesheet" href="${href}"></noscript>`
          
          // 只添加一次loadCSS polyfill
          if (!loadCSSAdded) {
            loadCSSAdded = true
            const loadCSSScript = `<script>!function(e){"use strict";var t=function(t,n,r){var o,i=e.document,a=i.createElement("link");if(n)o=n;else{var l=(i.body||i.getElementsByTagName("head")[0]).childNodes;o=l[l.length-1]}var d=i.styleSheets;a.rel="stylesheet",a.href=t,a.media="only x",function e(t){if(i.body)return t();setTimeout(function(){e(t)})}(function(){o.parentNode.insertBefore(a,n?o:o.nextSibling)});var f=function(e){for(var t=a.href,n=d.length;n--;)if(d[n].href===t)return e();setTimeout(function(){f(e)})};return a.addEventListener&&a.addEventListener("load",function(){this.media=r||"all"}),a.onloadcssdefined=f,f(function(){a.media!==r&&(a.media=r||"all")}),a};"undefined"!=typeof exports?exports.loadCSS=t:e.loadCSS=t}("undefined"!=typeof global?global:this);</script>`
            return `${preloadLink}\n${noscriptFallback}\n${loadCSSScript}`
          }
          return `${preloadLink}\n${noscriptFallback}`
        })

        // 写入修改后的HTML
        writeFileSync(htmlPath, html, 'utf-8')
        console.log('✓ CSS优化完成: 关键CSS已内联，非关键CSS已异步加载')
      } catch (error) {
        console.warn('CSS优化插件警告:', error)
      }
    }
  }
}

/**
 * 提取关键CSS
 * 包含基础样式、布局样式等above-the-fold内容所需的CSS
 */
function extractCriticalCSS(css: string): string {
  // 关键选择器模式（above-the-fold内容所需）
  const criticalPatterns = [
    /\*\s*\{[^}]*\}/g,  // 通用选择器
    /body\s*\{[^}]*\}/g,  // body样式
    /html\s*\{[^}]*\}/g,  // html样式
    /#app\s*\{[^}]*\}/g,  // app容器
    /\.app-content\s*\{[^}]*\}/g,  // app内容
    /\.home\s*\{[^}]*\}/g,  // home页面
    /\.container\s*\{[^}]*\}/g,  // 容器
    /\.header-section\s*\{[^}]*\}/g,  // 头部区域
    /\.header-content\s*\{[^}]*\}/g,  // 头部内容
    /\.header-title\s*\{[^}]*\}/g,  // 标题
    /\.header-subtitle\s*\{[^}]*\}/g,  // 副标题
    /\.header-search[^{]*\{[^}]*\}/g,  // 搜索框
    /\.btn\s*\{[^}]*\}/g,  // 按钮基础样式
    /\.btn-primary\s*\{[^}]*\}/g,  // 主要按钮
  ]
  
  const extractedRules = new Set<string>()
  
  // 提取所有匹配的关键CSS规则
  criticalPatterns.forEach(pattern => {
    const matches = css.match(pattern)
    if (matches) {
      matches.forEach(match => extractedRules.add(match))
    }
  })
  
  // 如果提取的规则太少，则提取前2000字符作为后备
  let criticalCSS = Array.from(extractedRules).join('\n')
  
  if (criticalCSS.length < 500) {
    // 后备方案：提取前2000字符，确保包含完整的CSS规则
    const fallbackCSS = css.substring(0, 2000)
    const lastBraceIndex = fallbackCSS.lastIndexOf('}')
    if (lastBraceIndex > 0) {
      criticalCSS = fallbackCSS.substring(0, lastBraceIndex + 1)
    } else {
      criticalCSS = fallbackCSS
    }
  }
  
  // 限制关键CSS大小（约2KB），避免内联过多内容
  if (criticalCSS.length > 2000) {
    const truncated = criticalCSS.substring(0, 2000)
    const lastBraceIndex = truncated.lastIndexOf('}')
    if (lastBraceIndex > 0) {
      return truncated.substring(0, lastBraceIndex + 1)
    }
    return truncated
  }
  
  return criticalCSS
}

