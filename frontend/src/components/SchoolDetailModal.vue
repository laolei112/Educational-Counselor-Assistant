<template>
  <div v-if="visible" class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop>
      <!-- 关闭按钮 -->
      <button class="close-btn" @click="closeModal">
        <span>✕</span>
      </button>

      <!-- 学校名称和状态 -->
      <div class="header">
        <h2 class="school-name">{{ displayName }}</h2>
        <div class="school-meta">
          <span class="district">{{ districtText }}</span>
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
                  {{ teachingLanguageText }}
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
              <label>学费</label>
              <div>{{ formatTuition(school.tuition) }}</div>
            </div>
            <div class="info-item">
              <label>课程类型</label>
              <div>{{ curriculumTypesText }}</div>
            </div>
            <div v-if="school.religion" class="info-item">
              <label>宗教</label>
              <div>{{ religionText }}</div>
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
            <li v-for="(feature, idx) in featuresTexts" :key="idx">
              • {{ feature }}
            </li>
          </ul>
        </section>

        <!-- 入学信息部分（中学特有） -->
        <section v-if="school.type === 'secondary' && school.admissionInfo" class="admission-info">
          <h3>📝 中一入学信息</h3>
          <div class="admission-content" v-html="school.admissionInfo"></div>
        </section>

        <!-- 插班信息部分（中学特有） -->
        <section v-if="school.type === 'secondary' && school.transferInfo && (school.transferInfo.S1 || school.transferInfo.插班)" class="transfer-info">
          <div class="transfer-header">
            <h3>✏️ 入学申请</h3>
            <span 
              v-if="getTransferStatus()"
              :class="['status-tag', `status-${getTransferStatus()}`]"
            >
              {{ getTransferStatusLabel() }}
            </span>
          </div>
          
          <!-- 申请卡片 -->
          <div class="application-cards">
            <!-- 中一申请卡片 -->
            <div 
              v-if="school.transferInfo.S1"
              :class="['application-card', getCardStatus(school.transferInfo.S1)]"
            >
              <div class="card-status-badge">
                {{ isCardOpen(school.transferInfo.S1) ? 'OPEN' : 'CLOSED' }}
              </div>
              <div class="card-content">
                <div class="card-grade">中一</div>
                <div class="card-period">
                  {{ formatDateRange(school.transferInfo.S1.入学申请开始时间, school.transferInfo.S1.入学申请截至时间) }}
                </div>
              </div>
            </div>

            <!-- 插班申请卡片 -->
            <div 
              v-if="school.transferInfo.插班"
              :class="['application-card', getCardStatus(school.transferInfo.插班, true)]"
            >
              <div class="card-status-badge">
                {{ isCardOpen(school.transferInfo.插班, true) ? 'OPEN' : 'CLOSED' }}
              </div>
              <div class="card-content">
                <div class="card-grade">{{ getTransferGradeText() }}</div>
                <div class="card-period">
                  {{ formatTransferDateRange() }}
                </div>
              </div>
            </div>
          </div>

          <!-- 申请详情说明 -->
          <div v-if="school.admissionInfo" class="application-details">
            <div class="details-text" v-html="extractAdmissionDetails()"></div>
          </div>

          <!-- 入学准则 -->
          <div v-if="hasAdmissionCriteria()" class="admission-criteria">
            <div class="criteria-list">
              <div 
                v-for="(criterion, idx) in extractAdmissionCriteria()" 
                :key="idx"
                class="criterion-item"
              >
                {{ criterion }}
              </div>
            </div>
          </div>
        </section>

        <!-- 课程设置部分（中学特有） -->
        <section v-if="school.type === 'secondary' && school.schoolCurriculum" class="curriculum">
          <h3>📚 课程设置（DSE）</h3>
          <div class="curriculum-table-wrapper">
            <table class="curriculum-table">
              <thead>
                <tr>
                  <th class="lang-header">授课语言</th>
                  <th class="subjects-header">科目</th>
                  <th class="count-header">科目数</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="school.schoolCurriculum['中文授课'] && school.schoolCurriculum['中文授课'].length > 0">
                  <td class="lang-cell">中文授课</td>
                  <td class="subjects-cell">
                    <div class="subjects-list">
                      {{ school.schoolCurriculum['中文授课'].join('、') }}
                    </div>
                  </td>
                  <td class="count-cell">{{ school.schoolCurriculum['中文授课'].length }}</td>
                </tr>
                <tr v-if="school.schoolCurriculum['英文授课'] && school.schoolCurriculum['英文授课'].length > 0">
                  <td class="lang-cell">英文授课</td>
                  <td class="subjects-cell">
                    <div class="subjects-list">
                      {{ school.schoolCurriculum['英文授课'].join('、') }}
                    </div>
                  </td>
                  <td class="count-cell">{{ school.schoolCurriculum['英文授课'].length }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- 联络信息部分 -->
        <section v-if="school.contact" class="contact">
          <h3>📞 联络信息</h3>
          <div class="contact-info">
            <div v-if="school.contact.address" class="contact-item">
              <label>地址：</label>
              <span>{{ addressText }}</span>
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
              <a :href="school.contact.website" target="_blank" rel="noopener noreferrer" class="website-link">
                {{ school.contact.website }}
              </a>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted, computed, onMounted } from 'vue'
import type { School } from '@/types/school'
import { formatTuition } from '@/utils/formatter'
import { useLanguageStore } from '@/stores/language'

interface Props {
  school: School
  visible: boolean
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 控制教学语言说明弹窗显示
const showLanguageInfo = ref(false)

// 语言切换与文本转换
const languageStore = useLanguageStore()
const currentLanguage = computed(() => languageStore.currentLanguage)

// 同步转换（使用本地转换器）
const convertIfNeeded = (text?: string | null): string => {
  const val = text || ''
  if (!val) return ''
  return currentLanguage.value === 'zh-TW' ? languageStore.convertText(val) : val
}

const displayName = computed(() => {
  if (currentLanguage.value === 'zh-TW' && props.school.nameTraditional) {
    return props.school.nameTraditional
  }
  return convertIfNeeded(props.school.name)
})

const districtText = computed(() => convertIfNeeded(props.school.district))
const religionText = computed(() => convertIfNeeded(props.school.religion))
const addressText = computed(() => convertIfNeeded(props.school.contact?.address))
const teachingLanguageText = computed(() => convertIfNeeded(props.school.teachingLanguage || '中英文并重'))
const featuresTexts = computed(() => Array.isArray(props.school.features) ? props.school.features.map(f => convertIfNeeded(f)) : [])

// 从 school.schoolCurriculum 中解析课程体系
const curriculumTypesText = computed(() => {
  const sc = (props.school as any).schoolCurriculum
  if (!sc) return 'DSE'
  try {
    const data = typeof sc === 'string' ? JSON.parse(sc) : sc
    const types = data && data['课程体系']
    if (Array.isArray(types) && types.length) return types.join(' + ')
    if (typeof types === 'string' && types.trim()) return types
  } catch (_) {
    // ignore parse error
  }
  return 'DSE'
})

// 监听弹窗显示状态，控制 body 滚动
watch(() => props.visible, (newVisible) => {
  if (newVisible) {
    // 弹窗打开时，禁用 body 滚动
    document.body.style.overflow = 'hidden'
  } else {
    // 弹窗关闭时，恢复 body 滚动
    document.body.style.overflow = ''
    showLanguageInfo.value = false
  }
})

// 组件销毁时确保恢复 body 滚动
onUnmounted(() => {
  document.body.style.overflow = ''
})

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

// 插班信息相关函数
const getTransferStatus = () => {
  if (!props.school.transferInfo) return null
  const transferInfo = props.school.transferInfo
  
  // 检查是否有开放的申请
  const now = new Date()
  const hasOpen = 
    (transferInfo.S1 && isCardOpen(transferInfo.S1)) ||
    (transferInfo.插班 && isCardOpen(transferInfo.插班, true))
  
  if (hasOpen) return 'open'
  return 'closed'
}

const getTransferStatusLabel = () => {
  const status = getTransferStatus()
  if (status === 'open') return '进行中'
  return '已关闭'
}

const isCardOpen = (info: any, isTransfer = false): boolean => {
  if (!info) return false
  
  const now = new Date()
  
  if (isTransfer) {
    // 检查插班信息，可能有多个时间段
    const start1 = info.插班申请开始时间1 ? parseDate(info.插班申请开始时间1) : null
    const end1 = info.插班申请截止时间1 ? parseDate(info.插班申请截止时间1) : null
    const start2 = info.插班申请开始时间2 ? parseDate(info.插班申请开始时间2) : null
    const end2 = info.插班申请截止时间2 ? parseDate(info.插班申请截止时间2) : null
    
    if (start1 && end1 && now >= start1 && now <= end1) return true
    if (start2 && end2 && now >= start2 && now <= end2) return true
    return false
  } else {
    // S1申请
    const start = info.入学申请开始时间 ? parseDate(info.入学申请开始时间) : null
    const end = info.入学申请截至时间 ? parseDate(info.入学申请截至时间) : null
    
    if (start && end && now >= start && now <= end) return true
    return false
  }
}

const parseDate = (dateStr: string): Date | null => {
  if (!dateStr || typeof dateStr !== 'string') return null
  
  const trimmed = dateStr.trim()
  if (!trimmed) return null
  
  // 尝试多种日期格式
  // 格式1: 2025.1.2, 2025-1-2, 2025/1/2
  let match = trimmed.match(/^(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})$/)
  if (match) {
    const year = parseInt(match[1])
    const month = parseInt(match[2]) - 1
    const day = parseInt(match[3])
    if (month >= 0 && month <= 11 && day >= 1 && day <= 31) {
      return new Date(year, month, day)
    }
  }
  
  // 格式2: 20250102
  match = trimmed.match(/^(\d{4})(\d{2})(\d{2})$/)
  if (match) {
    const year = parseInt(match[1])
    const month = parseInt(match[2]) - 1
    const day = parseInt(match[3])
    if (month >= 0 && month <= 11 && day >= 1 && day <= 31) {
      return new Date(year, month, day)
    }
  }
  
  // 尝试直接解析（ISO格式等）
  const parsed = new Date(trimmed)
  if (!isNaN(parsed.getTime())) {
    // 验证日期是否合理
    const year = parsed.getFullYear()
    if (year >= 2000 && year <= 2100) {
      return parsed
    }
  }
  
  return null
}

const formatDateRange = (start?: string, end?: string): string => {
  if (!start || !end) return '-'
  const formatDate = (dateStr: string): string => {
    const date = parseDate(dateStr)
    if (!date) return dateStr
    return `${date.getFullYear()}.${date.getMonth() + 1}.${date.getDate()}`
  }
  return `${formatDate(start)}-${formatDate(end)}`
}

const formatTransferDateRange = (): string => {
  const transfer = props.school.transferInfo?.插班
  if (!transfer) return '-'
  
  // 优先使用第一个时间段，如果没有则使用第二个
  if (transfer.插班申请开始时间1 && transfer.插班申请截止时间1) {
    return formatDateRange(transfer.插班申请开始时间1, transfer.插班申请截止时间1)
  }
  if (transfer.插班申请开始时间2 && transfer.插班申请截止时间2) {
    return formatDateRange(transfer.插班申请开始时间2, transfer.插班申请截止时间2)
  }
  return '-'
}

const getTransferGradeText = (): string => {
  const transfer = props.school.transferInfo?.插班
  if (!transfer) return '中二至中五'
  
  // 优先使用第一个年级，如果没有则使用第二个
  if (transfer.可插班年级1) {
    return transfer.可插班年级1
  }
  if (transfer.可插班年级2) {
    return transfer.可插班年级2
  }
  return '中二至中五'
}

const getCardStatus = (info: any, isTransfer = false): string => {
  return isCardOpen(info, isTransfer) ? 'card-open' : 'card-closed'
}

const extractAdmissionDetails = (): string => {
  if (!props.school.admissionInfo) return ''
  // 提取申请详情部分（排除入学准则）
  const text = props.school.admissionInfo
  // 尝试提取入学准则之前的内容
  const criteriaMatch = text.match(/入学准则|收生准则|录取标准/)
  if (criteriaMatch) {
    return text.substring(0, criteriaMatch.index)
  }
  // 如果没有找到入学准则，返回全部内容
  return text
}

const hasAdmissionCriteria = (): boolean => {
  return extractAdmissionCriteria().length > 0
}

const extractAdmissionCriteria = (): string[] => {
  if (!props.school.admissionInfo) return []
  const text = props.school.admissionInfo
  
  // 尝试提取入学准则
  const criteriaMatch = text.match(/(入学准则|收生准则|录取标准)[：:]?\s*([^\n]+(?:\n[^\n]+)*)/i)
  if (criteriaMatch) {
    const criteriaText = criteriaMatch[2]
    // 按行分割，过滤空行
    const lines = criteriaText.split('\n').filter(line => line.trim())
    // 提取带百分比的条目
    const criteria = lines.filter(line => {
      const trimmed = line.trim()
      // 匹配包含百分比的条目，如 "1. 面试表现 35%;"
      return /\d+%/.test(trimmed) && (/^\d+\./.test(trimmed) || /^[•·]/.test(trimmed))
    })
    return criteria.length > 0 ? criteria : lines.slice(0, 5) // 最多返回5条
  }
  
  // 如果没有找到明确的准则部分，尝试在整个文本中查找带百分比的条目
  const percentagePattern = /(\d+\.\s*[^：:]+[：:]?\s*\d+%[；;]?)/g
  const matches = text.match(percentagePattern)
  return matches || []
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
  overscroll-behavior: contain;
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
  position: relative;
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

/* 入学信息样式 */
.admission-content {
  color: #2c3e50;
  font-size: 15px;
  line-height: 1.8;
}

/* 插班信息样式 */
.transfer-info {
  margin-bottom: 32px;
}

.transfer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.transfer-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  padding-bottom: 8px;
  border-bottom: 2px solid #e9ecef;
  flex: 1;
}

.status-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  margin-left: 12px;
}

.status-tag.status-open {
  background: #d1fae5;
  color: #065f46;
}

.status-tag.status-closed {
  background: #fee2e2;
  color: #991b1b;
}

.application-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.application-card {
  position: relative;
  padding: 16px;
  border-radius: 12px;
  border: 2px solid;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all 0.2s;
}

.application-card.card-open {
  background: #d1fae5;
  border-color: #10b981;
  color: #065f46;
}

.application-card.card-closed {
  background: #f3f4f6;
  border-color: #9ca3af;
  color: #6b7280;
}

.card-status-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.card-open .card-status-badge {
  background: rgba(255, 255, 255, 0.9);
  color: #065f46;
}

.card-closed .card-status-badge {
  background: rgba(255, 255, 255, 0.9);
  color: #6b7280;
}

.card-content {
  flex: 1;
  padding-right: 60px;
}

.card-grade {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.card-period {
  font-size: 13px;
  opacity: 0.9;
}

.application-details {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.details-text {
  color: #2c3e50;
  font-size: 14px;
  line-height: 1.8;
}

.details-text p {
  margin: 8px 0;
}

.details-text p:first-child {
  margin-top: 0;
}

.details-text p:last-child {
  margin-bottom: 0;
}

.admission-criteria {
  margin-top: 16px;
}

.criteria-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.criterion-item {
  color: #2c3e50;
  font-size: 14px;
  line-height: 1.6;
  padding: 8px 0;
}

.admission-content p {
  margin: 8px 0;
}

.admission-content ul,
.admission-content ol {
  margin: 8px 0;
  padding-left: 24px;
}

.admission-content li {
  margin: 4px 0;
  line-height: 1.6;
}

.admission-content strong,
.admission-content b {
  font-weight: 600;
  color: #2c3e50;
}

.admission-content br {
  line-height: 2;
}

/* 课程设置表格样式 */
.curriculum-table-wrapper {
  overflow-x: auto;
}

.curriculum-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  background: white;
}

.curriculum-table thead {
  background: #f8f9fa;
}

.curriculum-table th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border: 1px solid #dee2e6;
}

.curriculum-table td {
  padding: 12px;
  border: 1px solid #dee2e6;
  color: #2c3e50;
}

.curriculum-table .lang-header {
  width: 100px;
}

.curriculum-table .count-header {
  width: 80px;
  text-align: center;
}

.curriculum-table .lang-cell {
  font-weight: 600;
  color: #495057;
  white-space: nowrap;
  vertical-align: top;
}

.curriculum-table .count-cell {
  text-align: center;
  font-weight: 600;
  color: #007bff;
  vertical-align: top;
}

.curriculum-table .subjects-cell {
  max-width: 500px;
}

.curriculum-table .subjects-list {
  line-height: 1.8;
  word-wrap: break-word;
}

.curriculum-table tbody tr:hover {
  background: #f8f9fa;
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

.website-link {
  color: #007bff;
  text-decoration: none;
  transition: all 0.2s;
  word-break: break-all;
}

.website-link:hover {
  color: #0056b3;
  text-decoration: underline;
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
  transition: opacity 0.2s;
  display: inline-block;
}

.info-icon:hover {
  opacity: 1;
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
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow: hidden;
  width: 420px;
  max-width: calc(100vw - 40px);
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

  .info-icon {
    font-size: 16px;
  }

  .transfer-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .transfer-header h3 {
    border-bottom: none;
    padding-bottom: 0;
  }

  .status-tag {
    margin-left: 0;
  }

  .application-cards {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .application-card {
    padding: 14px;
  }
}

/* 移动端样式调整 */
@media (max-width: 480px) {
  /* 教学语言弹窗在手机上宽度调整 */
  .language-info-popup {
    width: 90%;
    max-width: 400px;
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
}

/* 极小屏手机端单列布局 - 仅在非常小的屏幕上使用单列 */
@media (max-width: 360px) {
  .info-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style> 