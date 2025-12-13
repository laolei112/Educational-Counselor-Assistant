<template>
  <div class="school-detail-page">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>{{ convertIfNeeded('加载中...') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="!school" class="error-container">
      <i class="fa-solid fa-circle-exclamation"></i>
      <p>{{ convertIfNeeded('未找到学校信息') }}</p>
      <a href="/" class="back-link">{{ convertIfNeeded('返回首页') }}</a>
    </div>

    <template v-else>
      <!-- Header Section with Gradient -->
      <div class="header-gradient">
        <!-- Decorative Background Elements -->
        <div class="header-decoration header-decoration-1"></div>
        <div class="header-decoration header-decoration-2"></div>
        <div class="header-dots"></div>

        <div class="header-container">
          <!-- Breadcrumb -->
          <nav class="breadcrumb">
            <a href="/" class="breadcrumb-link">
              <i class="fa-solid fa-house"></i> {{ convertIfNeeded('首页') }}
            </a>
            <span class="breadcrumb-separator"><i class="fa-solid fa-chevron-right"></i></span>
            <a :href="`/${school.type}`" class="breadcrumb-link" @click.prevent="handleBreadcrumbClick(school.type)">
              {{ school.type === 'secondary' ? convertIfNeeded('中学') : convertIfNeeded('小学') }}
            </a>
            <span class="breadcrumb-separator"><i class="fa-solid fa-chevron-right"></i></span>
            <span class="breadcrumb-current">{{ displayName }}</span>
          </nav>

          <div class="header-content">
            <div class="header-info">
              <!-- School Name -->
              <div class="school-title-row">
                <h1 class="school-name">{{ displayName }}</h1>
                <div class="school-logo-placeholder" :title="convertIfNeeded('学校')">
                  <i class="fa-solid fa-school"></i>
                </div>
              </div>

              <!-- English Name & Founded Year -->
              <p v-if="school.nameEnglish" class="school-english-name">
                {{ school.nameEnglish }}
                <span v-if="school.foundedYear" class="founded-year">EST. {{ school.foundedYear }}</span>
              </p>

              <!-- Tags -->
              <div class="header-tags">
                <!-- Banding (中学) -->
                <span v-if="school.type === 'secondary' && school.schoolGroup" class="tag tag-yellow">
                  <i class="fa-solid fa-trophy"></i> {{ school.schoolGroup.replace('BAND', 'Band').trim() }}
                </span>
                <!-- District -->
                <span class="tag tag-glass">
                  <i class="fa-solid fa-map-pin"></i> {{ convertIfNeeded(school.district) }}
                </span>
                <!-- Category -->
                <span class="tag tag-glass">
                  <i class="fa-solid fa-sack-dollar"></i> {{ getCategoryLabel(school.category) }}
                </span>
                <!-- Gender -->
                <span class="tag tag-glass">
                  <i :class="getGenderIcon(school.gender)"></i> {{ getGenderLabel(school.gender) }}
                </span>
                <!-- Religion -->
                <span v-if="school.religion" class="tag tag-glass">
                  <i class="fa-solid fa-hands-praying"></i> {{ convertIfNeeded(school.religion) }}
                </span>
              </div>
            </div>

            <!-- Action Buttons (PC) -->
            <div class="header-actions">
              <button class="action-btn action-btn-glass" @click="handleFavorite">
                <i class="fa-regular fa-star"></i>
                <span>{{ convertIfNeeded('收藏学校') }}</span>
              </button>
              <button class="action-btn action-btn-primary" @click="handleContact">
                <i class="fa-solid fa-paper-plane"></i>
                <span>{{ convertIfNeeded('联系学校') }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="main-container">
        <div class="content-grid">
          <!-- Left Column: Info & Stats -->
          <div class="left-column">
            <!-- Quick Stats (中学 & 小学) -->
            <div v-if="school.foundedYear || school.schoolArea || school.teacherCount" :class="['card', 'quick-stats-card', school.type === 'primary' ? 'primary-quick-stats' : 'secondary-quick-stats']">
              <div class="quick-stats-row">
                <div v-if="school.foundedYear" class="quick-stat-item">
                  <div class="quick-stat-icon"><i class="fa-regular fa-calendar"></i></div>
                  <div class="quick-stat-value">{{ school.foundedYear }}{{ convertIfNeeded('年') }}</div>
                  <div class="quick-stat-label">{{ convertIfNeeded('创校') }}</div>
                </div>
                <div v-if="school.schoolArea" class="quick-stat-item">
                  <div class="quick-stat-icon"><i class="fa-solid fa-ruler-combined"></i></div>
                  <div class="quick-stat-value">{{ school.schoolArea }}</div>
                  <div class="quick-stat-label">{{ convertIfNeeded('占地') }}</div>
                </div>
              </div>
            </div>

            <!-- Teachers Stats (中学 & 小学) -->
            <div v-if="school.teacherCount || school.teacherInfo" :class="['card', school.type === 'primary' ? 'primary-teacher-stats' : 'secondary-teacher-stats']">
              <h3 class="section-title">
                <div class="section-icon section-icon-blue">
                  <i class="fa-solid fa-chalkboard-user"></i>
                </div>
                {{ convertIfNeeded('师资概况') }}
              </h3>

              <!-- Teacher Count Highlight -->
              <div v-if="school.teacherCount" class="teacher-count-box">
                <span class="teacher-count-number">{{ school.teacherCount }}</span>
                <div class="teacher-count-info">
                  <span class="teacher-count-label">{{ convertIfNeeded('教师总数') }}</span>
                </div>
              </div>

              <!-- Progress Bars -->
              <div v-if="school.teacherInfo" class="progress-list">
                <div v-if="school.teacherInfo.bachelor_rate" class="progress-item">
                  <div class="progress-header">
                    <span class="progress-label">
                      <span class="progress-dot bg-blue"></span> {{ convertIfNeeded('学士学位') }}
                    </span>
                    <span class="progress-value">{{ school.teacherInfo.bachelor_rate }}%</span>
                  </div>
                  <div class="progress-bar">
                    <div class="progress-fill bg-blue" :style="{ width: school.teacherInfo.bachelor_rate + '%' }"></div>
                  </div>
                </div>
                <div v-if="school.teacherInfo.master_phd_rate" class="progress-item">
                  <div class="progress-header">
                    <span class="progress-label">
                      <span class="progress-dot bg-purple"></span> {{ convertIfNeeded('硕士/博士') }}
                    </span>
                    <span class="progress-value">{{ school.teacherInfo.master_phd_rate }}%</span>
                  </div>
                  <div class="progress-bar">
                    <div class="progress-fill bg-purple" :style="{ width: school.teacherInfo.master_phd_rate + '%' }"></div>
                  </div>
                </div>
                <div v-if="school.teacherInfo.special_education_rate" class="progress-item">
                  <div class="progress-header">
                    <span class="progress-label">
                      <span class="progress-dot bg-green"></span> {{ convertIfNeeded('特殊培训') }}
                    </span>
                    <span class="progress-value">{{ school.teacherInfo.special_education_rate }}%</span>
                  </div>
                  <div class="progress-bar">
                    <div class="progress-fill bg-green" :style="{ width: school.teacherInfo.special_education_rate + '%' }"></div>
                  </div>
                </div>
              </div>

              <!-- Experience Distribution -->
              <div v-if="school.teacherInfo && (school.teacherInfo.experience_0_4_years || school.teacherInfo.experience_5_9_years || school.teacherInfo.experience_10_plus_years)" class="experience-section">
                <div class="experience-header">
                  <h4>{{ convertIfNeeded('年资分布') }}</h4>
                  <i class="fa-solid fa-chart-pie"></i>
                </div>
                <div class="experience-grid">
                  <div v-if="school.teacherInfo.experience_0_4_years" class="experience-item experience-item-primary">
                    <div class="experience-value">{{ school.teacherInfo.experience_0_4_years }}%</div>
                    <div class="experience-label">0-4{{ convertIfNeeded('年') }}</div>
                  </div>
                  <div v-if="school.teacherInfo.experience_5_9_years" class="experience-item">
                    <div class="experience-value">{{ school.teacherInfo.experience_5_9_years }}%</div>
                    <div class="experience-label">5-9{{ convertIfNeeded('年') }}</div>
                  </div>
                  <div v-if="school.teacherInfo.experience_10_plus_years" class="experience-item">
                    <div class="experience-value">{{ school.teacherInfo.experience_10_plus_years }}%</div>
                    <div class="experience-label">10{{ convertIfNeeded('年以上') }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Admission Info -->
            <div v-if="school.admissionInfo" class="card secondary-admission">
              <h3 class="section-title">
                <div class="section-icon section-icon-orange">
                  <i class="fa-solid fa-file-signature"></i>
                </div>
                {{ convertIfNeeded('收生标准') }}
              </h3>
              <div class="admission-notice">
                <i class="fa-solid fa-circle-exclamation"></i>
                <span>{{ convertIfNeeded(school.admissionInfo) }}</span>
              </div>
            </div>

            <!-- Contact Card -->
            <div v-if="school.contact" :class="['card', school.type === 'primary' ? 'primary-contact' : 'secondary-contact']">
              <h3 class="section-title">
                <div class="section-icon section-icon-gray">
                  <i class="fa-regular fa-address-card"></i>
                </div>
                {{ convertIfNeeded('联络资讯') }}
              </h3>
              <ul class="contact-list">
                <li v-if="school.contact.address" class="contact-item">
                  <div class="contact-icon">
                    <i class="fa-solid fa-location-dot"></i>
                  </div>
                  <span>{{ convertIfNeeded(school.contact.address) }}</span>
                </li>
                <li v-if="school.contact.phone" class="contact-item">
                  <div class="contact-icon contact-icon-green">
                    <i class="fa-solid fa-phone"></i>
                  </div>
                  <span class="contact-phone">{{ school.contact.phone }}</span>
                </li>
                <li v-if="school.contact.email" class="contact-item">
                  <div class="contact-icon contact-icon-purple">
                    <i class="fa-solid fa-envelope"></i>
                  </div>
                  <a :href="`mailto:${school.contact.email}`" class="contact-link">{{ school.contact.email }}</a>
                </li>
                <li v-if="school.contact.website" class="contact-item">
                  <div class="contact-icon contact-icon-blue">
                    <i class="fa-solid fa-globe"></i>
                  </div>
                  <a :href="school.contact.website" target="_blank" rel="noopener noreferrer" class="contact-link">
                    {{ school.contact.website }}
                  </a>
                </li>
              </ul>
            </div>
          </div>

          <!-- Right Column: Details -->
          <div class="right-column">
            <!-- Basic Info (中学) - 放在顶部 -->
            <section v-if="school.type === 'secondary'" class="card secondary-basic-info">
              <h3 class="section-title">
                <div class="section-icon section-icon-blue">
                  <i class="fa-solid fa-info-circle"></i>
                </div>
                {{ convertIfNeeded('基本信息') }}
              </h3>
              <div class="basic-info-grid">
                <div class="info-item">
                  <label>{{ convertIfNeeded('学校规模') }}</label>
                  <div>{{ school.totalClasses || school.schoolScale?.classes || '-' }}{{ convertIfNeeded('班') }}</div>
                </div>              
                <div class="info-item">
                  <label>{{ convertIfNeeded('学费') }}</label>
                  <div>{{ formatTuition(school.tuition) }}</div>
                </div>                  
                <div class="info-item info-item-with-popup">
                  <label>
                    {{ convertIfNeeded('教学语言') }}
                    <span class="info-icon" @click.stop="showLanguageInfo = !showLanguageInfo">
                      <i class="fa-solid fa-circle-info"></i>
                    </span>
                  </label>
                  <div>{{ convertIfNeeded(teachingLanguageText) }}</div>
                  <!-- 教学语言说明弹窗 -->
                  <div v-if="showLanguageInfo" class="language-info-popup" @click.stop>
                    <div class="popup-header">
                      <span>{{ convertIfNeeded('教学语言分类标准') }}</span>
                      <button class="popup-close" @click="showLanguageInfo = false">
                        <i class="fa-solid fa-xmark"></i>
                      </button>
                    </div>
                    <div class="popup-content">
                      <table class="language-table">
                        <thead>
                          <tr>
                            <th>{{ convertIfNeeded('分类') }}</th>
                            <th>{{ convertIfNeeded('英文授课占比') }}</th>
                            <th>{{ convertIfNeeded('说明') }}</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td class="category">{{ convertIfNeeded('英文') }}</td>
                            <td class="ratio">≥ 80%</td>
                            <td class="desc">{{ convertIfNeeded('绝大部分科目使用英文授课') }}</td>
                          </tr>
                          <tr>
                            <td class="category">{{ convertIfNeeded('主要英文') }}</td>
                            <td class="ratio">60% - 79%</td>
                            <td class="desc">{{ convertIfNeeded('多数科目使用英文授课') }}</td>
                          </tr>
                          <tr class="highlight">
                            <td class="category">{{ convertIfNeeded('中英文并重') }}</td>
                            <td class="ratio">40% - 59%</td>
                            <td class="desc">{{ convertIfNeeded('中英文授课科目数量接近') }}</td>
                          </tr>
                          <tr>
                            <td class="category">{{ convertIfNeeded('主要中文') }}</td>
                            <td class="ratio">20% - 39%</td>
                            <td class="desc">{{ convertIfNeeded('多数科目使用中文授课') }}</td>
                          </tr>
                          <tr>
                            <td class="category">{{ convertIfNeeded('中文') }}</td>
                            <td class="ratio">&lt; 20%</td>
                            <td class="desc">{{ convertIfNeeded('绝大部分科目使用中文授课') }}</td>
                          </tr>
                        </tbody>
                      </table>
                      <div class="popup-note">
                        {{ convertIfNeeded('注：基于中四至中六 DSE 科目统计') }}
                      </div>
                    </div>
                  </div>
                </div>
                <div class="info-item">
                  <label>{{ convertIfNeeded('课程类型') }}</label>
                  <div>{{ curriculumTypesText }}</div>
                </div>
                <div v-if="school.schoolSponsor" class="info-item">
                  <label>{{ convertIfNeeded('办学团体') }}</label>
                  <div>{{ convertIfNeeded(school.schoolSponsor) }}</div>
                </div>                
                <div v-if="school.schoolMotto" class="info-item">
                  <label>{{ convertIfNeeded('校训') }}</label>
                  <div>{{ convertIfNeeded(school.schoolMotto) }}</div>
                </div>
              </div>
            </section>

            <!-- Application Cards (中学) -->
            <div v-if="school.type === 'secondary' && school.transferInfo && (hasValidS1Info(school.transferInfo.S1) || hasValidTransferInfo(school.transferInfo.插班))" class="card application-cards-container secondary-application">
              <h3 class="section-title section-title-standalone">
                <div class="section-icon section-icon-green">
                  <i class="fa-solid fa-calendar-check"></i>
                </div>
                {{ convertIfNeeded('入学申请') }}
              </h3>
              <div class="application-cards">
                <!-- S1 Application Card -->
                <div 
                  v-if="hasValidS1Info(school.transferInfo.S1)"
                  :class="['application-card', getCardStatus(school.transferInfo.S1)]"
                >
                  <div class="card-status-badge" :class="isCardOpen(school.transferInfo.S1) ? 'badge-open' : 'badge-closed'">
                    <i :class="isCardOpen(school.transferInfo.S1) ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-xmark'"></i>
                    {{ isCardOpen(school.transferInfo.S1) ? 'OPEN' : 'CLOSED' }}
                  </div>
                  <div class="card-content">
                    <div class="card-grade">
                      <i class="fa-solid fa-graduation-cap"></i>
                      {{ convertIfNeeded('中一申请') }}
                    </div>
                    <div class="card-period">
                      <i class="fa-regular fa-clock"></i>
                      {{ formatDateRange(school.transferInfo.S1.入学申请开始时间, school.transferInfo.S1.入学申请截至时间) }}
                    </div>
                    <a 
                      v-if="school.transferInfo.S1.申请详情地址"
                      :href="school.transferInfo.S1.申请详情地址"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="card-link"
                      @click.stop
                    >
                      <i class="fa-solid fa-arrow-up-right-from-square"></i>
                      {{ convertIfNeeded('查看详情') }}
                    </a>
                  </div>
                </div>

                <!-- Transfer Application Card -->
                <div 
                  v-if="school.transferInfo.插班 && hasValidTransferInfo(school.transferInfo.插班)"
                  :class="['application-card', getCardStatus(school.transferInfo.插班, true)]"
                >
                  <div class="card-status-badge" :class="isCardOpen(school.transferInfo.插班, true) ? 'badge-open' : 'badge-closed'">
                    <i :class="isCardOpen(school.transferInfo.插班, true) ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-xmark'"></i>
                    {{ isCardOpen(school.transferInfo.插班, true) ? 'OPEN' : 'CLOSED' }}
                  </div>
                  <div class="card-content">
                    <div class="card-grade">
                      <i class="fa-solid fa-user-plus"></i>
                      {{ convertIfNeeded('插班申请') }}
                    </div>
                    <div class="card-period">
                      <i class="fa-regular fa-clock"></i>
                      {{ formatTransferDateRange() }}
                    </div>
                    <a 
                      v-if="getTransferDetailLink()"
                      :href="getTransferDetailLink()"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="card-link"
                      @click.stop
                    >
                      <i class="fa-solid fa-arrow-up-right-from-square"></i>
                      {{ convertIfNeeded('查看详情') }}
                    </a>
                  </div>
                </div>
              </div>
            </div>

            <!-- Basic Info (小学) - 放在顶部 -->
            <section v-if="school.type === 'primary'" class="card primary-basic-info">
              <h3 class="section-title">
                <div class="section-icon section-icon-blue">
                  <i class="fa-solid fa-info-circle"></i>
                </div>
                {{ convertIfNeeded('基本信息') }}
              </h3>
              <div class="basic-info-grid">
                <div v-if="school.schoolSponsor" class="info-item">
                  <label>{{ convertIfNeeded('辦學團體') }}</label>
                  <div>{{ convertIfNeeded(school.schoolSponsor) }}</div>
                </div>
                <div class="info-item info-item-with-popup">
                  <label>
                    {{ convertIfNeeded('教學語言') }}
                    <span class="info-icon" @click.stop="showLanguageInfo = !showLanguageInfo">
                      <i class="fa-solid fa-circle-info"></i>
                    </span>
                  </label>
                  <div>{{ convertIfNeeded(teachingLanguageText) }}</div>
                  <!-- 教学语言说明弹窗 -->
                  <div v-if="showLanguageInfo" class="language-info-popup" @click.stop>
                    <div class="popup-header">
                      <span>{{ convertIfNeeded('教学语言分类标准') }}</span>
                      <button class="popup-close" @click="showLanguageInfo = false">
                        <i class="fa-solid fa-xmark"></i>
                      </button>
                    </div>
                    <div class="popup-content">
                      <table class="language-table">
                        <thead>
                          <tr>
                            <th>{{ convertIfNeeded('分类') }}</th>
                            <th>{{ convertIfNeeded('英文授课占比') }}</th>
                            <th>{{ convertIfNeeded('说明') }}</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td class="category">{{ convertIfNeeded('英文') }}</td>
                            <td class="ratio">≥ 80%</td>
                            <td class="desc">{{ convertIfNeeded('绝大部分科目使用英文授课') }}</td>
                          </tr>
                          <tr>
                            <td class="category">{{ convertIfNeeded('主要英文') }}</td>
                            <td class="ratio">60% - 79%</td>
                            <td class="desc">{{ convertIfNeeded('多数科目使用英文授课') }}</td>
                          </tr>
                          <tr class="highlight">
                            <td class="category">{{ convertIfNeeded('中英文并重') }}</td>
                            <td class="ratio">40% - 59%</td>
                            <td class="desc">{{ convertIfNeeded('中英文授课科目数量接近') }}</td>
                          </tr>
                          <tr>
                            <td class="category">{{ convertIfNeeded('主要中文') }}</td>
                            <td class="ratio">20% - 39%</td>
                            <td class="desc">{{ convertIfNeeded('多数科目使用中文授课') }}</td>
                          </tr>
                          <tr>
                            <td class="category">{{ convertIfNeeded('中文') }}</td>
                            <td class="ratio">&lt; 20%</td>
                            <td class="desc">{{ convertIfNeeded('绝大部分科目使用中文授课') }}</td>
                          </tr>
                        </tbody>
                      </table>
                      <div class="popup-note">
                        {{ convertIfNeeded('注：基于中四至中六 DSE 科目统计') }}
                      </div>
                    </div>
                  </div>
                </div>
                <div v-if="school.schoolMotto" class="info-item">
                  <label>{{ convertIfNeeded('校訓') }}</label>
                  <div>{{ convertIfNeeded(school.schoolMotto) }}</div>
                </div>
                <div class="info-item">
                  <label>{{ convertIfNeeded('學費') }}</label>
                  <div>{{ formatTuition(school.tuition) }}</div>
                </div>
                <div class="info-item">
                  <label>{{ convertIfNeeded('學校規模') }}</label>
                  <div>{{ school.schoolScale?.classes ?? '-' }}{{ convertIfNeeded('班') }}</div>
                </div>
                <div class="info-item">
                  <label>{{ convertIfNeeded('課程類型') }}</label>
                  <div>{{ curriculumTypesText }}</div>
                </div>
              </div>
            </section>

            <!-- Application Cards (小学) -->
            <div v-if="school.type === 'primary' && school.transferInfo && (hasValidP1Info(school.transferInfo.小一) || hasValidTransferInfo(school.transferInfo.插班))" class="card application-cards-container primary-application">
              <h3 class="section-title section-title-standalone">
                <div class="section-icon section-icon-green">
                  <i class="fa-solid fa-calendar-check"></i>
                </div>
                {{ convertIfNeeded('入学申请') }}
              </h3>
              <div class="application-cards">
                <!-- P1 Application Card -->
                <div 
                  v-if="hasValidP1Info(school.transferInfo.小一)"
                  :class="['application-card', getCardStatusForP1(school.transferInfo.小一)]"
                >
                  <div class="card-status-badge" :class="isCardOpenForP1(school.transferInfo.小一) ? 'badge-open' : 'badge-closed'">
                    <i :class="isCardOpenForP1(school.transferInfo.小一) ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-xmark'"></i>
                    {{ isCardOpenForP1(school.transferInfo.小一) ? 'OPEN' : 'CLOSED' }}
                  </div>
                  <div class="card-content">
                    <div class="card-grade">
                      <i class="fa-solid fa-graduation-cap"></i>
                      {{ convertIfNeeded('小一申请') }}
                    </div>
                    <div class="card-period">
                      <i class="fa-regular fa-clock"></i>
                      {{ formatDateRangeForP1(school.transferInfo.小一.小一入学申请开始时间, school.transferInfo.小一.小一入学申请截止时间) }}
                    </div>
                    <a 
                      v-if="school.transferInfo.小一.小一申请详情"
                      :href="school.transferInfo.小一.小一申请详情"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="card-link"
                      @click.stop
                    >
                      <i class="fa-solid fa-arrow-up-right-from-square"></i>
                      {{ convertIfNeeded('查看详情') }}
                    </a>
                  </div>
                </div>

                <!-- Transfer Application Card (Primary) -->
                <div 
                  v-if="school.transferInfo.插班 && hasValidTransferInfo(school.transferInfo.插班)"
                  :class="['application-card', getCardStatus(school.transferInfo.插班, true)]"
                >
                  <div class="card-status-badge" :class="isCardOpen(school.transferInfo.插班, true) ? 'badge-open' : 'badge-closed'">
                    <i :class="isCardOpen(school.transferInfo.插班, true) ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-xmark'"></i>
                    {{ isCardOpen(school.transferInfo.插班, true) ? 'OPEN' : 'CLOSED' }}
                  </div>
                  <div class="card-content">
                    <div class="card-grade">
                      <i class="fa-solid fa-user-plus"></i>
                      {{ convertIfNeeded('插班申请') }}
                    </div>
                    <div class="card-period">
                      <i class="fa-regular fa-clock"></i>
                      {{ formatTransferDateRange() }}
                    </div>
                    <a 
                      v-if="getTransferDetailLink()"
                      :href="getTransferDetailLink()"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="card-link"
                      @click.stop
                    >
                      <i class="fa-solid fa-arrow-up-right-from-square"></i>
                      {{ convertIfNeeded('查看详情') }}
                    </a>
                  </div>
                </div>
              </div>
            </div>

            <!-- Secondary School Info (小学升中信息) -->
            <section v-if="school.type === 'primary' && (hasSecondaryInfo || hasPromotionInfo)" class="card primary-secondary-info">
              <h3 class="section-title">
                <div class="section-icon section-icon-orange">
                  <i class="fa-solid fa-arrow-up-right-dots"></i>
                </div>
                {{ convertIfNeeded('升中资讯') }}
              </h3>

              <!-- Band 1 Rate Summary -->
              <div v-if="school.band1Rate" class="band1-rate-box">
                <div class="band1-rate-label">
                  <i class="fa-solid fa-trophy"></i>
                  {{ convertIfNeeded('最近一年升Band 1比例') }}
                </div>
                <div class="band1-rate-value">{{ school.band1Rate.toFixed(1) }}%</div>
              </div>

              <!-- Linked Schools -->
              <div v-if="hasSecondaryInfo" class="secondary-info-list">
                <div v-if="school.secondaryInfo.through_train || school.secondaryInfo.结龙" class="secondary-info-item secondary-info-through">
                  <div class="secondary-info-badge badge-through">
                    <i class="fa-solid fa-link"></i>
                    {{ convertIfNeeded('一条龙中学') }}
                  </div>
                  <div class="secondary-info-content">
                    {{ convertIfNeeded(school.secondaryInfo.through_train || school.secondaryInfo.结龙) }}
                  </div>
                </div>
                <div v-if="school.secondaryInfo.direct || school.secondaryInfo.直属" class="secondary-info-item secondary-info-direct">
                  <div class="secondary-info-badge badge-direct">
                    <i class="fa-solid fa-building"></i>
                    {{ convertIfNeeded('直属中学') }}
                  </div>
                  <div class="secondary-info-content">
                    {{ convertIfNeeded(school.secondaryInfo.direct || school.secondaryInfo.直属) }}
                  </div>
                </div>
                <div v-if="school.secondaryInfo.associated || school.secondaryInfo.联系" class="secondary-info-item secondary-info-associated">
                  <div class="secondary-info-badge badge-associated">
                    <i class="fa-solid fa-handshake"></i>
                    {{ convertIfNeeded('联系中学') }}
                  </div>
                  <div class="secondary-info-content">
                    {{ convertIfNeeded(school.secondaryInfo.associated || school.secondaryInfo.联系) }}
                  </div>
                </div>
              </div>

              <!-- Yearly Promotion Stats -->
              <div v-if="hasPromotionInfo && school.promotionInfo.yearly_stats" class="promotion-yearly-stats">
                <h4 class="promotion-subtitle">
                  <i class="fa-solid fa-chart-line"></i>
                  {{ convertIfNeeded('历年升中数据') }}
                </h4>
                <div class="yearly-stats-container">
                  <div v-for="yearData in getSortedYearlyStats()" :key="yearData.year" class="yearly-stat-card">
                    <div class="yearly-stat-header">
                      <span class="yearly-stat-year">{{ yearData.year }}{{ convertIfNeeded('年') }}</span>
                      <span class="yearly-stat-rate" :class="getBandRateClass(yearData.rate)">
                        {{ yearData.rate?.toFixed(1) || '0' }}%
                      </span>
                    </div>
                    <div class="yearly-stat-summary">
                      <span v-if="yearData.total">{{ convertIfNeeded('毕业生') }}: {{ yearData.total }}{{ convertIfNeeded('人') }}</span>
                      <span v-if="yearData.band1"> | Band 1: {{ yearData.band1 }}{{ convertIfNeeded('人') }}</span>
                    </div>
                    <!-- Schools List -->
                    <div v-if="yearData.schools && Object.keys(yearData.schools).length > 0" class="yearly-schools-list">
                      <div 
                        v-for="(schoolInfo, schoolName) in getDisplaySchools(yearData.schools, yearData.year)" 
                        :key="schoolName" 
                        class="yearly-school-item"
                      >
                        <span class="school-name-text">{{ convertIfNeeded(schoolName as string) }}</span>
                        <span class="school-band-badge" :class="getBandBadgeClass(schoolInfo.band || schoolInfo)">
                          {{ formatBand(schoolInfo.band || schoolInfo) }}
                        </span>
                        <span class="school-count">{{ formatStudentCount(schoolInfo.count || schoolInfo) }}</span>
                      </div>
                      <!-- Show More/Less Button -->
                      <button 
                        v-if="Object.keys(yearData.schools).length > 5"
                        class="show-more-btn"
                        @click="toggleYearExpand(yearData.year)"
                      >
                        <i :class="expandedYears[yearData.year] ? 'fa-solid fa-chevron-up' : 'fa-solid fa-chevron-down'"></i>
                        {{ expandedYears[yearData.year] ? convertIfNeeded('收起') : convertIfNeeded('展示全部') + ' (' + Object.keys(yearData.schools).length + ')' }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <!-- Class Structure -->
            <div v-if="school.type === 'secondary' && school.classesByGrade" class="card secondary-class-structure">
              <h3 class="section-title">
                <div class="section-icon section-icon-blue">
                  <i class="fa-solid fa-layer-group"></i>
                </div>
                {{ convertIfNeeded('班级结构') }}
              </h3>
              <!-- 教学模式突出显示 -->
              <div v-if="school.classTeachingMode" class="class-teaching-mode-highlight">
                <div class="teaching-mode-icon">
                  <i class="fa-solid fa-chalkboard-user"></i>
                </div>
                <div class="teaching-mode-content">
                  <div class="teaching-mode-label">{{ convertIfNeeded('教学模式') }}</div>
                  <div class="teaching-mode-text">{{ convertIfNeeded(school.classTeachingMode) }}</div>
                </div>
              </div>
              <!-- 班级人数精简显示 -->
              <div class="class-grid-container class-grid-compact">
                <div class="class-grid class-grid-primary">
                  <div class="class-grid-header">
                    <div class="class-grid-label">{{ convertIfNeeded('中一') }}</div>
                    <div class="class-grid-label">{{ convertIfNeeded('中二') }}</div>
                    <div class="class-grid-label">{{ convertIfNeeded('中三') }}</div>
                    <div class="class-grid-label">{{ convertIfNeeded('中四') }}</div>
                    <div class="class-grid-label">{{ convertIfNeeded('中五') }}</div>
                    <div class="class-grid-label">{{ convertIfNeeded('中六') }}</div>
                  </div>
                  <div class="class-grid-values">
                    <div class="class-grid-value">{{ school.classesByGrade.S1 ?? '-' }}</div>
                    <div class="class-grid-value">{{ school.classesByGrade.S2 ?? '-' }}</div>
                    <div class="class-grid-value">{{ school.classesByGrade.S3 ?? '-' }}</div>
                    <div class="class-grid-value">{{ school.classesByGrade.S4 ?? '-' }}</div>
                    <div class="class-grid-value">{{ school.classesByGrade.S5 ?? '-' }}</div>
                    <div class="class-grid-value">{{ school.classesByGrade.S6 ?? '-' }}</div>
                  </div>
                </div>
              </div>

              <div v-if="school.remarks" class="class-remarks">
                <i class="fa-solid fa-circle-info"></i>
                <p>{{ convertIfNeeded(school.remarks) }}</p>
              </div>
            </div>

            <!-- Curriculum -->
            <div v-if="school.type === 'secondary' && school.curriculumByLanguage" class="card secondary-curriculum">
              <h3 class="section-title">
                <div class="section-icon section-icon-purple">
                  <i class="fa-solid fa-book-open"></i>
                </div>
                {{ convertIfNeeded('开设科目') }}
              </h3>

              <div class="curriculum-grid">
                <!-- Junior Section -->
                <div v-if="school.curriculumByLanguage.junior" class="curriculum-section curriculum-section-junior">
                  <div class="curriculum-header">
                    <div class="curriculum-header-left">
                      <span class="curriculum-dot curriculum-dot-blue"></span>
                      {{ convertIfNeeded('初中课程') }}
                    </div>
                    <span class="curriculum-note">中一至中三</span>
                  </div>
                  <div class="curriculum-body">
                    <div v-if="school.curriculumByLanguage.junior.chinese_medium" class="subject-group">
                      <div class="subject-group-label">
                        <i class="fa-solid fa-font"></i> {{ convertIfNeeded('中文教学') }}
                      </div>
                      <div class="subject-tags">
                        <span v-for="subject in parseSubjects(school.curriculumByLanguage.junior.chinese_medium)" :key="subject" class="subject-tag subject-tag-chinese">
                          {{ convertIfNeeded(subject) }}
                        </span>
                      </div>
                    </div>
                    <div v-if="school.curriculumByLanguage.junior.english_medium" class="subject-group">
                      <div class="subject-group-label subject-group-label-english">
                        <i class="fa-solid fa-globe"></i> {{ convertIfNeeded('英文教学') }}
                      </div>
                      <div class="subject-tags">
                        <span v-for="subject in parseSubjects(school.curriculumByLanguage.junior.english_medium)" :key="subject" class="subject-tag subject-tag-english">
                          {{ convertIfNeeded(subject) }}
                        </span>
                      </div>
                    </div>
                    <div v-if="school.curriculumByLanguage.junior.mixed_medium" class="subject-group">
                      <div class="subject-group-label subject-group-label-mixed">
                        <i class="fa-solid fa-language"></i> {{ convertIfNeeded('按班别/组别') }}
                      </div>
                      <div class="subject-tags">
                        <span v-for="subject in parseSubjects(school.curriculumByLanguage.junior.mixed_medium)" :key="subject" class="subject-tag subject-tag-mixed">
                          {{ convertIfNeeded(subject) }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Senior Section -->
                <div v-if="school.curriculumByLanguage.senior" class="curriculum-section curriculum-section-senior">
                  <div class="curriculum-header curriculum-header-senior">
                    <div class="curriculum-header-left">
                      <span class="curriculum-dot curriculum-dot-green"></span>
                      {{ convertIfNeeded('高中课程') }}
                    </div>
                    <span class="curriculum-note">中四至中六</span>
                  </div>
                  <div class="curriculum-body">
                    <div v-if="school.curriculumByLanguage.senior.chinese_medium" class="subject-group">
                      <div class="subject-group-label">
                        <i class="fa-solid fa-font"></i> {{ convertIfNeeded('中文教学') }}
                      </div>
                      <div class="subject-tags">
                        <span v-for="subject in parseSubjects(school.curriculumByLanguage.senior.chinese_medium)" :key="subject" class="subject-tag subject-tag-chinese">
                          {{ convertIfNeeded(subject) }}
                        </span>
                      </div>
                    </div>
                    <div v-if="school.curriculumByLanguage.senior.english_medium" class="subject-group">
                      <div class="subject-group-label subject-group-label-english">
                        <i class="fa-solid fa-globe"></i> {{ convertIfNeeded('英文教学') }}
                      </div>
                      <div class="subject-tags">
                        <span v-for="subject in parseSubjects(school.curriculumByLanguage.senior.english_medium)" :key="subject" class="subject-tag subject-tag-english">
                          {{ convertIfNeeded(subject) }}
                        </span>
                      </div>
                    </div>
                    <div v-if="school.curriculumByLanguage.senior.mixed_medium" class="subject-group">
                      <div class="subject-group-label subject-group-label-mixed">
                        <i class="fa-solid fa-language"></i> {{ convertIfNeeded('按班别/组别') }}
                      </div>
                      <div class="subject-tags">
                        <span v-for="subject in parseSubjects(school.curriculumByLanguage.senior.mixed_medium)" :key="subject" class="subject-tag subject-tag-mixed">
                          {{ convertIfNeeded(subject) }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Policies Grid -->
            <div v-if="school.type === 'secondary' && (school.languagePolicy || school.diversitySupport)" class="policies-grid secondary-policies">
              <div v-if="school.languagePolicy" class="card policy-card">
                <h3 class="section-title section-title-sm">
                  <div class="section-icon section-icon-indigo">
                    <i class="fa-solid fa-comments"></i>
                  </div>
                  {{ convertIfNeeded('语文政策') }}
                </h3>
                <div class="policy-content">
                  <i class="fa-solid fa-quote-right policy-quote-icon"></i>
                  <p>{{ convertIfNeeded(school.languagePolicy) }}</p>
                </div>
              </div>
              <div v-if="school.diversitySupport" class="card policy-card">
                <h3 class="section-title section-title-sm">
                  <div class="section-icon section-icon-pink">
                    <i class="fa-solid fa-hand-holding-heart"></i>
                  </div>
                  {{ convertIfNeeded('学生支援') }}
                </h3>
                <div class="policy-content">
                  <i class="fa-solid fa-seedling policy-quote-icon policy-quote-icon-green"></i>
                  <p>{{ convertIfNeeded(school.diversitySupport) }}</p>
                </div>
              </div>
            </div>
            <!-- Learning Features -->
            <div v-if="school.type === 'secondary' && (school.careerEducation || school.wholePersonLearning || school.schoolBasedCurriculum || school.teachingStrategy)" class="card secondary-learning">
              <h3 class="section-title">
                <div class="section-icon section-icon-yellow">
                  <i class="fa-solid fa-lightbulb"></i>
                </div>
                {{ convertIfNeeded('学习特色') }}
              </h3>
              <div class="learning-list">
                <div v-if="school.teachingStrategy" class="learning-item">
                  <div class="learning-label">{{ convertIfNeeded('教学策略') }}</div>
                  <div class="learning-text">{{ convertIfNeeded(school.teachingStrategy) }}</div>
                </div>
                <div v-if="school.careerEducation" class="learning-item">
                  <div class="learning-label">{{ convertIfNeeded('生涯规划教育') }}</div>
                  <div class="learning-text">{{ convertIfNeeded(school.careerEducation) }}</div>
                </div>
                <div v-if="school.wholePersonLearning" class="learning-item">
                  <div class="learning-label">{{ convertIfNeeded('全方位学习') }}</div>
                  <div class="learning-text">{{ convertIfNeeded(school.wholePersonLearning) }}</div>
                </div>
                <div v-if="school.schoolBasedCurriculum" class="learning-item">
                  <div class="learning-label">{{ convertIfNeeded('校本课程') }}</div>
                  <div class="learning-text">{{ convertIfNeeded(school.schoolBasedCurriculum) }}</div>
                </div>
              </div>
            </div>
            <!-- Facilities & Transport -->
            <div v-if="school.type === 'secondary' && (school.facilities || school.transportation)" class="card secondary-facilities">
              <h3 class="section-title">
                <div class="section-icon section-icon-green">
                  <i class="fa-solid fa-school"></i>
                </div>
                {{ convertIfNeeded('设施与交通') }}
              </h3>
              <div class="facilities-grid">
                <div v-if="school.facilities" class="facility-item">
                  <span class="facility-label">
                    <i class="fa-solid fa-basketball"></i> {{ convertIfNeeded('主要设施') }}
                  </span>
                  <div class="facility-content">
                    {{ convertIfNeeded(school.facilities) }}
                  </div>
                </div>
                <div v-if="school.transportation" class="facility-item">
                  <span class="facility-label">
                    <i class="fa-solid fa-train-subway"></i> {{ convertIfNeeded('交通资讯') }}
                  </span>
                  <div class="facility-content">
                    {{ convertIfNeeded(school.transportation) }}
                  </div>
                </div>
              </div>
            </div>            
            <!-- Class Structure (小学) -->
            <div v-if="school.type === 'primary' && school.classesByGrade" class="card primary-class-structure">
              <h3 class="section-title">
                <div class="section-icon section-icon-blue">
                  <i class="fa-solid fa-layer-group"></i>
                </div>
                {{ convertIfNeeded('班级结构') }}
              </h3>
              <!-- 教学模式突出显示 -->
              <div v-if="school.classTeachingMode" class="class-teaching-mode-highlight">
                <div class="teaching-mode-icon">
                  <i class="fa-solid fa-chalkboard-user"></i>
                </div>
                <div class="teaching-mode-content">
                  <div class="teaching-mode-label">{{ convertIfNeeded('教学模式') }}</div>
                  <div class="teaching-mode-text">{{ convertIfNeeded(school.classTeachingMode) }}</div>
                </div>
              </div>
              <!-- 班级人数精简显示 -->
              <div class="class-grid-container class-grid-compact">
                <div class="class-grid class-grid-primary">
                  <div class="class-grid-header">
                    <div class="class-grid-label">{{ convertIfNeeded('小一') }}</div>
                    <div class="class-grid-label">{{ convertIfNeeded('小二') }}</div>
                    <div class="class-grid-label">{{ convertIfNeeded('小三') }}</div>
                    <div class="class-grid-label">{{ convertIfNeeded('小四') }}</div>
                    <div class="class-grid-label">{{ convertIfNeeded('小五') }}</div>
                    <div class="class-grid-label">{{ convertIfNeeded('小六') }}</div>
                  </div>
                  <div class="class-grid-values">
                    <div class="class-grid-value">{{ school.classesByGrade.P1 ?? school.classesByGrade.primary_1 ?? '-' }}</div>
                    <div class="class-grid-value">{{ school.classesByGrade.P2 ?? school.classesByGrade.primary_2 ?? '-' }}</div>
                    <div class="class-grid-value">{{ school.classesByGrade.P3 ?? school.classesByGrade.primary_3 ?? '-' }}</div>
                    <div class="class-grid-value">{{ school.classesByGrade.P4 ?? school.classesByGrade.primary_4 ?? '-' }}</div>
                    <div class="class-grid-value">{{ school.classesByGrade.P5 ?? school.classesByGrade.primary_5 ?? '-' }}</div>
                    <div class="class-grid-value">{{ school.classesByGrade.P6 ?? school.classesByGrade.primary_6 ?? '-' }}</div>
                  </div>
                </div>
              </div>
            </div>
            <!-- Learning Features (小学) -->
            <div v-if="school.type === 'primary' && (school.schoolMission || school.wholePersonLearning || school.diversitySupport)" class="card primary-learning">
              <h3 class="section-title">
                <div class="section-icon section-icon-yellow">
                  <i class="fa-solid fa-lightbulb"></i>
                </div>
                {{ convertIfNeeded('学习特色') }}
              </h3>
              <div class="learning-list">
                <div v-if="school.schoolMission" class="learning-item">
                  <div class="learning-label">{{ convertIfNeeded('办学宗旨') }}</div>
                  <div class="learning-text">{{ convertIfNeeded(school.schoolMission) }}</div>
                </div>
                <div v-if="school.wholePersonLearning" class="learning-item">
                  <div class="learning-label">{{ convertIfNeeded('全方位学习') }}</div>
                  <div class="learning-text">{{ convertIfNeeded(school.wholePersonLearning) }}</div>
                </div>
                <div v-if="school.diversitySupport" class="learning-item">
                  <div class="learning-label">{{ convertIfNeeded('照顾学生多样性') }}</div>
                  <div class="learning-text">{{ convertIfNeeded(school.diversitySupport) }}</div>
                </div>
              </div>
            </div>

            <!-- Assessment & Class Arrangement (小学) -->
            <div v-if="school.type === 'primary' && (school.multiAssessment || school.classArrangement || school.lunchArrangement)" class="card primary-policy">
              <h3 class="section-title">
                <div class="section-icon section-icon-purple">
                  <i class="fa-solid fa-clipboard-list"></i>
                </div>
                {{ convertIfNeeded('学校政策') }}
              </h3>
              <div class="learning-list">
                <div v-if="school.multiAssessment" class="learning-item">
                  <div class="learning-label">{{ convertIfNeeded('多元学习评估') }}</div>
                  <div class="learning-text">{{ convertIfNeeded(school.multiAssessment) }}</div>
                </div>
                <div v-if="school.classArrangement" class="learning-item">
                  <div class="learning-label">{{ convertIfNeeded('分班安排') }}</div>
                  <div class="learning-text">{{ convertIfNeeded(school.classArrangement) }}</div>
                </div>
                <div v-if="school.lunchArrangement" class="learning-item">
                  <div class="learning-label">{{ convertIfNeeded('午膳安排') }}</div>
                  <div class="learning-text">{{ convertIfNeeded(school.lunchArrangement) }}</div>
                </div>
              </div>
            </div>
            <!-- Facilities & Transport (小学) -->
            <div v-if="school.type === 'primary' && (school.specialRooms || school.schoolBus || school.nannyBus || school.classroomCount)" class="card primary-facilities">
              <h3 class="section-title">
                <div class="section-icon section-icon-green">
                  <i class="fa-solid fa-school"></i>
                </div>
                {{ convertIfNeeded('设施与交通') }}
              </h3>
              <div class="facilities-stats" v-if="school.classroomCount || school.hallCount || school.playgroundCount || school.libraryCount">
                <div v-if="school.classroomCount" class="facility-stat">
                  <i class="fa-solid fa-chalkboard"></i>
                  <span>{{ convertIfNeeded('课室') }} {{ school.classroomCount }}</span>
                </div>
                <div v-if="school.hallCount" class="facility-stat">
                  <i class="fa-solid fa-building-columns"></i>
                  <span>{{ convertIfNeeded('礼堂') }} {{ school.hallCount }}</span>
                </div>
                <div v-if="school.playgroundCount" class="facility-stat">
                  <i class="fa-solid fa-futbol"></i>
                  <span>{{ convertIfNeeded('操场') }} {{ school.playgroundCount }}</span>
                </div>
                <div v-if="school.libraryCount" class="facility-stat">
                  <i class="fa-solid fa-book"></i>
                  <span>{{ convertIfNeeded('图书馆') }} {{ school.libraryCount }}</span>
                </div>
              </div>
              <div class="facilities-grid">
                <div v-if="school.specialRooms" class="facility-item">
                  <span class="facility-label"><i class="fa-solid fa-door-open"></i> {{ convertIfNeeded('特别室') }}</span>
                  <div class="facility-content">{{ convertIfNeeded(school.specialRooms) }}</div>
                </div>
                <div v-if="school.schoolBus || school.nannyBus" class="facility-item">
                  <span class="facility-label"><i class="fa-solid fa-bus"></i> {{ convertIfNeeded('交通服务') }}</span>
                  <div class="facility-content">
                    <span v-if="school.schoolBus">{{ convertIfNeeded('校车') }}: {{ convertIfNeeded(school.schoolBus) }}</span>
                    <span v-if="school.schoolBus && school.nannyBus"> | </span>
                    <span v-if="school.nannyBus">{{ convertIfNeeded('保姆车') }}: {{ convertIfNeeded(school.nannyBus) }}</span>
                  </div>
                </div>
              </div>
            </div>            
          </div>
        </div>

        <!-- Recommendations Section -->
        <section v-if="recommendations.related.length || recommendations.popular.length" class="recommendations-section">
          <h2 class="recommendations-title">
            <i class="fa-solid fa-compass"></i>
            {{ convertIfNeeded('你可能想浏览') }}
          </h2>
          
          <!-- Related Schools (Same District) -->
          <div v-if="recommendations.related.length" class="recommendation-group">
            <h3 class="recommendation-group-title">
              <i class="fa-solid fa-map-location-dot"></i>
              {{ convertIfNeeded('同区学校推荐') }}
            </h3>
            <div class="recommendation-list">
              <a 
                v-for="recSchool in recommendations.related" 
                :key="recSchool.id" 
                :href="`/school/${recSchool.type}/${recSchool.id}`"
                class="recommendation-card"
                @click.prevent="handleRecommendationClick(recSchool)"
              >
                <div class="rec-card-header">
                  <span class="rec-school-name">{{ convertIfNeeded(recSchool.name) }}</span>
                  <i class="fa-solid fa-arrow-right rec-arrow"></i>
                </div>
                <div class="rec-card-meta">
                  <span class="rec-meta-item">
                    <i class="fa-solid fa-location-dot"></i>
                    {{ convertIfNeeded(recSchool.district) }}
                  </span>
                  <span class="rec-meta-divider">|</span>
                  <span class="rec-meta-item">{{ getCategoryLabel(recSchool.category) }}</span>
                </div>
              </a>
            </div>
          </div>

          <!-- Popular Schools -->
          <div v-if="recommendations.popular.length" class="recommendation-group">
            <h3 class="recommendation-group-title">
              <i class="fa-solid fa-fire"></i>
              {{ convertIfNeeded('热门学校推荐') }}
            </h3>
            <div class="recommendation-list">
              <a 
                v-for="recSchool in recommendations.popular" 
                :key="recSchool.id" 
                :href="`/school/${recSchool.type}/${recSchool.id}`"
                class="recommendation-card recommendation-card-popular"
                @click.prevent="handleRecommendationClick(recSchool)"
              >
                <div class="rec-card-header">
                  <span class="rec-school-name">{{ convertIfNeeded(recSchool.name) }}</span>
                  <i class="fa-solid fa-arrow-right rec-arrow"></i>
                </div>
                <div class="rec-card-meta">
                  <span class="rec-meta-item">
                    <i class="fa-solid fa-location-dot"></i>
                    {{ convertIfNeeded(recSchool.district) }}
                  </span>
                  <span class="rec-meta-divider">|</span>
                  <span v-if="recSchool.band1Rate !== undefined && recSchool.band1Rate !== null" class="rec-meta-item rec-meta-highlight">
                    <i class="fa-solid fa-trophy"></i>
                    Band 1: {{ recSchool.band1Rate.toFixed(0) }}%
                  </span>
                  <span v-else-if="recSchool.schoolGroup" class="rec-meta-item">
                    {{ convertIfNeeded(recSchool.schoolGroup) }}
                  </span>
                  <span v-else class="rec-meta-item rec-meta-highlight">
                    <i class="fa-solid fa-star"></i>
                    {{ convertIfNeeded('热门') }}
                  </span>
                </div>
              </a>
            </div>
          </div>
        </section>
      </div>

      <!-- Mobile Bottom Action Bar -->
      <div class="mobile-action-bar">
        <div class="mobile-action-left">
          <button class="mobile-action-icon" @click="handleFavorite">
            <i class="fa-regular fa-heart"></i>
            <span>{{ convertIfNeeded('收藏') }}</span>
          </button>
          <button class="mobile-action-icon" @click="handleShare">
            <i class="fa-solid fa-arrow-up-from-bracket"></i>
            <span>{{ convertIfNeeded('分享') }}</span>
          </button>
        </div>
        <button class="mobile-action-primary" @click="handleContact">
          <i class="fa-regular fa-paper-plane"></i> {{ convertIfNeeded('联络学校') }}
        </button>
      </div>

      <!-- Toast Message -->
      <div v-if="showToast" class="toast-message">
        {{ toastMessage }}
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSchoolStore } from '@/stores/school'
import type { School } from '@/types/school'
import { formatTuition } from '@/utils/formatter'
import { useLanguageStore } from '@/stores/language'
import { isCardOpen, parseDate, formatDateRange } from '@/utils/applicationStatus'

const route = useRoute()
const router = useRouter()
const schoolStore = useSchoolStore()
const languageStore = useLanguageStore()

const school = ref<School | null>(null)
const loading = ref(true)
const showToast = ref(false)
const toastMessage = ref('')
const recommendations = ref<{ related: School[], popular: School[] }>({ related: [], popular: [] })
const showLanguageInfo = ref(false)

// 教学语言文本计算
const teachingLanguageText = computed(() => school.value ? convertIfNeeded(school.value.teachingLanguage || '中英文并重') : '')

// 课程类型文本计算
const curriculumTypesText = computed(() => {
  if (!school.value) return 'DSE'
  const sc = (school.value as any).schoolCurriculum
  if (!sc) return 'DSE'
  try {
    const data = typeof sc === 'string' ? JSON.parse(sc) : sc
    const types = data && data['课程体系']
    if (Array.isArray(types) && types.length) return types.map((t: string) => convertIfNeeded(t)).join(' + ')
    if (typeof types === 'string' && types.trim()) return convertIfNeeded(types)
  } catch (_) {}
  return 'DSE'
})

// Load recommendations
const loadRecommendations = async () => {
  if (!school.value) return
  try {
    const data = await schoolStore.fetchSchoolRecommendations(school.value.id, school.value.type as any)
    recommendations.value = data
  } catch (error) {
    console.error('获取推荐失败:', error)
  }
}

// Handle recommendation click - use window.location for SEO
const handleRecommendationClick = (recSchool: School) => {
  window.location.href = `/school/${recSchool.type}/${recSchool.id}`
}

// Fetch school detail
const fetchDetail = async () => {
  const { type, id } = route.params
  if (!type || !id) return

  loading.value = true
  try {
    school.value = await schoolStore.fetchSchoolDetail(Number(id), type as any)
    console.log('school:', school.value)
    if (school.value?.type) {
      sessionStorage.setItem('lastSchoolType', school.value.type)
    }
    
    if (school.value) {
      const name = convertIfNeeded(school.value.name)
      document.title = `${name} - BetterSchool`
    }
    
    // Load recommendations after school data is loaded
    await loadRecommendations()
  } catch (error) {
    console.error('获取学校详情失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDetail()
})

watch(() => route.params, () => {
  fetchDetail()
})

// Language conversion
const currentLanguage = computed(() => languageStore.currentLanguage)

const convertIfNeeded = (text?: string | null): string => {
  const val = text || ''
  if (!val) return ''
  return languageStore.convertText(val)
}

const displayName = computed(() => {
  if (!school.value) return ''
  if (currentLanguage.value === 'zh-TW' && school.value.nameTraditional) {
    return school.value.nameTraditional
  }
  return convertIfNeeded(school.value.name)
})

// Helper functions
const getCategoryLabel = (category: string) => {
  const labels: Record<string, string> = {
    elite: '名校联盟',
    traditional: '传统名校',
    direct: '直资',
    government: '官立',
    private: '私立',
    aided: '资助'
  }
  return convertIfNeeded(labels[category] || category)
}

const getGenderLabel = (gender: string) => {
  const labels: Record<string, string> = {
    coed: '男女校',
    boys: '男校',
    girls: '女校'
  }
  return convertIfNeeded(labels[gender] || gender)
}

const getGenderIcon = (gender: string) => {
  const icons: Record<string, string> = {
    coed: 'fa-solid fa-venus-mars',
    boys: 'fa-solid fa-mars',
    girls: 'fa-solid fa-venus'
  }
  return icons[gender] || 'fa-solid fa-venus-mars'
}

const parseSubjects = (subjectStr?: string): string[] => {
  if (!subjectStr) return []
  return subjectStr.split(/[,、;，；]/).map(s => s.trim()).filter(s => s)
}

// Application status helpers
const hasValidS1Info = (s1: any): boolean => {
  if (!s1) return false
  return !!(s1.入学申请开始时间 || s1.申请详情地址)
}

const hasValidP1Info = (p1: any): boolean => {
  if (!p1) return false
  return !!(p1.小一入学申请开始时间 || p1.小一申请详情地址)
}

const hasValidTransferInfo = (transfer: any): boolean => {
  if (!transfer) return false
  const hasTime1 = transfer.插班申请开始时间1
  const hasTime2 = transfer.插班申请开始时间2
  const hasLink = transfer.插班详情链接 || transfer.插班申请详情链接
  return !!(hasTime1 || hasTime2 || hasLink)
}

const getCardStatus = (info: any, isTransfer = false): string => {
  return isCardOpen(info, isTransfer) ? 'card-open' : 'card-closed'
}

const getTransferDetailLink = (): string | undefined => {
  const transfer = school.value?.transferInfo?.插班
  if (!transfer) return undefined
  return transfer.插班申请详情链接 || transfer.插班详情链接
}

const formatTransferDateRange = (): string => {
  const transfer = school.value?.transferInfo?.插班
  if (!transfer) return '-'
  
  let display = ""
  
  if (transfer.插班申请开始时间1) {
    const start1 = transfer.插班申请开始时间1
    const end1 = transfer.插班申请截止时间1
    const grade = transfer.可插班年级1 || ''
    
    let timeDisplay = ''
    if (end1) {
      const start1Date = parseDate(start1)
      if (!start1Date && (start1.includes('开放') || start1.includes('申请'))) {
        const end1Date = parseDate(end1)
        if (end1Date) {
          timeDisplay = `截止 ${end1Date.getFullYear()}.${end1Date.getMonth() + 1}.${end1Date.getDate()}`
        } else {
          timeDisplay = start1
        }
      } else {
        timeDisplay = formatDateRange(start1, end1)
      }
    } else {
      timeDisplay = start1
    }
    
    display = grade ? `${grade}: ${timeDisplay}` : timeDisplay
  }
  
  if (transfer.插班申请开始时间2) {
    const start2 = transfer.插班申请开始时间2
    const end2 = transfer.插班申请截止时间2
    const grade2 = transfer.可插班年级2 || ''
    
    let timeDisplay2 = ''
    if (end2) {
      timeDisplay2 = formatDateRange(start2, end2)
    } else {
      timeDisplay2 = start2
    }
    
    const part2 = grade2 ? `${grade2}: ${timeDisplay2}` : timeDisplay2
    display = display ? `${display} | ${part2}` : part2
  }
  
  return display || '-'
}

const isCardOpenForP1 = (p1Info: any): boolean => {
  if (!p1Info) return false
  
  const now = new Date()
  const start = p1Info.小一入学申请开始时间 ? parseDate(p1Info.小一入学申请开始时间) : null
  const end = p1Info.小一入学申请截至时间 ? parseDate(p1Info.小一入学申请截至时间) : null
  
  if (start && end && now >= start && now <= end) return true
  return false
}

const getCardStatusForP1 = (p1Info: any): string => {
  return isCardOpenForP1(p1Info) ? 'card-open' : 'card-closed'
}

const formatDateRangeForP1 = (start?: string, end?: string): string => {
  if (!start || !end) return '-'
  const formatDate = (dateStr: string): string => {
    const date = parseDate(dateStr)
    if (!date) return dateStr
    return `${date.getFullYear()}.${date.getMonth() + 1}.${date.getDate()}`
  }
  return `${formatDate(start)}-${formatDate(end)}`
}

// Promotion Info helpers
const hasSecondaryInfo = computed(() => {
  const info = school.value?.secondaryInfo
  if (!info) return false
  return !!(info.through_train || info.direct || info.associated || info.结龙 || info.直属 || info.联系)
})

const hasPromotionInfo = computed(() => {
  const info = school.value?.promotionInfo
  if (!info) return false
  return !!(info.yearly_stats && Object.keys(info.yearly_stats).length > 0)
})

// 展开/收起状态
const expandedYears = ref<Record<string, boolean>>({})

const toggleYearExpand = (year: string) => {
  expandedYears.value[year] = !expandedYears.value[year]
}

const getSortedYearlyStats = (): Array<{ year: string; rate?: number; total?: number; band1?: number; schools?: Record<string, any> }> => {
  const stats = school.value?.promotionInfo?.yearly_stats
  if (!stats) return []
  // Sort by year descending (从大到小，最新年份在前)
  // 返回数组以保持排序顺序（Object 的数字键会自动按升序排列）
  return Object.entries(stats)
    .sort(([a], [b]) => Number(b) - Number(a))
    .map(([year, data]) => ({ year, ...(data as { rate?: number; total?: number; band1?: number; schools?: Record<string, any> }) }))
}

const getDisplaySchools = (schools: Record<string, any>, year: string) => {
  if (!schools) return {}
  const isExpanded = expandedYears.value[year]
  // Sort by count descending
  const sorted = Object.entries(schools)
    .sort(([, a], [, b]) => {
      const countA = typeof a === 'object' ? (a.count || 0) : (typeof a === 'number' ? a : 0)
      const countB = typeof b === 'object' ? (b.count || 0) : (typeof b === 'number' ? b : 0)
      return countB - countA
    })
  // 如果展开则显示全部，否则只显示前5个
  const limited = isExpanded ? sorted : sorted.slice(0, 5)
  return Object.fromEntries(limited)
}

const getBandRateClass = (rate?: number): string => {
  if (!rate) return ''
  if (rate >= 70) return 'rate-excellent'
  if (rate >= 50) return 'rate-good'
  if (rate >= 30) return 'rate-average'
  return 'rate-low'
}

const getTopSchools = (schools: Record<string, any>, limit: number) => {
  if (!schools) return {}
  // Sort by count descending and take top N
  const sorted = Object.entries(schools)
    .sort(([, a], [, b]) => {
      const countA = typeof a === 'object' ? (a.count || 0) : (typeof a === 'number' ? a : 0)
      const countB = typeof b === 'object' ? (b.count || 0) : (typeof b === 'number' ? b : 0)
      return countB - countA
    })
    .slice(0, limit)
  return Object.fromEntries(sorted)
}

const getBandBadgeClass = (band: any): string => {
  if (!band) return 'band-unknown'
  const bandStr = String(band).toUpperCase()
  if (bandStr.includes('1A')) return 'band-1a'
  if (bandStr.includes('1B')) return 'band-1b'
  if (bandStr.includes('1C') || bandStr.includes('1')) return 'band-1c'
  if (bandStr.includes('2')) return 'band-2'
  if (bandStr.includes('3')) return 'band-3'
  return 'band-unknown'
}

const formatBand = (band: any): string => {
  if (!band) return '-'
  if (typeof band === 'number') return String(band)
  const bandStr = String(band)
  // 简化显示
  if (bandStr.includes('1A') || bandStr.includes('1a')) return 'Band 1A'
  if (bandStr.includes('1B') || bandStr.includes('1b')) return 'Band 1B'
  if (bandStr.includes('1C') || bandStr.includes('1c')) return 'Band 1C'
  if (bandStr.includes('1') || bandStr.toLowerCase().includes('band 1')) return 'Band 1'
  if (bandStr.includes('2')) return 'Band 2'
  if (bandStr.includes('3')) return 'Band 3'
  return bandStr.length > 4 ? bandStr.substring(0, 4) : bandStr
}

const formatStudentCount = (count: any): string => {
  if (count === undefined || count === null) return ''
  if (count === '未知') return convertIfNeeded('未知')
  if (typeof count === 'number') return `${count}${convertIfNeeded('人')}`
  return String(count)
}

// Actions
const handleBreadcrumbClick = (schoolType: string) => {
  router.push(`/${schoolType}`)
}

const handleFavorite = () => {
  showToastMessage(convertIfNeeded('收藏功能开发中'))
}

const handleContact = () => {
  if (school.value?.contact?.website) {
    window.open(school.value.contact.website, '_blank')
  } else {
    showToastMessage(convertIfNeeded('暂无联系方式'))
  }
}

const handleShare = async () => {
  const shareData = {
    title: document.title,
    text: `查看${displayName.value}的详细资料`,
    url: window.location.href
  }

  if (navigator.share) {
    try {
      await navigator.share(shareData)
      return
    } catch (err) {
      console.log('Share cancelled')
    }
  }

  try {
    await navigator.clipboard.writeText(window.location.href)
    showToastMessage(convertIfNeeded('链接已复制'))
  } catch (err) {
    showToastMessage(convertIfNeeded('复制失败'))
  }
}

const showToastMessage = (message: string) => {
  toastMessage.value = message
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 2000)
}
</script>

<style scoped>
/* Base Styles */
.school-detail-page {
  min-height: 100vh;
  background-color: #F0F2F5;
  font-family: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Loading & Error States */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  color: #6b7280;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #4A80F0;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-container i {
  font-size: 48px;
  color: #ef4444;
  margin-bottom: 16px;
}

.back-link {
  margin-top: 16px;
  color: #4A80F0;
  text-decoration: none;
}

/* Header Gradient */
.header-gradient {
  background: linear-gradient(135deg, #2b58b5 0%, #4A80F0 100%);
  color: white;
  padding-top: 32px;
  padding-bottom: 96px;
  position: relative;
  overflow: hidden;
}

.header-decoration {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
}

.header-decoration-1 {
  top: -128px;
  right: -128px;
  width: 500px;
  height: 500px;
  background: rgba(255, 255, 255, 0.1);
  filter: blur(48px);
}

.header-decoration-2 {
  bottom: -80px;
  left: -80px;
  width: 400px;
  height: 400px;
  background: rgba(147, 197, 253, 0.1);
  filter: blur(48px);
}

.header-dots {
  position: absolute;
  inset: 0;
  opacity: 0.03;
  background-image: radial-gradient(#ffffff 1px, transparent 1px);
  background-size: 30px 30px;
}

.header-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 16px;
  position: relative;
  z-index: 10;
}

/* Breadcrumb */
.breadcrumb {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: rgba(191, 219, 254, 1);
  margin-bottom: 32px;
}

.breadcrumb-link {
  color: rgba(191, 219, 254, 1);
  text-decoration: none;
  transition: color 0.2s;
}

.breadcrumb-link:hover {
  color: white;
}

.breadcrumb-separator {
  margin: 0 12px;
  opacity: 0.4;
  font-size: 10px;
}

.breadcrumb-current {
  color: white;
  font-weight: 500;
}

/* Header Content */
.header-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

@media (min-width: 768px) {
  .header-content {
    flex-direction: row;
    justify-content: space-between;
    align-items: flex-end;
  }
}

.header-info {
  flex: 1;
}

.school-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.school-name {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 0.025em;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin: 0;
}

@media (min-width: 768px) {
  .school-name {
    font-size: 36px;
  }
}

.school-logo-placeholder {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(12px);
  padding: 6px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  cursor: help;
}

.school-logo-placeholder i {
  font-size: 20px;
}

.school-english-name {
  color: rgba(191, 219, 254, 1);
  font-size: 16px;
  margin-bottom: 24px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.founded-year {
  font-size: 12px;
  background: rgba(30, 64, 175, 0.3);
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid rgba(96, 165, 250, 0.3);
  color: rgba(191, 219, 254, 1);
}

/* Header Tags */
.header-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tag-yellow {
  background-color: #FCC419;
  color: white;
  font-weight: 700;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.tag-yellow i {
  color: #b45309;
}

.tag-glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Header Actions */
.header-actions {
  display: none;
  gap: 12px;
  font-size: 14px;
  font-weight: 500;
}

@media (min-width: 768px) {
  .header-actions {
    display: flex;
  }
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn-glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.action-btn-glass:hover {
  background: rgba(255, 255, 255, 0.2);
}

.action-btn-glass i {
  color: #fde047;
}

.action-btn-primary {
  background: white;
  color: #4A80F0;
  font-weight: 700;
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

.action-btn-primary:hover {
  background: #eff6ff;
}

/* Main Container */
.main-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 16px 96px;
  margin-top: -48px;
  position: relative;
  z-index: 10;
}

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

@media (min-width: 1024px) {
  .content-grid {
    grid-template-columns: 4fr 8fr;
  }
}

.left-column,
.right-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Mobile order for primary school cards */
@media (max-width: 1023px) {
  .content-grid {
    display: flex;
    flex-direction: column;
  }
  
  .left-column,
  .right-column {
    display: contents;
  }
  
  /* 小学卡片移动端顺序 */
  /* 创校时间放在基本信息前，设施与交通放在联络资讯前 */
  .primary-quick-stats { order: 1; }
  .primary-basic-info { order: 2; }
  .primary-application { order: 3; }
  .primary-secondary-info { order: 4; }
  .primary-class-structure { order: 5; }
  .primary-teacher-stats { order: 6; }
  .primary-learning { order: 7; }
  .primary-policy { order: 8; }
  .primary-facilities { order: 9; }
  .primary-contact { order: 10; }
  
  /* 中学卡片移动端顺序 */
  /* 创校时间放在基本信息前，收生标准放在入学申请后，设施与交通放在联络资讯前 */
  .secondary-quick-stats { order: 1; }
  .secondary-basic-info { order: 2; }
  .secondary-application { order: 3; }
  .secondary-admission { order: 4; }
  .secondary-class-structure { order: 5; }
  .secondary-curriculum { order: 6; }
  .secondary-teacher-stats { order: 7; }
  .secondary-policies { order: 8; }
  .secondary-learning { order: 9; }
  .secondary-facilities { order: 10; }
  .secondary-contact { order: 11; }
}

/* Card */
.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  padding: 24px;
  transition: box-shadow 0.2s;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Section Title */
.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.section-title-sm {
  font-size: 15px;
}

.section-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 8px;
  font-size: 14px;
}

.section-icon-blue { background: #eff6ff; color: #4A80F0; }
.section-icon-orange { background: #fff7ed; color: #f97316; }
.section-icon-gray { background: #f3f4f6; color: #6b7280; }
.section-icon-purple { background: #f5f3ff; color: #8b5cf6; }
.section-icon-green { background: #f0fdf4; color: #22c55e; }
.section-icon-pink { background: #fdf2f8; color: #ec4899; }
.section-icon-indigo { background: #eef2ff; color: #6366f1; }
.section-icon-yellow { background: #fefce8; color: #eab308; }

/* Quick Stats Card */
.quick-stats-card {
  padding: 20px;
}

.quick-stats-row {
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.quick-stat-item {
  text-align: center;
  flex: 1;
  padding: 0 8px;
  border-right: 1px solid #f3f4f6;
}

.quick-stat-item:last-child {
  border-right: none;
}

.quick-stat-icon {
  color: #9ca3af;
  font-size: 12px;
  margin-bottom: 4px;
}

.quick-stat-value {
  font-size: 14px;
  font-weight: 700;
  color: #1f2937;
}

.quick-stat-label {
  font-size: 11px;
  color: #9ca3af;
  margin-top: 2px;
}

/* Teacher Count Box */
.teacher-count-box {
  display: flex;
  align-items: flex-end;
  background: linear-gradient(135deg, #eff6ff 0%, white 100%);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #dbeafe;
  margin-bottom: 24px;
}

.teacher-count-number {
  font-size: 48px;
  font-weight: 700;
  color: #4A80F0;
  line-height: 1;
  letter-spacing: -0.02em;
}

.teacher-count-info {
  margin-left: 12px;
  display: flex;
  flex-direction: column;
}

.teacher-count-label {
  font-size: 14px;
  font-weight: 700;
  color: #1f2937;
}

/* Progress List */
.progress-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 0 4px;
}

.progress-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  font-weight: 500;
}

.progress-label {
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 6px;
}

.progress-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.progress-dot.bg-blue { background: #3b82f6; }
.progress-dot.bg-purple { background: #8b5cf6; }
.progress-dot.bg-green { background: #22c55e; }

.progress-value {
  font-weight: 700;
  color: #1f2937;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-fill.bg-blue { background: #3b82f6; box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3); }
.progress-fill.bg-purple { background: #8b5cf6; box-shadow: 0 2px 4px rgba(139, 92, 246, 0.3); }
.progress-fill.bg-green { background: #22c55e; box-shadow: 0 2px 4px rgba(34, 197, 94, 0.3); }

/* Experience Section */
.experience-section {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f3f4f6;
}

.experience-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.experience-header h4 {
  font-size: 12px;
  font-weight: 700;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.experience-header i {
  color: #d1d5db;
}

.experience-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.experience-item {
  background: #f9fafb;
  border-radius: 8px;
  padding: 8px;
  text-align: center;
  border: 1px solid #f3f4f6;
}

.experience-item-primary {
  background: rgba(239, 246, 255, 0.5);
  border-color: rgba(191, 219, 254, 0.5);
}

.experience-item-primary .experience-value {
  color: #4A80F0;
}

.experience-value {
  font-size: 18px;
  font-weight: 700;
  color: #6b7280;
}

.experience-label {
  font-size: 10px;
  color: #9ca3af;
  font-weight: 500;
}

/* Admission Notice */
.admission-notice {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: #fff7ed;
  color: #9a3412;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #fed7aa;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.6;
}

.admission-notice i {
  color: #f97316;
  margin-top: 2px;
}

/* Contact List */
.contact-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.contact-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  font-size: 14px;
  color: #6b7280;
  cursor: pointer;
  transition: color 0.2s;
}

.contact-item:hover {
  color: #1f2937;
}

.contact-icon {
  width: 32px;
  height: 32px;
  background: #f9fafb;
  color: #9ca3af;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.contact-item:hover .contact-icon {
  background: #eff6ff;
  color: #4A80F0;
}

.contact-item:hover .contact-icon-green {
  background: #f0fdf4;
  color: #22c55e;
}

.contact-item:hover .contact-icon-purple {
  background: #f5f3ff;
  color: #8b5cf6;
}

.contact-item:hover .contact-icon-blue {
  background: #eff6ff;
  color: #4A80F0;
}

.contact-phone {
  font-family: ui-monospace, monospace;
  color: #1f2937;
  font-weight: 500;
}

.contact-link {
  color: #4A80F0;
  text-decoration: none;
  font-weight: 500;
}

.contact-link:hover {
  text-decoration: underline;
}

/* Class Grid */
.class-grid-container {
  background: #f9fafb;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.class-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.class-grid-header,
.class-grid-values {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 8px;
}

@media (min-width: 768px) {
  .class-grid-header,
  .class-grid-values {
    gap: 16px;
  }
}

.class-grid-label {
  font-size: 12px;
  font-weight: 700;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  text-align: center;
}

.class-grid-value {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  padding: 16px 8px;
  text-align: center;
  font-size: 20px;
  font-weight: 700;
  color: #4A80F0;
  transition: transform 0.3s;
}

.class-grid-value:hover {
  transform: translateY(-4px);
}

/* Primary school class grid (6 columns) */
.class-grid-primary .class-grid-header,
.class-grid-primary .class-grid-values {
  grid-template-columns: repeat(6, 1fr);
}

/* Facilities Stats */
.facilities-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.facility-stat {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f9fafb;
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 14px;
  color: #4b5563;
  border: 1px solid #e5e7eb;
}

.facility-stat i {
  color: #4A80F0;
  font-size: 14px;
}

/* Secondary School Info (升中资讯) */
.secondary-info-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.secondary-info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px 16px;
  border-radius: 10px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}

.secondary-info-through {
  background: linear-gradient(135deg, #fef3c7 0%, #fef9c3 100%);
  border-color: #fcd34d;
}

.secondary-info-direct {
  background: linear-gradient(135deg, #dbeafe 0%, #eff6ff 100%);
  border-color: #93c5fd;
}

.secondary-info-associated {
  background: linear-gradient(135deg, #dcfce7 0%, #f0fdf4 100%);
  border-color: #86efac;
}

.secondary-info-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  width: fit-content;
}

.badge-through {
  background: #fbbf24;
  color: #78350f;
}

.badge-direct {
  background: #3b82f6;
  color: white;
}

.badge-associated {
  background: #22c55e;
  color: white;
}

.secondary-info-content {
  font-size: 14px;
  color: #374151;
  line-height: 1.6;
}

.band1-rate-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 20px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #fef3c7 0%, #fef9c3 100%);
  border-radius: 12px;
  border: 1px solid #fcd34d;
}

.band1-rate-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #92400e;
}

.band1-rate-label i {
  color: #f59e0b;
}

.band1-rate-value {
  font-size: 24px;
  font-weight: 700;
  color: #b45309;
}

/* Yearly Promotion Stats */
.promotion-yearly-stats {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.promotion-subtitle {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 16px 0;
}

.promotion-subtitle i {
  color: #f59e0b;
}

.yearly-stats-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.yearly-stat-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
}

.yearly-stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.yearly-stat-year {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
}

.yearly-stat-rate {
  font-size: 18px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 20px;
  background: #f3f4f6;
}

.yearly-stat-rate.rate-excellent {
  background: linear-gradient(135deg, #fef3c7 0%, #fef9c3 100%);
  color: #b45309;
}

.yearly-stat-rate.rate-good {
  background: linear-gradient(135deg, #dbeafe 0%, #eff6ff 100%);
  color: #1d4ed8;
}

.yearly-stat-rate.rate-average {
  background: linear-gradient(135deg, #dcfce7 0%, #f0fdf4 100%);
  color: #15803d;
}

.yearly-stat-rate.rate-low {
  background: #f3f4f6;
  color: #6b7280;
}

.yearly-stat-summary {
  font-size: 14px;
  color: #000000;
  font-weight: 600;
  margin-bottom: 12px;
}

.yearly-schools-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.yearly-school-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  font-size: 13px;
}

.school-name-text {
  flex: 1;
  color: #374151;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.school-band-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
  white-space: nowrap;
}

.school-band-badge.band-1a {
  background: linear-gradient(135deg, #fef3c7 0%, #fef9c3 100%);
  color: #b45309;
  border: 1px solid #fcd34d;
}

.school-band-badge.band-1b {
  background: linear-gradient(135deg, #fef9c3 0%, #fefce8 100%);
  color: #ca8a04;
  border: 1px solid #fde047;
}

.school-band-badge.band-1c,
.school-band-badge.band-1 {
  background: linear-gradient(135deg, #dbeafe 0%, #eff6ff 100%);
  color: #1d4ed8;
  border: 1px solid #93c5fd;
}

.school-band-badge.band-2 {
  background: linear-gradient(135deg, #dcfce7 0%, #f0fdf4 100%);
  color: #15803d;
  border: 1px solid #86efac;
}

.school-band-badge.band-3 {
  background: #f3f4f6;
  color: #6b7280;
  border: 1px solid #e5e7eb;
}

.school-band-badge.band-unknown {
  background: #f9fafb;
  color: #9ca3af;
  border: 1px solid #e5e7eb;
}

.school-count {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
}

.show-more-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 10px 16px;
  margin-top: 8px;
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s ease;
}

.show-more-btn:hover {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  border-color: #d1d5db;
  color: #374151;
}

.show-more-btn i {
  font-size: 11px;
  transition: transform 0.2s ease;
}

/* Teaching Mode Highlight */
.class-teaching-mode-highlight {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #7dd3fc;
  margin-bottom: 16px;
}

.teaching-mode-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.teaching-mode-icon i {
  color: white;
  font-size: 20px;
}

.teaching-mode-content {
  flex: 1;
}

.teaching-mode-label {
  font-size: 12px;
  font-weight: 600;
  color: #0369a1;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
}

.teaching-mode-text {
  font-size: 15px;
  color: #0c4a6e;
  line-height: 1.6;
  font-weight: 500;
}

/* Compact Class Grid */
.class-grid-compact {
  padding: 16px;
  margin-bottom: 0;
}

.class-grid-compact .class-grid-value {
  padding: 10px 4px;
  font-size: 16px;
  border-radius: 8px;
}

.class-grid-compact .class-grid-label {
  font-size: 11px;
}

@media (max-width: 640px) {
  .class-teaching-mode-highlight {
    padding: 16px;
    gap: 12px;
  }
  
  .teaching-mode-icon {
    width: 40px;
    height: 40px;
  }
  
  .teaching-mode-icon i {
    font-size: 16px;
  }
  
  .teaching-mode-text {
    font-size: 14px;
  }
  
  .class-grid-compact .class-grid-value {
    padding: 8px 2px;
    font-size: 14px;
  }
}

.class-remarks {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #eff6ff;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #bfdbfe;
  font-size: 14px;
  color: #1e40af;
}

.class-remarks i {
  color: #4A80F0;
  margin-top: 2px;
}

.class-remarks p {
  margin: 0;
  line-height: 1.6;
}

/* Curriculum Grid */
.curriculum-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

@media (min-width: 768px) {
  .curriculum-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.curriculum-section {
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  transition: border-color 0.3s;
}

.curriculum-section-junior:hover {
  border-color: #93c5fd;
}

.curriculum-section-senior:hover {
  border-color: #86efac;
}

.curriculum-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-weight: 700;
  color: #1f2937;
  transition: background 0.2s;
}

.curriculum-section-junior:hover .curriculum-header {
  background: rgba(239, 246, 255, 0.5);
}

.curriculum-section-senior:hover .curriculum-header {
  background: rgba(240, 253, 244, 0.5);
}

.curriculum-header-left {
  display: flex;
  align-items: center;
}

.curriculum-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}

.curriculum-dot-blue { background: #4A80F0; }
.curriculum-dot-green { background: #22c55e; }

.curriculum-note {
  font-size: 12px;
  color: #9ca3af;
  font-weight: 400;
}

.curriculum-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.subject-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.subject-group-label {
  font-size: 12px;
  font-weight: 700;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  gap: 6px;
}

.subject-group-label i {
  font-size: 10px;
}

.subject-group-label-english {
  color: #4A80F0;
}

.subject-group-label-mixed {
  color: #f59e0b;
}

.subject-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.subject-tag {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  transition: all 0.2s;
}

.subject-tag-chinese {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  color: #6b7280;
}

.subject-tag-chinese:hover {
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.subject-tag-english {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #4A80F0;
  font-weight: 500;
}

.subject-tag-english:hover {
  background: #dbeafe;
}

.subject-tag-mixed {
  background: #fffbeb;
  border: 1px solid #fde68a;
  color: #d97706;
}

.subject-tag-mixed:hover {
  background: #fef3c7;
}

/* Policies Grid */
.policies-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

@media (min-width: 768px) {
  .policies-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.policy-card {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.policy-content {
  flex: 1;
  background: #f9fafb;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e5e7eb;
  position: relative;
  overflow: hidden;
}

.policy-content p {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.6;
  text-align: justify;
  position: relative;
  z-index: 1;
}

.policy-quote-icon {
  position: absolute;
  bottom: 8px;
  right: 8px;
  font-size: 48px;
  color: #e5e7eb;
  opacity: 0.5;
}

.policy-quote-icon-green {
  color: #d1fae5;
}

/* Facilities Grid */
.facilities-grid {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

@media (min-width: 768px) {
  .facilities-grid {
    flex-direction: row;
  }
}

.facility-item {
  flex: 1;
}

.facility-label {
  font-weight: 700;
  color: #1f2937;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.facility-label i {
  color: #f97316;
}

.facility-item:last-child .facility-label i {
  color: #4A80F0;
}

.facility-content {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.8;
  transition: box-shadow 0.2s;
}

.facility-content:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* Learning List */
.learning-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.learning-item {
  background: #f9fafb;
  border-radius: 12px;
  padding: 16px;
  border-left: 4px solid #4A80F0;
}

.learning-label {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.learning-text {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.6;
}

/* Features List (小学) */
.features-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.features-list li {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  font-size: 14px;
  color: #4b5563;
  line-height: 1.6;
}

.features-list li i {
  color: #22c55e;
  margin-top: 4px;
}

/* Basic Info Grid (小学 & 中学) */
.basic-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item-full {
  grid-column: 1 / -1;
}

.info-item label {
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
}

.info-item div {
  font-size: 16px;
  color: #1f2937;
  font-weight: 500;
}

/* Info Item with Popup */
.info-item-with-popup {
  position: relative;
}

.info-item-with-popup label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.info-icon {
  cursor: pointer;
  color: #9ca3af;
  font-size: 12px;
  transition: color 0.2s;
}

.info-icon:hover {
  color: #4A80F0;
}

.info-icon i {
  font-size: 12px;
}

/* Language Info Popup */
.language-info-popup {
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 100;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  border: 1px solid #e5e7eb;
  width: 360px;
  max-width: calc(100vw - 32px);
  margin-top: 8px;
  overflow: hidden;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-weight: 600;
  font-size: 14px;
  color: #1f2937;
}

.popup-close {
  background: none;
  border: none;
  cursor: pointer;
  color: #9ca3af;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.popup-close:hover {
  color: #1f2937;
}

.popup-content {
  padding: 16px;
}

.language-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.language-table th {
  text-align: left;
  padding: 8px 10px;
  background: #f3f4f6;
  color: #6b7280;
  font-weight: 600;
  font-size: 12px;
}

.language-table td {
  padding: 10px;
  border-bottom: 1px solid #f3f4f6;
  color: #4b5563;
}

.language-table tr:last-child td {
  border-bottom: none;
}

.language-table tr.highlight {
  background: #eff6ff;
}

.language-table tr.highlight td {
  color: #1d4ed8;
  font-weight: 500;
}

.language-table .category {
  font-weight: 600;
  color: #1f2937;
}

.language-table .ratio {
  font-family: ui-monospace, monospace;
  color: #4A80F0;
  font-weight: 500;
}

.language-table .desc {
  color: #6b7280;
  font-size: 12px;
}

.popup-note {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
  font-size: 12px;
  color: #9ca3af;
  text-align: center;
}

/* Mobile Action Bar */
.mobile-action-bar {
  display: flex;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-top: 1px solid #e5e7eb;
  padding: 12px 16px;
  gap: 16px;
  z-index: 50;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.06);
}

@media (min-width: 768px) {
  .mobile-action-bar {
    display: none;
  }
}

.mobile-action-left {
  display: flex;
  gap: 20px;
  padding: 0 8px;
}

.mobile-action-icon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #6b7280;
  background: none;
  border: none;
  cursor: pointer;
  transition: transform 0.2s;
}

.mobile-action-icon:active {
  transform: scale(0.95);
}

.mobile-action-icon i {
  font-size: 20px;
}

.mobile-action-icon span {
  font-size: 10px;
  font-weight: 500;
}

.mobile-action-primary {
  flex: 1;
  background: #4A80F0;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px;
  font-weight: 700;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  box-shadow: 0 10px 15px rgba(74, 128, 240, 0.2);
  transition: transform 0.2s;
}

.mobile-action-primary:active {
  transform: scale(0.95);
}

/* Toast Message */
.toast-message {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 12px 24px;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 500;
  z-index: 100;
  animation: fadeIn 0.2s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, -40%);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%);
  }
}

/* Mobile Responsive Adjustments */
@media (max-width: 767px) {
  .header-gradient {
    padding-top: 16px;
    padding-bottom: 64px;
  }

  .breadcrumb {
    margin-bottom: 16px;
    font-size: 12px;
  }

  .school-name {
    font-size: 24px;
  }

  .school-english-name {
    font-size: 14px;
    margin-bottom: 16px;
  }

  .header-tags {
    gap: 8px;
  }

  .tag {
    padding: 4px 10px;
    font-size: 12px;
  }

  .main-container {
    padding-bottom: 120px;
  }

  .card {
    padding: 16px;
  }

  .section-title {
    font-size: 15px;
  }

  .teacher-count-number {
    font-size: 40px;
  }

  .class-grid-value {
    font-size: 16px;
    padding: 12px 4px;
  }
}

/* Application Cards */
.application-cards-container {
  margin-bottom: 24px;
}

.section-title-standalone {
  margin-bottom: 16px;
}

.application-cards {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

@media (min-width: 640px) {
  .application-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

.application-card {
  position: relative;
  background: white;
  border-radius: 16px;
  padding: 20px;
  border: 2px solid #e5e7eb;
  transition: all 0.3s ease;
  overflow: hidden;
}

.application-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
}

.application-card.card-open {
  border-color: #10b981;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
}

.application-card.card-open::before {
  background: linear-gradient(90deg, #10b981, #34d399);
}

.application-card.card-closed {
  border-color: #e5e7eb;
  background: #f9fafb;
}

.application-card.card-closed::before {
  background: linear-gradient(90deg, #9ca3af, #d1d5db);
}

.card-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.card-status-badge.badge-open {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  color: #047857;
}

.card-status-badge.badge-closed {
  background: #f3f4f6;
  color: #6b7280;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.card-grade {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-grade i {
  color: #4A80F0;
  font-size: 16px;
}

.card-period {
  font-size: 14px;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 6px;
}

.card-period i {
  font-size: 12px;
}

.card-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #4A80F0, #6366f1);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s ease;
  width: fit-content;
}

.card-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(74, 128, 240, 0.3);
}

.card-link i {
  font-size: 11px;
}

.card-closed .card-grade {
  color: #6b7280;
}

.card-closed .card-grade i {
  color: #9ca3af;
}

.card-closed .card-link {
  background: #9ca3af;
}

/* Mobile Application Cards */
@media (max-width: 639px) {
  .application-card {
    padding: 16px;
  }

  .card-grade {
    font-size: 16px;
  }

  .card-period {
    font-size: 13px;
  }

  .card-link {
    padding: 6px 12px;
    font-size: 12px;
  }
}

/* Recommendations Section */
.recommendations-section {
  margin-top: 48px;
  padding-top: 32px;
  border-top: 1px solid #e5e7eb;
}

.recommendations-title {
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.recommendations-title i {
  color: #4A80F0;
}

.recommendation-group {
  margin-bottom: 28px;
}

.recommendation-group-title {
  font-size: 16px;
  font-weight: 600;
  color: #4b5563;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.recommendation-group-title i {
  color: #6b7280;
  font-size: 14px;
}

.recommendation-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

@media (min-width: 640px) {
  .recommendation-list {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .recommendation-list {
    grid-template-columns: repeat(3, 1fr);
  }
}

.recommendation-card {
  display: block;
  background: white;
  border-radius: 12px;
  padding: 16px;
  text-decoration: none;
  transition: all 0.2s ease;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.recommendation-card:hover {
  border-color: #4A80F0;
  box-shadow: 0 4px 12px rgba(74, 128, 240, 0.15);
  transform: translateY(-2px);
}

.recommendation-card-popular {
  background: linear-gradient(135deg, #fefce8 0%, #fef9c3 100%);
  border-color: #fde047;
}

.recommendation-card-popular:hover {
  border-color: #facc15;
  box-shadow: 0 4px 12px rgba(250, 204, 21, 0.25);
}

.rec-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.rec-school-name {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.4;
  flex: 1;
  margin-right: 8px;
}

.rec-arrow {
  color: #9ca3af;
  font-size: 12px;
  transition: transform 0.2s ease;
}

.recommendation-card:hover .rec-arrow {
  transform: translateX(4px);
  color: #4A80F0;
}

.rec-card-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  font-size: 13px;
  color: #6b7280;
}

.rec-meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.rec-meta-item i {
  font-size: 11px;
}

.rec-meta-divider {
  color: #d1d5db;
  margin: 0 4px;
}

.rec-meta-highlight {
  color: #b45309;
  font-weight: 500;
}

.rec-meta-highlight i {
  color: #f59e0b;
}

/* Mobile Recommendations */
@media (max-width: 639px) {
  .recommendations-section {
    margin-top: 32px;
    padding-top: 24px;
  }

  .recommendations-title {
    font-size: 18px;
    margin-bottom: 20px;
  }

  .recommendation-group-title {
    font-size: 14px;
    margin-bottom: 12px;
  }

  .recommendation-card {
    padding: 14px;
  }

  .rec-school-name {
    font-size: 14px;
  }

  .rec-card-meta {
    font-size: 12px;
  }
}
</style>
