<template>
  <div class="school-card" @click="handleCardClick">
    <div class="card-header">
      <div class="title-row">
        <h3 class="school-name">{{ school.name }}</h3>
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
        <span class="tuition">学费：{{ formatTuition(school.tuition) }}</span>
      </div>

      <div v-if="school.linkedSchools && school.linkedSchools.length" class="linked-schools">
        直属中学：{{ school.linkedSchools.join('、') }}
      </div>

      <div class="bottom-row">
        <div class="status-info">
          <span 
            v-if="school.applicationStatus"
            :class="['status-badge', `status-${school.applicationStatus}`]"
          >
            {{ getStatusLabel(school.applicationStatus) }}
          </span>
          <span v-if="school.applicationDeadline" class="deadline">
            截止：{{ school.applicationDeadline }}
          </span>
        </div>
        
        <!-- 小学显示升学比例 -->
        <div v-if="school.type === 'primary' && school.band1Rate !== undefined" class="band-rate">
          <span class="rate-circle">升Band 1比例：{{ school.band1Rate }}%</span>
          <span class="arrow">→</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { School } from '@/types/school'

interface Props {
  school: School
}

interface Emits {
  (e: 'click', school: School): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const handleCardClick = () => {
  emit('click', props.school)
}

const getSchoolTypeLabel = (type: string) => {
  const labels = {
    elite: '名校联盟',
    traditional: '传统名校',
    direct: '直资学校',
    government: '官立学校',
    private: '私立学校',
    aided: '资助学校'
  }
  return labels[type as keyof typeof labels] || type
}

const getStatusLabel = (status: string) => {
  const labels = {
    open: '开放申请',
    closed: '申请截止',
    deadline: '即将截止'
  }
  return labels[status as keyof typeof labels] || status
}

const getGenderLabel = (gender: string) => {
  const labels = {
    coed: '男女校',
    boys: '男校',
    girls: '女校',
    '男': '男校',
    '女': '女校',
    '男女': '男女校'
  }
  return labels[gender as keyof typeof labels] || gender
}

const formatTuition = (tuition: number | string | undefined) => {
  if (tuition === undefined || tuition === null) {
    return '未提供'
  }
  
  // 如果是数字，格式化为千分位
  if (typeof tuition === 'number') {
    return `${tuition.toLocaleString()}港元/年`
  }
  
  // 如果是字符串，直接返回（中学数据可能是字符串格式）
  if (typeof tuition === 'string') {
    // 如果已经包含货币符号或"免费"等字样，直接返回
    if (tuition.includes('$') || tuition.includes('免费') || tuition.includes('港元')) {
      return tuition
    }
    // 否则尝试解析为数字
    const num = parseFloat(tuition)
    if (!isNaN(num)) {
      return `${num.toLocaleString()}港元/年`
    }
    return tuition
  }
  
  return '未提供'
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
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

.linked-schools {
  color: #4338ca;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
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

.band-rate {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.rate-circle {
  background: #fbbf24;
  color: #92400e;
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 13px;
  white-space: nowrap;
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
  }
  
  .school-name {
    font-size: 18px;
    min-width: 0; /* 允许文本截断 */
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
}
</style> 