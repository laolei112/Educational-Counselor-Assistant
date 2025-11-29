import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { cssOptimizer } from './vite-plugin-css-optimizer'
import { resourceHints } from './vite-plugin-resource-hints'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), cssOptimizer(), resourceHints()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: 'https://betterschool.hk',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    // 代码混淆和压缩配置
    minify: 'terser', // 使用 terser 进行代码压缩和混淆
    terserOptions: {
      compress: {
        // 生产环境移除 console
        drop_console: true,
        drop_debugger: true,
        // 移除未使用的代码
        pure_funcs: ['console.log', 'console.info', 'console.debug', 'console.warn']
      },
      mangle: {
        // 混淆变量名
        toplevel: true,
        // 混淆属性名（谨慎使用，可能影响某些库）
        // properties: {
        //   regex: /^_/
        // }
      },
      format: {
        // 移除注释
        comments: false
      }
    },
    // 分块策略 - 将关键代码分离，优化加载性能
    rollupOptions: {
      output: {
        // 手动分块，优化代码分割
        manualChunks: (id) => {
          // 将node_modules中的依赖分离
          if (id.includes('node_modules')) {
            // Vue核心库单独打包
            if (id.includes('vue') && !id.includes('vue-router') && !id.includes('pinia')) {
              return 'vue-core'
            }
            // Vue Router单独打包
            if (id.includes('vue-router')) {
              return 'vue-router'
            }
            // Pinia单独打包
            if (id.includes('pinia')) {
              return 'pinia'
            }
            // 加密相关库
            if (id.includes('crypto-js')) {
              return 'crypto-utils'
            }
            // 其他第三方库
            return 'vendor'
          }
          // 工具函数单独打包
          if (id.includes('/utils/')) {
            return 'utils'
          }
          // API相关代码单独打包
          if (id.includes('/api/')) {
            return 'api'
          }
        },
        // 混淆文件名
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    },
    // 启用源码映射（仅用于调试，生产环境建议关闭）
    sourcemap: false, // 生产环境关闭 source map
    // 代码分割阈值
    chunkSizeWarningLimit: 1000
  }
}) 