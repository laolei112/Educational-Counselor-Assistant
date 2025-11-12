<template>
  <div class="school-card" @click="handleCardClick">
    <!-- Header: 校名 + 标签 -->
    <div class="card-header">
      <h3 class="school-name">{{ getSchoolName() }}</h3>
      <div class="header-tags">
        <span 
          v-if="school.type === 'secondary' && school.schoolGroup"
          class="group-badge"
        >
          {{ school.schoolGroup }}
        </span>
        <span 
          v-if="schoolTypeTag"
          :class="['type-tag', getTypeTagClass(school.schoolType || school.category)]"
        >
          {{ schoolTypeTag }}
        </span>
        <span 
          v-if="genderTag"
          class="gender-tag"
        >
          {{ genderTag }}
        </span>
      </div>
    </div>

    <!-- Meta行: 地区 | 对应校网 | 宗教 -->
    <div class="meta-row">
      <span class="meta-item">{{ convertIfNeeded('片区') }}：{{ convertIfNeeded(school.district) || '—' }}</span>
      <span class="meta-divider">｜</span>
      <span class="meta-item">{{ convertIfNeeded('对应校网') }}：{{ school.schoolNet || '—' }}</span>
      <span class="meta-divider">｜</span>
      <span class="meta-item">{{ convertIfNeeded('宗教') }}：{{ convertIfNeeded(school.religion) || '—' }}</span>
    </div>

    <!-- KV信息区: 使用CSS Grid，固定标签列 + 自适应值列 -->
    <div class="kv-info-grid">
      <!-- 办学性质 -->
      <!-- <div class="kv-row">
        <span class="kv-label">{{ getText('school.schoolType') }}</span>
        <span class="kv-value">{{ getSchoolTypeLabel(school.schoolType || school.category) || '—' }}</span>
      </div> -->
      
      <!-- 性别 -->
      <!-- <div class="kv-row">
        <span class="kv-label">{{ getText('school.gender') }}</span>
        <span class="kv-value">{{ getGenderLabel(school.gender) || '—' }}</span>
      </div> -->
      
      <!-- 学费 -->
      <div class="kv-row">
        <span class="kv-label">{{ getText('school.tuition') }}</span>
        <span class="kv-value">{{ formatTuition(school.tuition) }}</span>
      </div>
      
      <!-- 结龙学校 -->
      <div v-if="school.secondaryInfo?.through_train" class="kv-row">
        <span class="kv-label">{{ getText('school.throughTrain') }}</span>
        <span class="kv-value truncate-text" :title="convertIfNeeded(school.secondaryInfo.through_train)">
          {{ convertIfNeeded(school.secondaryInfo.through_train) }}
        </span>
      </div>
      
      <!-- 直属中学 -->
      <div v-if="school.secondaryInfo?.direct" class="kv-row">
        <span class="kv-label">{{ getText('school.direct') }}</span>
        <span class="kv-value truncate-text" :title="convertIfNeeded(school.secondaryInfo.direct)">
          {{ convertIfNeeded(school.secondaryInfo.direct) }}
        </span>
      </div>
      
      <!-- 联系中学 -->
      <div v-if="school.secondaryInfo?.associated" class="kv-row">
        <span class="kv-label">{{ getText('school.associated') }}</span>
        <span class="kv-value truncate-text" :title="convertIfNeeded(school.secondaryInfo.associated)">
          {{ convertIfNeeded(school.secondaryInfo.associated) }}
        </span>
      </div>
    </div>

    <!-- Footer: KPI徽章（左） + 操作"详情"（右） -->
    <div class="card-footer">
      <div class="footer-left">
        <!-- 小学显示升学比例 -->
        <span 
          v-if="school.type === 'primary' && school.band1Rate !== undefined && school.band1Rate !== null"
          class="kpi-badge"
        >
          {{ getText('school.band1Rate') }}：{{ school.band1Rate }}%
        </span>
        <!-- 申请状态徽章 -->
        <span 
          v-if="applicationStatus"
          :class="['status-badge', `status-${applicationStatus}`]"
        >
          {{ getStatusLabel(applicationStatus) }}
        </span>
      </div>
      <div class="footer-right">
        <span class="details-link">{{ getText('school.details') }}→</span>
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
  if (props.school.transferInfo) {
    const transferInfo = props.school.transferInfo
    const now = new Date()
    
    // 中学：检查S1申请
    if (props.school.type === 'secondary' && transferInfo.S1 && isCardOpen(transferInfo.S1, false)) {
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
    
    // 小学：检查小一申请
    if (props.school.type === 'primary' && transferInfo.小一) {
      // 小一申请结构与S1类似，使用相同逻辑
      const p1Info = {
        入学申请开始时间: transferInfo.小一.小一入学申请开始时间,
        入学申请截至时间: transferInfo.小一.小一入学申请截至时间
      }
      if (isCardOpen(p1Info, false)) {
        const end = p1Info.入学申请截至时间 ? parseDate(p1Info.入学申请截至时间) : null
        if (end) {
          const daysUntilDeadline = Math.ceil((end.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
          if (daysUntilDeadline <= 7 && daysUntilDeadline > 0) {
            return 'deadline'
          }
        }
        return 'open'
      }
    }
    
    // 检查插班申请是否开放（中学和小学共用）
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

// 获取多语言文本（用于预定义的UI文本）
const getText = (key: string) => {
  return languageStore.getText(key)
}

// 文本转换（用于后端返回的动态文本，进行简繁体转换）
const convertIfNeeded = (text?: string | null): string => {
  const val = text || ''
  if (!val) return ''
  // 总是调用 convertText，它会根据当前语言进行正确的转换
  return languageStore.convertText(val)
}

// 获取学校类型标签
const schoolTypeTag = computed(() => {
  return getSchoolTypeLabel(props.school.schoolType || props.school.category)
})

// 获取性别标签
const genderTag = computed(() => {
  return getGenderLabel(props.school.gender)
})

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

// 获取类型标签的CSS类
const getTypeTagClass = (type: string) => {
  if (!type) return ''
  const raw = (type || '').toString().trim().toLowerCase().replace(/\s+sch$/i, '')
  if (raw === '私立' || raw === '私立学校' || raw === 'private') return 'type-private'
  if (raw === '直資' || raw === '直资' || raw === '直資學校' || raw === '直资学校' || raw === 'direct') return 'type-direct'
  if (raw === '官立' || raw === '官立学校' || raw === 'government') return 'type-government'
  if (raw === '資助' || raw === '资助' || raw === '資助學校' || raw === '资助学校' || raw === 'aided') return 'type-aided'
  return 'type-default'
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
</script>

<style scoped>
/* 卡片容器 - 使用CSS Grid实现四段式布局 */
.school-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
  border: 1px solid #f1f3f4;
  display: grid;
  grid-template-rows: auto auto 1fr auto;
  gap: 16px;
  min-height: 280px;
  height: 100%;
}

.school-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* Header: 校名 + 标签 */
.card-header {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.school-name {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  line-height: 1.3;
  min-width: 0;
  word-break: break-word;
}

.header-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.group-badge {
  background: #fbbf24;
  color: #92400e;
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 13px;
  white-space: nowrap;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.25);
}

.type-tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.type-private {
  background: #3b82f6;
  color: #f0f9ff;
}

.type-direct {
  background: #3b82f6;
  color: #f0f9ff;
}

.type-government {
  background: #3b82f6;
  color: #f0f9ff;
}

.type-aided {
  background: #3b82f6;
  color: #f0f9ff;
}

.type-default {
  background: #3b82f6;
  color: #f0f9ff;
}

.gender-tag {
  background: #3b82f6;
  color: #f0f9ff;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

/* Meta行: 地区 | 对应校网 | 宗教 */
.meta-row {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-size: 14px;
  line-height: 22px;
  flex-wrap: wrap;
}

.meta-item {
  white-space: nowrap;
}

.meta-divider {
  color: #d1d5db;
  font-weight: 300;
  user-select: none;
}

/* KV信息区: 固定标签列 + 自适应值列 */
.kv-info-grid {
  display: grid;
  grid-template-columns: 80px 1fr;
  gap: 8px 16px;
  align-content: start;
}

.kv-row {
  display: contents;
}

.kv-label {
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  line-height: 24px;
  white-space: nowrap;
}

.kv-value {
  color: #1a1a1a;
  font-size: 14px;
  font-weight: 400;
  line-height: 24px;
  word-break: break-word;
}

/* 长文本截断：最多两行 */
.truncate-text {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 24px;
  max-height: 48px; /* 2行 × 24px */
}

/* Footer: KPI徽章（左） + 操作"详情"（右） */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid #f1f3f4;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  flex: 1;
}

.footer-right {
  flex-shrink: 0;
}

.kpi-badge {
  background: #fef3c7;
  color: #92400e;
  padding: 6px 12px;
  border-radius: 16px;
  font-weight: 600;
  font-size: 12px;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 28px;
  line-height: 1;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 28px;
  line-height: 1;
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

.details-link {
  font-size: 14px;
  color: #9ca3af;
  font-weight: 600;
  white-space: nowrap;
}

/* 移动端响应式 */
@media (max-width: 768px) {
  .school-card {
    padding: 16px;
    min-height: 260px;
    gap: 12px;
  }
  
  .school-name {
    font-size: 18px;
  }
  
  .group-badge,
  .type-tag,
  .gender-tag {
    font-size: 11px;
    padding: 3px 8px;
  }
  
  .meta-row {
    font-size: 13px;
    line-height: 20px;
  }
  
  .kv-info-grid {
    grid-template-columns: 70px 1fr;
    gap: 6px 12px;
  }
  
  .kv-label,
  .kv-value {
    font-size: 13px;
    line-height: 22px;
  }
  
  .truncate-text {
    line-height: 22px;
    max-height: 44px; /* 2行 × 22px */
  }
  
  .kpi-badge,
  .status-badge {
    font-size: 11px;
    padding: 4px 10px;
    height: 24px;
    line-height: 1;
  }
  
  .details-link {
    font-size: 13px;
  }
}

/* 确保在网格布局中卡片高度一致 */
@media (min-width: 768px) {
  .school-card {
    min-height: 300px;
  }
}
</style>