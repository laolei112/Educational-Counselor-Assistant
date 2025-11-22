import type { Plugin } from 'vite'
import { readFileSync, writeFileSync, existsSync } from 'fs'
import { join } from 'path'

/**
 * Vite插件：添加资源提示（preload/prefetch）优化关键资源加载
 */
export function resourceHints(): Plugin {
  return {
    name: 'resource-hints',
    apply: 'build',
    enforce: 'post',
    writeBundle(options, bundle) {
      if (!options.dir) return

      const htmlPath = join(options.dir, 'index.html')
      if (!existsSync(htmlPath)) return

      try {
        let html = readFileSync(htmlPath, 'utf-8')

        // 查找关键JS文件（入口文件）
        const jsRegex = /<script\s+type="module"\s+crossorigin\s+src="([^"]+\.js)"><\/script>/g
        const jsMatches = Array.from(html.matchAll(jsRegex))

        if (jsMatches.length > 0) {
          // 为入口JS文件添加preload
          const entryJs = jsMatches[0][1]
          const preloadLink = `<link rel="modulepreload" href="${entryJs}" crossorigin>`
          
          // 在head中添加preload
          html = html.replace('</head>', `${preloadLink}\n</head>`)
        }

        // 查找vendor chunks（vue-core, vue-router, pinia等）
        const vendorChunks = ['vue-core', 'vue-router', 'pinia']
        vendorChunks.forEach(chunkName => {
          // 在bundle中查找对应的chunk文件
          for (const fileName in bundle) {
            if (fileName.includes(chunkName) && fileName.endsWith('.js')) {
              const chunkPath = `/${fileName}`
              const prefetchLink = `<link rel="prefetch" href="${chunkPath}" as="script">`
              // 在head末尾添加prefetch（非关键资源）
              html = html.replace('</head>', `${prefetchLink}\n</head>`)
              break
            }
          }
        })

        // 写入修改后的HTML
        writeFileSync(htmlPath, html, 'utf-8')
        console.log('✓ 资源提示优化完成')
      } catch (error) {
        console.warn('资源提示插件警告:', error)
      }
    }
  }
}

