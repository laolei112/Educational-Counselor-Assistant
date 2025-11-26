<template>
  <div class="contact-button-wrapper">
    <!-- 联系我们按钮 -->
    <button 
      class="contact-button" 
      @click="showModal = true"
      :title="getText('contact.button.title')"
    >
      <img src="/images/services.png" alt="客服" class="contact-icon-image" />
      <span class="contact-text">{{ getText('contact.service.text') }}</span>
    </button>

    <!-- 联系模态框 -->
    <div v-if="showModal" class="contact-modal-overlay" @click="closeModal">
      <div class="contact-modal-container" @click.stop>
        <!-- 关闭按钮 -->
        <button class="contact-close-btn" @click="closeModal">
          <span>✕</span>
        </button>

        <!-- 模态框内容 -->
        <div class="contact-modal-content">
          <h2 class="contact-modal-title">{{ getText('contact.modal.title') }}</h2>
          <p class="contact-modal-subtitle">{{ getText('contact.modal.subtitle') }}</p>
          
          <div class="qr-codes-container">
            <!-- 微信二维码 -->
            <div class="qr-code-item">
              <div class="qr-code-label">
                <span class="qr-icon">💬</span>
                <span>{{ getText('contact.wechat.label') }}</span>
              </div>
              <div class="qr-code-wrapper">
                <img 
                  :src="wechatQRCode" 
                  :alt="getText('contact.wechat.label')"
                  class="qr-code-image"
                  @error="handleImageError"
                />
              </div>
              <p class="qr-code-hint">{{ getText('contact.wechat.hint') }}</p>
            </div>

            <!-- WhatsApp二维码 -->
            <div class="qr-code-item">
              <div class="qr-code-label">
                <span class="qr-icon">📱</span>
                <span>{{ getText('contact.whatsapp.label') }}</span>
              </div>
              <div class="qr-code-wrapper">
                <img 
                  :src="whatsappQRCode" 
                  :alt="getText('contact.whatsapp.label')"
                  class="qr-code-image"
                  @error="handleImageError"
                />
              </div>
              <p class="qr-code-hint">{{ getText('contact.whatsapp.hint') }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useLanguageStore } from '@/stores/language'

const languageStore = useLanguageStore()
const getText = languageStore.getText

const showModal = ref(false)

// 二维码图片路径 - 用户需要将实际的二维码图片放在 public 目录下
const wechatQRCode = '/images/wechat-qr.png'
const whatsappQRCode = '/images/whatsapp-qr.png'

const closeModal = () => {
  showModal.value = false
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  // 如果图片加载失败，显示占位符
  img.style.display = 'none'
  const wrapper = img.parentElement
  if (wrapper) {
    wrapper.innerHTML = `
      <div class="qr-placeholder">
        <span>请添加二维码图片</span>
        <span class="qr-placeholder-path">${img.src.split('/').pop()}</span>
      </div>
    `
  }
}
</script>

<style scoped>
.contact-button-wrapper {
  position: relative;
}

/* 固定在右侧中间的按钮 */
.contact-button {
  position: fixed;
  top: 50%;
  right: 16px;
  transform: translateY(-50%);
  z-index: 999;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 10px;
  background: white;
  color: #2563eb;
  border: 2px solid #93c5fd;
  border-radius: 50%;
  width: 70px;
  height: 70px;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.contact-button:hover {
  transform: translateY(-50%) scale(1.05);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3);
  background: #f0f7ff;
  border-color: #60a5fa;
  color: #1d4ed8;
}

.contact-button:active {
  transform: translateY(-50%) scale(0.98);
  background: #e0f0ff;
}

.contact-icon-image {
  width: 32px;
  height: 32px;
  object-fit: contain;
  flex-shrink: 0;
}

.contact-text {
  font-size: 10px;
  white-space: nowrap;
  line-height: 1.2;
  font-weight: 600;
}

/* 模态框遮罩 */
.contact-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 模态框容器 */
.contact-modal-container {
  position: relative;
  background: white;
  border-radius: 16px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 关闭按钮 */
.contact-close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 32px;
  height: 32px;
  border: none;
  background: #f3f4f6;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #6b7280;
  transition: all 0.2s;
  z-index: 10;
}

.contact-close-btn:hover {
  background: #e5e7eb;
  color: #374151;
  transform: rotate(90deg);
}

/* 模态框内容 */
.contact-modal-content {
  padding: 40px 32px 32px;
}

.contact-modal-title {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
  text-align: center;
}

.contact-modal-subtitle {
  font-size: 14px;
  color: #6b7280;
  text-align: center;
  margin: 0 0 32px 0;
}

/* 二维码容器 */
.qr-codes-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 32px;
  margin-top: 24px;
}

.qr-code-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.qr-code-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}

.qr-icon {
  font-size: 20px;
}

.qr-code-wrapper {
  width: 200px;
  height: 200px;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  margin-bottom: 12px;
  transition: all 0.3s;
}

.qr-code-wrapper:hover {
  border-color: #2563eb;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
}

.qr-code-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.qr-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  font-size: 14px;
  height: 100%;
  gap: 4px;
}

.qr-placeholder-path {
  font-size: 12px;
  color: #d1d5db;
}

.qr-code-hint {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .contact-button {
    right: 12px;
    width: 60px;
    height: 60px;
    padding: 8px;
  }

  .contact-icon-image {
    width: 28px;
    height: 28px;
  }

  .contact-text {
    font-size: 9px;
  }

  .contact-modal-container {
    width: 95%;
    max-height: 85vh;
  }

  .contact-modal-content {
    padding: 32px 24px 24px;
  }

  .contact-modal-title {
    font-size: 20px;
  }

  .qr-codes-container {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .qr-code-wrapper {
    width: 180px;
    height: 180px;
  }
}

@media (max-width: 480px) {
  .contact-button {
    right: 8px;
    width: 55px;
    height: 55px;
    padding: 6px;
    gap: 3px;
  }

  .contact-icon-image {
    width: 24px;
    height: 24px;
  }

  .contact-text {
    font-size: 8px;
  }

  .qr-code-wrapper {
    width: 160px;
    height: 160px;
  }
}
</style>

