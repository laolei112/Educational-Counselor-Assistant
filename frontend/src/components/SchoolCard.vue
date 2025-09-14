<template>
  <div class="school-card">
    <div class="card-header">
      <h3 class="school-name">{{ school.name }}</h3>
      <span 
        v-if="school.category === 'government'"
        :class="['category-tag', `tag-${school.category}`]"
      >
        {{ getCategoryLabel(school.category) }}
      </span>
    </div>

    <div class="card-content">
      <div class="tags-row">
        <span class="band-tag">Band1比例 {{ school.band1Rate }}%</span>
        <span 
          :class="['status-tag', `status-${school.applicationStatus}`]"
        >
          {{ getStatusLabel(school.applicationStatus) }}
        </span>
        <span 
          v-if="school.category !== 'government'"
          :class="['category-tag', `tag-${school.category}`]"
        >
          {{ getCategoryLabel(school.category) }}
        </span>
      </div>

      <div class="info-row">
        <div class="info-item">
          <span class="icon">📍</span>
          {{ school.district }} | {{ school.schoolNet }}
        </div>
      </div>

      <div class="info-row">
        <div class="info-item">
          <span class="icon">👥</span>
          {{ getGenderLabel(school.gender) }}
        </div>
        <div class="info-item">
          <span class="icon">💰</span>
          学费：${{ school.tuition.toLocaleString() }}/年
        </div>
      </div>

      <div class="feeder-info">
        <span class="icon">🎓</span>
        衔接：{{ [...school.feederSchools, ...school.linkedUniversities].join('、') }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { School } from '@/types/school'

interface Props {
  school: School
}

defineProps<Props>()

const getCategoryLabel = (category: string) => {
  const labels = {
    elite: '名校联盟',
    traditional: '传统名校',
    direct: '直资学校',
    government: '官立学校'
  }
  return labels[category as keyof typeof labels] || category
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
    girls: '女校'
  }
  return labels[gender as keyof typeof labels] || gender
}
</script>

<style scoped>
.school-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.school-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.school-name {
  font-size: 20px;
  font-weight: bold;
  color: #1f2937;
  margin: 0;
  flex: 1;
  margin-right: 12px;
}

.category-tag {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.tag-elite {
  background-color: #dbeafe;
  color: #1d4ed8;
}

.tag-traditional {
  background-color: #fef3c7;
  color: #d97706;
}

.tag-direct {
  background-color: #fce7f3;
  color: #be185d;
}

.tag-government {
  background-color: #f3f4f6;
  color: #374151;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tags-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.band-tag {
  background-color: #10b981;
  color: white;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 600;
}

.status-tag {
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 600;
}

.status-open {
  background-color: #10b981;
  color: white;
}

.status-closed {
  background-color: #ef4444;
  color: white;
}

.status-deadline {
  background-color: #f59e0b;
  color: white;
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
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
  
  .school-name {
    margin-right: 0;
    margin-bottom: 4px;
    font-size: 18px;
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