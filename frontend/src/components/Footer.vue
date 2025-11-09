<template>
  <footer class="app-footer">
    <div class="footer-content">
      <!-- 上半部分：产品信息和链接 -->
      <div class="footer-top">
        <div class="footer-section">
          <h3 class="footer-title">{{ getText('footer.about.title') }}</h3>
          <p class="footer-description">{{ getText('footer.about.description') }}</p>
        </div>
        
        <div class="footer-section">
          <h3 class="footer-title">{{ getText('footer.links.title') }}</h3>
          <ul class="footer-links">
            <li><a href="#" class="footer-link">{{ getText('footer.links.home') }}</a></li>
            <li><a href="#" class="footer-link">{{ getText('footer.links.about') }}</a></li>
            <li><a href="#" class="footer-link">{{ getText('footer.links.contact') }}</a></li>
            <li><a href="#" class="footer-link">{{ getText('footer.links.privacy') }}</a></li>
          </ul>
        </div>
        
        <div class="footer-section">
          <h3 class="footer-title">{{ getText('footer.contact.title') }}</h3>
          <ul class="footer-contact">
            <li>📧 {{ getText('footer.contact.email') }}: info@example.com</li>
            <li>📱 {{ getText('footer.contact.phone') }}: +852 1234 5678</li>
          </ul>
        </div>
      </div>
      
      <!-- 分隔线 -->
      <div class="footer-divider"></div>
      
      <!-- 下半部分：版权信息 -->
      <div class="footer-bottom">
        <div class="footer-copyright">
          <p>© {{ currentYear }} {{ getText('footer.copyright.company') }}. {{ getText('footer.copyright.rights') }}</p>
          <!-- <p class="footer-icp">{{ getText('footer.copyright.icp') }}</p> -->
        </div>
        
        <div class="footer-meta">
          <span class="footer-meta-item">{{ getText('footer.meta.version') }}: v1.0.0</span>
          <span class="footer-meta-separator">|</span>
          <span class="footer-meta-item">{{ getText('footer.meta.updated') }}: 2025-11-09</span>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useLanguageStore } from '@/stores/language'

const languageStore = useLanguageStore()
const getText = languageStore.getText

// 获取当前年份
const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.app-footer {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 3rem 0 1.5rem;
  margin-top: 4rem;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.footer-top {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.footer-section {
  padding: 0;
}

.footer-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: white;
}

.footer-description {
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  font-size: 0.9rem;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 0.5rem;
}

.footer-link {
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.footer-link:hover {
  color: white;
  text-decoration: underline;
}

.footer-contact {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-contact li {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.footer-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.2);
  margin: 2rem 0;
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.footer-copyright {
  flex: 1;
}

.footer-copyright p {
  margin: 0.25rem 0;
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.875rem;
}

.footer-icp {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
}

.footer-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.75);
  font-size: 0.8rem;
}

.footer-meta-item {
  white-space: nowrap;
}

.footer-meta-separator {
  color: rgba(255, 255, 255, 0.5);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-footer {
    padding: 2rem 0 1rem;
    margin-top: 2rem;
  }
  
  .footer-top {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .footer-bottom {
    flex-direction: column;
    align-items: flex-start;
    text-align: left;
  }
  
  .footer-meta {
    flex-wrap: wrap;
  }
}
</style>

