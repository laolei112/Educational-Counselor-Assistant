<template>
  <div class="school-card" @click="handleCardClick">
    <div class="card-header">
      <div class="title-row">
        <h3 class="school-name">{{ getSchoolName() }}</h3>
        <span 
          v-if="school.type === 'secondary' && school.schoolGroup"
          class="group-badge-inline"
        >
          {{ school.schoolGroup }}
        </span>
      </div>
    </div>

    <div class="card-content">
      <div class="location-info">
        <span>{{ school.district }}</span>
        <template v-if="school.schoolNet">
          <span class="divider">｜</span>
          <span class="school-net">对应校网：{{ school.schoolNet }}</span>
        </template>
        <template v-if="school.religion">
          <span class="divider">｜</span>
          <span>{{ school.religion }}</span>
        </template>
      </div>

      <div class="location-info">
        <span class="gender">{{ getSchoolTypeLabel(school.schoolType || school.category) }}</span>
        <template v-if="school.gender">
          <span class="divider">｜</span>
          <span class="gender">{{ getGenderLabel(school.gender) }}</span>
        </template>
        <span class="divider">｜</span>
        <span class="tuition">{{ getText('school.tuition') }}：{{ formatTuition(school.tuition) }}</span>
      </div>

      <div v-if="school.secondaryInfo && hasSecondaryInfo(school.secondaryInfo)" class="secondary-info">
        <div v-if="school.secondaryInfo.through_train" class="secondary-item">
          <span class="secondary-label">{{ getText('school.throughTrain') }}：</span>
          <span class="secondary-value">{{ convertIfNeeded(school.secondaryInfo.through_train) }}</span>
        </div>
        <div v-if="school.secondaryInfo.direct" class="secondary-item">
          <span class="secondary-label">{{ getText('school.direct') }}：</span>
          <span class="secondary-value">{{ convertIfNeeded(school.secondaryInfo.direct) }}</span>
        </div>
        <div v-if="school.secondaryInfo.associated" class="secondary-item">
          <span class="secondary-label">{{ getText('school.associated') }}：</span>
          <span class="secondary-value">{{ convertIfNeeded(school.secondaryInfo.associated) }}</span>
        </div>
      </div>

      <div class="bottom-row">
        <div class="status-info">
          <span 
            v-if="applicationStatus"
            :class="['status-badge', `status-${applicationStatus}`]"
          >
            {{ getStatusLabel(applicationStatus) }}
          </span>
          <template v-if="school.transferInfo?.application_deadline">
            <span class="divider">｜</span>
            <span class="deadline">{{ getText('school.deadline') }}：{{ school.transferInfo.application_deadline }}</span>
          </template>
        </div>
        
        <!-- 小学显示升学比例和详情 -->
        <div v-if="school.type === 'primary'" class="band-rate-wrapper">
          <template v-if="school.promotionInfo?.band1_rate !== undefined">
            <span class="rate-circle">{{ getText('school.band1Rate') }}：{{ school.promotionInfo.band1_rate }}%</span>
          </template>
          <span class="arrow">{{ getText('school.details') }}→</span>
        </div>
        <div v-if="school.type === 'secondary'" class="band-rate-wrapper">
          <span class="arrow">{{ getText('school.details') }}→</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { School } from '@/types/school'
import { formatTuition } from '@/utils/formatter'
import { useLanguageStore } from '@/stores/language'

interface Props {
  school: School
}

interface Emits {
  (e: 'click', school: School): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const languageStore = useLanguageStore()

const handleCardClick = () => {
  emit('click', props.school)
}

// 检查申请是否开放
const isCardOpen = (info: any, isTransfer = false): boolean => {
  if (!info) return false
  
  const now = new Date()
  
  if (isTransfer) {
    // 检查插班信息，可能有多个时间段
    const startTime1 = info.插班申请开始时间1
    const startTime2 = info.插班申请开始时间2
    
    if (startTime1 && typeof startTime1 === 'string' && startTime1.startsWith('开放申请')) return true
    if (startTime2 && typeof startTime2 === 'string' && startTime2.startsWith('开放申请')) return true
    
    if (startTime1 && typeof startTime1 === 'string' && startTime1.startsWith('每年')) {
      const month = parseMonth(startTime1)
      if (month !== null && now.getMonth() === month) return true
    }
    if (startTime2 && typeof startTime2 === 'string' && startTime2.startsWith('每年')) {
      const month2 = parseMonth(startTime2)
      if (month2 !== null && now.getMonth() === month2) return true
    }
    
    const start1 = startTime1 ? parseDate(startTime1) : null
    const end1 = info.插班申请截止时间1 ? parseDate(info.插班申请截止时间1) : null
    const start2 = startTime2 ? parseDate(startTime2) : null
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

const parseMonth = (dateStr: string): number | null => {
  if (!dateStr || typeof dateStr !== 'string') return null
  const trimmed = dateStr.trim()
  if (!trimmed) return null
  // 格式：每年X月X日
  const match = trimmed.match(/^每年(\d{1,2})月(\d{1,2})日$/)
  if (match) {
    return parseInt(match[1]) - 1 // 月份从0开始
  }
  // 格式：每年X月xxx
  const match2 = trimmed.match(/^每年(\d{1,2})月(.*)$/)
  if (match2) {
    return parseInt(match2[1]) - 1 // 月份从0开始
  }
  return null
}

const parseDate = (dateStr: string): Date | null => {
  if (!dateStr || typeof dateStr !== 'string') return null
  
  const trimmed = dateStr.trim()
  if (!trimmed) return null
  
  // 尝试多种日期格式
  // 格式1: 2025.1.2, 2025-1-2, 2025/1/2
  let match = trimmed.match(/^(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})(?:\s+\d{1,2}:\d{1,2}:\d{1,2})?$/)
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

  // 格式3: 2025年1月2日
  match = trimmed.match(/^(\d{4})年(\d{1,2})月(\d{1,2})日$/)
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

// 计算申请状态
const applicationStatus = computed(() => {
  // 优先使用后端返回的状态
  if (props.school.transferInfo?.application_status) {
    return props.school.transferInfo.application_status
  }
  
  // 如果没有后端状态，则根据实际数据计算
  if (props.school.type === 'secondary' && props.school.transferInfo) {
    const transferInfo = props.school.transferInfo
    const now = new Date()
    
    // 检查S1申请是否开放
    if (transferInfo.S1 && isCardOpen(transferInfo.S1, false)) {
      // 检查是否即将截止（7天内）
      const end = transferInfo.S1.入学申请截至时间 ? parseDate(transferInfo.S1.入学申请截至时间) : null
      if (end) {
        const daysUntilDeadline = Math.ceil((end.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
        if (daysUntilDeadline <= 7 && daysUntilDeadline > 0) {
          return 'deadline'
        }
      }
      return 'open'
    }
    
    // 检查插班申请是否开放
    if (transferInfo.插班 && isCardOpen(transferInfo.插班, true)) {
      // 检查是否即将截止
      const end1 = transferInfo.插班.插班申请截止时间1 ? parseDate(transferInfo.插班.插班申请截止时间1) : null
      const end2 = transferInfo.插班.插班申请截止时间2 ? parseDate(transferInfo.插班.插班申请截止时间2) : null
      const nearestEnd = end1 && end2 
        ? (end1 < end2 ? end1 : end2)
        : (end1 || end2)
      
      if (nearestEnd) {
        const daysUntilDeadline = Math.ceil((nearestEnd.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
        if (daysUntilDeadline <= 7 && daysUntilDeadline > 0) {
          return 'deadline'
        }
      }
      return 'open'
    }
  }
  
  return null
})

// 获取学校名称（根据当前语言）
const getSchoolName = () => {
  return languageStore.getSchoolName(props.school)
}

// 获取多语言文本
const getText = (key: string) => {
  return languageStore.getText(key)
}

// 简繁体转换
const convertIfNeeded = (text?: string | null): string => {
  const val = text || ''
  if (!val) return ''
  return languageStore.convertText(val)
}

const getSchoolTypeLabel = (type: string) => {
  if (!type) return ''
  const raw = (type || '').toString().trim().toLowerCase().replace(/\s+sch$/i, '')
  let key = raw
  if (raw === '私立' || raw === '私立学校' || raw === 'private') key = 'private'
  else if (raw === '直資' || raw === '直资' || raw === '直資學校' || raw === '直资学校' || raw === 'direct') key = 'direct'
  else if (raw === '官立' || raw === '官立学校' || raw === 'government') key = 'government'
  else if (raw === '資助' || raw === '资助' || raw === '資助學校' || raw === '资助学校' || raw === 'aided') key = 'aided'
  else if (raw === '名校聯盟' || raw === '名校联盟' || raw === 'elite') key = 'elite'
  else if (raw === '傳統名校' || raw === '传统名校' || raw === 'traditional') key = 'traditional'
  const text = languageStore.getText(`school.type.${key}`)
  return text !== `school.type.${key}` ? text : type
}

const getStatusLabel = (status: string) => {
  const statusKey = `school.applicationStatus.${status}` as keyof typeof languageStore.getText
  return languageStore.getText(statusKey)
}

const getGenderLabel = (gender: string) => {
  if (!gender) return ''
  const raw = (gender || '').toString().trim().toLowerCase()
  let key = raw
  if (raw === '男女' || raw === '男女校' || raw === 'coed') key = 'coed'
  else if (raw === '男' || raw === '男校' || raw === 'boys') key = 'boys'
  else if (raw === '女' || raw === '女校' || raw === 'girls') key = 'girls'
  const text = languageStore.getText(`school.gender.${key}`)
  return text !== `school.gender.${key}` ? text : gender
}

const hasSecondaryInfo = (secondaryInfo: any) => {
  return secondaryInfo && (
    secondaryInfo.through_train || 
    secondaryInfo.direct || 
    secondaryInfo.associated
  )
}
</script>

<style scoped>
.school-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
  border: 1px solid #f1f3f4;
}

.school-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  gap: 12px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.school-name {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  line-height: 1.3;
  min-width: 0;
}

.group-badge-inline {
  background: #fbbf24;
  color: #92400e;
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 13px;
  white-space: nowrap;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.25);
  flex-shrink: 0;
}

.school-type-tag {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
  background: #f0f9ff;
  color: #0369a1;
}

.type-private {
  background: #f0f9ff;
  color: #0369a1;
}

.type-direct {
  background: #fef3e2;
  color: #ea580c;
}

.type-government {
  background: #f3f4f6;
  color: #374151;
}

.type-aided {
  background: #f0fdf4;
  color: #166534;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.location-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 4px;
}

.divider {
  color: #d1d5db;
  font-weight: 300;
  user-select: none;
}

.school-net {
  font-weight: 500;
}

.basic-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #374151;
  font-size: 14px;
  margin-bottom: 4px;
}

.gender {
  font-weight: 500;
}

.tuition {
  font-weight: 600;
  color: #1a1a1a;
}

.secondary-info {
  margin-bottom: 8px;
}

.secondary-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 4px;
  font-size: 14px;
  line-height: 1.4;
}

.secondary-label {
  color: #4338ca;
  font-weight: 500;
  margin-right: 8px;
  flex-shrink: 0;
  min-width: 80px;
  white-space: nowrap;
}

.secondary-value {
  color: #1a1a1a;
  font-weight: 400;
  flex: 1;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.bottom-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  gap: 12px;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.status-open {
  background: #d1fae5;
  color: #065f46;
}

.status-closed {
  background: #fee2e2;
  color: #991b1b;
}

.status-deadline {
  background: #fef3c7;
  color: #92400e;
}

.deadline {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
}

.band-rate-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.band-rate-wrapper .rate-circle {
  flex-shrink: 0;
}

.band-rate-wrapper .arrow {
  flex-shrink: 0;
}

.rate-circle {
  background: #fef3c7; /* amber-100 */
  color: #92400e; /* amber-800 */
  padding: 4px 10px; /* py-1 px-2.5 */
  border-radius: 9999px; /* rounded-full */
  font-weight: 500; /* font-medium */
  font-size: 12px; /* text-xs */
  white-space: nowrap;
}

@media (min-width: 768px) {
  .rate-circle {
    font-size: 14px; /* md:text-sm */
  }
}

.school-group {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.group-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 14px;
  white-space: nowrap;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.arrow {
  font-size: 16px;
  color: #9ca3af;
  font-weight: bold;
}

.info-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6b7280;
  font-size: 14px;
}

.feeder-info {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  color: #1d4ed8;
  font-size: 14px;
  line-height: 1.5;
}

.icon {
  font-size: 16px;
}

@media (max-width: 768px) {
  .school-card {
    padding: 16px;
  }
  
  .card-header {
    flex-direction: row; /* 保持水平布局 */
    gap: 8px;
    align-items: center;
  }
  
  .title-row {
    gap: 6px;
    flex-wrap: wrap;
  }
  
  .school-name {
    font-size: 18px;
    word-break: break-word;
    overflow-wrap: break-word;
  }
  
  .group-badge-inline {
    font-size: 11px;
    padding: 3px 8px;
    border-radius: 10px;
  }
  
  .category-tag {
    font-size: 11px; /* 稍微减小标签字体 */
    padding: 3px 8px; /* 稍微减小标签内边距 */
  }
  
  .info-row {
    flex-direction: column;
    gap: 8px;
  }
  
  .tags-row {
    gap: 8px;
  }
  
  .secondary-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }
  
  .secondary-label {
    min-width: auto;
    margin-right: 0;
  }
}
</style> 