import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: 3000
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
    // 分块策略 - 将关键代码分离
    rollupOptions: {
      output: {
        // 手动分块，将加密相关代码单独打包
        manualChunks: {
          'crypto-utils': ['./src/utils/crypto.ts'],
          'vue-vendor': ['vue', 'vue-router', 'pinia']
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