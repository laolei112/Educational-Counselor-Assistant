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
              <label>教学语言</label>
              <div>{{ school.teachingLanguage || '中英文并重' }}</div>
            </div>
            <div class="info-item">
              <label>学费范围</label>
              <div>${{ school.tuition }}港元/年</div>
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
import type { School } from '@/types/school'

interface Props {
  school: School
  visible: boolean
}

interface Emits {
  (e: 'close'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const closeModal = () => {
  emit('close')
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
}
</style> 