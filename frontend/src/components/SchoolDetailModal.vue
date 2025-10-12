<template>
  <div v-if="visible" class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop>
      <!-- 关闭按钮 -->
      <button class="close-btn" @click="closeModal">
        <span>✕</span>
      </button>

      <!-- 学校名称和状态 -->
      <div class="header">
        <h2 class="school-name">{{ school.name }}</h2>
        <div class="school-meta">
          <span class="district">{{ school.district }}</span>
          <span class="separator">|</span>
          <span class="school-category">{{ getCategoryLabel(school.category) }}</span>
        </div>
        <span 
          :class="['status-badge', `status-${school.applicationStatus}`]"
        >
          {{ getStatusLabel(school.applicationStatus) }}
        </span>
      </div>

      <!-- 查看插班详细信息链接 -->
      <div class="info-link">
        <a href="#" class="detail-link">🔗 查看插班详细信息 ↗</a>
      </div>

      <div class="content">
        <!-- 基本信息部分 -->
        <section class="basic-info">
          <h3>📋 基本信息</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>学校规模</label>
              <div v-if="school.schoolScale">
                {{ school.schoolScale.classes }}班
              </div>
              <div v-else>-</div>
            </div>
            <div class="info-item">
              <label>
                教学语言
                <span class="info-icon" @click="showLanguageInfo = !showLanguageInfo">ℹ️</span>
              </label>
              <div class="teaching-language-wrapper">
                <span class="language-text">
                  {{ school.teachingLanguage || '中英文并重' }}
                </span>
              </div>
              <!-- 教学语言说明弹窗 -->
              <div v-if="showLanguageInfo" class="language-info-popup" @click.stop>
                <div class="popup-header">
                  <span>教学语言分类标准</span>
                  <button class="popup-close" @click="showLanguageInfo = false">✕</button>
                </div>
                <div class="popup-content">
                  <table class="language-table">
                    <thead>
                      <tr>
                        <th>分类</th>
                        <th>英文授课占比</th>
                        <th>说明</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td class="category">英文</td>
                        <td class="ratio">≥ 80%</td>
                        <td class="desc">绝大部分科目使用英文授课</td>
                      </tr>
                      <tr>
                        <td class="category">主要英文</td>
                        <td class="ratio">60% - 79%</td>
                        <td class="desc">多数科目使用英文授课</td>
                      </tr>
                      <tr class="highlight">
                        <td class="category">中英文并重</td>
                        <td class="ratio">40% - 59%</td>
                        <td class="desc">中英文授课科目数量接近</td>
                      </tr>
                      <tr>
                        <td class="category">主要中文</td>
                        <td class="ratio">20% - 39%</td>
                        <td class="desc">多数科目使用中文授课</td>
                      </tr>
                      <tr>
                        <td class="category">中文</td>
                        <td class="ratio">< 20%</td>
                        <td class="desc">绝大部分科目使用中文授课</td>
                      </tr>
                    </tbody>
                  </table>
                  <div class="popup-note">
                    注：基于中四至中六 DSE 科目统计
                  </div>
                </div>
              </div>
            </div>
            <div class="info-item">
              <label>学费范围</label>
              <div>{{ formatTuition(school.tuition) }}</div>
            </div>
            <div class="info-item">
              <label>课程类型</label>
              <div v-if="school.curriculum && school.curriculum.length">
                {{ school.curriculum.join('+') }}
              </div>
              <div v-else>DSE</div>
            </div>
            <div v-if="school.religion" class="info-item">
              <label>宗教</label>
              <div>{{ school.religion }}</div>
            </div>
            <div class="info-item">
              <label>性别类型</label>
              <div>{{ getGenderLabel(school.gender) }}</div>
            </div>
          </div>
        </section>

        <!-- 学校特色部分 -->
        <section v-if="school.features && school.features.length" class="features">
          <h3>❤️ 学校特色</h3>
          <ul class="features-list">
            <li v-for="feature in school.features" :key="feature">
              • {{ feature }}
            </li>
          </ul>
        </section>

        <!-- 联络信息部分 -->
        <section v-if="school.contact" class="contact">
          <h3>📞 联络信息</h3>
          <div class="contact-info">
            <div v-if="school.contact.address" class="contact-item">
              <label>地址：</label>
              <span>{{ school.contact.address }}</span>
            </div>
            <div v-if="school.contact.phone" class="contact-item">
              <label>电话：</label>
              <span>{{ school.contact.phone }}</span>
            </div>
            <div v-if="school.contact.email" class="contact-item">
              <label>邮箱：</label>
              <span>{{ school.contact.email }}</span>
            </div>
            <div v-if="school.contact.website" class="contact-item">
              <label>网址：</label>
              <span>{{ school.contact.website }}</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { School } from '@/types/school'
import { formatTuition } from '@/utils/formatter'

interface Props {
  school: School
  visible: boolean
}

interface Emits {
  (e: 'close'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

// 控制教学语言说明弹窗显示
const showLanguageInfo = ref(false)

const closeModal = () => {
  emit('close')
  showLanguageInfo.value = false
}

const getCategoryLabel = (category: string) => {
  const labels = {
    elite: '名校联盟',
    traditional: '传统名校',
    direct: '直资中学',
    government: '官立学校',
    private: '私立学校'
  }
  return labels[category as keyof typeof labels] || category
}

const getStatusLabel = (status: string) => {
  const labels = {
    open: '插班开放中',
    closed: '申请截止',
    deadline: '即将截止'
  }
  return labels[status as keyof typeof labels] || status
}

const getGenderLabel = (gender: string) => {
  const labels = {
    coed: '男女校',
    boys: '男校',
    girls: '女校'
  }
  return labels[gender as keyof typeof labels] || gender
}
</script>

<style scoped>
.modal-overlay {
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
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 16px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #666;
  z-index: 10;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.2);
}

.header {
  padding: 24px 24px 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 16px 16px 0 0;
}

.school-name {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.school-meta {
  font-size: 16px;
  color: #6c757d;
  margin-bottom: 12px;
}

.separator {
  margin: 0 8px;
}

.status-badge {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.status-open {
  background: #d4edda;
  color: #155724;
}

.status-closed {
  background: #f8d7da;
  color: #721c24;
}

.status-deadline {
  background: #fff3cd;
  color: #856404;
}

.info-link {
  padding: 0 24px 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.detail-link {
  color: #007bff;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}

.detail-link:hover {
  text-decoration: underline;
}

.content {
  padding: 24px;
}

section {
  margin-bottom: 32px;
}

section:last-child {
  margin-bottom: 0;
}

section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #e9ecef;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item label {
  font-size: 14px;
  font-weight: 500;
  color: #6c757d;
}

.info-item div {
  font-size: 16px;
  color: #2c3e50;
  font-weight: 500;
}

.features-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.features-list li {
  padding: 8px 0;
  color: #2c3e50;
  font-size: 15px;
  line-height: 1.5;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.contact-item {
  display: flex;
  align-items: center;
  font-size: 15px;
}

.contact-item label {
  font-weight: 600;
  color: #6c757d;
  min-width: 60px;
  margin-right: 8px;
}

.contact-item span {
  color: #2c3e50;
}

/* 教学语言相关样式 */
.info-item label {
  position: relative;
}

.info-icon {
  font-size: 14px;
  cursor: pointer;
  margin-left: 6px;
  opacity: 0.6;
  transition: all 0.2s;
  display: inline-block;
}

.info-icon:hover {
  opacity: 1;
  transform: scale(1.15);
}

.teaching-language-wrapper {
  position: relative;
}

.language-text {
  font-weight: 500;
  color: #2c3e50;
}

/* 教学语言说明弹窗 */
.language-info-popup {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 100;
  overflow: hidden;
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 2px solid #e9ecef;
  font-weight: 600;
  font-size: 14px;
  color: #2c3e50;
}

.popup-close {
  background: #e9ecef;
  border: none;
  color: #6c757d;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.2s;
}

.popup-close:hover {
  background: #dee2e6;
  color: #2c3e50;
}

.popup-content {
  padding: 16px;
}

/* 表格样式 */
.language-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.language-table thead {
  background: #f8f9fa;
}

.language-table th {
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.language-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #e9ecef;
  color: #2c3e50;
}

.language-table tbody tr:last-child td {
  border-bottom: none;
}

.language-table tbody tr:hover {
  background: #f8f9fa;
}

.language-table tbody tr.highlight {
  background: #fff3cd;
}

.language-table tbody tr.highlight:hover {
  background: #ffe69c;
}

.language-table .category {
  font-weight: 600;
  color: #2c3e50;
  white-space: nowrap;
}

.language-table .ratio {
  font-weight: 500;
  color: #495057;
  white-space: nowrap;
}

.language-table .desc {
  color: #6c757d;
  font-size: 12px;
}

.popup-note {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e9ecef;
  font-size: 11px;
  color: #6c757d;
}

@media (max-width: 768px) {
  .modal-container {
    margin: 10px;
    max-height: 95vh;
  }
  
  .header {
    padding: 20px 16px 12px;
  }
  
  .school-name {
    font-size: 24px;
  }
  
  .content {
    padding: 16px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }

  /* 移动端教学语言弹窗调整 */
  .language-info-popup {
    position: fixed;
    top: 50%;
    left: 50%;
    right: auto;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 400px;
    margin-top: 0;
  }

  .language-table {
    font-size: 12px;
  }

  .language-table th,
  .language-table td {
    padding: 8px 6px;
  }

  .language-table th {
    font-size: 11px;
  }

  .language-table .desc {
    font-size: 11px;
  }

  .info-icon {
    font-size: 16px;
  }
}
</style> 