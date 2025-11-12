/**
 * 插班申请状态判断工具函数
 * 用于学校卡片和详情弹窗的申请状态判断
 */

/**
 * 解析月份
 */
export const parseMonth = (dateStr: string): number | null => {
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

/**
 * 解析日期字符串
 */
export const parseDate = (dateStr: string): Date | null => {
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

/**
 * 检查申请是否开放
 */
export const isCardOpen = (info: any, isTransfer = false): boolean => {
  if (!info) return false
  
  const now = new Date()
  
  if (isTransfer) {
    // 检查插班信息，可能有多个时间段
    const startTime1 = info.插班申请开始时间1
    const startTime2 = info.插班申请开始时间2
    const end1 = info.插班申请截止时间1 ? parseDate(info.插班申请截止时间1) : null
    const end2 = info.插班申请截止时间2 ? parseDate(info.插班申请截止时间2) : null
    
    // 检查是否明确标记为"开放申请"或"开放中"
    let hasOpenStatus1 = false
    let hasOpenStatus2 = false
    
    if (startTime1 && typeof startTime1 === 'string') {
      const start1Lower = startTime1.toLowerCase().trim()
      if (start1Lower.includes('开放申请') || start1Lower.includes('开放中')) {
        hasOpenStatus1 = true
        // 如果有截止时间，需要检查是否已过期
        if (end1) {
          if (now <= end1) return true
          // 截止时间已过，继续检查其他条件
        } else {
          // 没有截止时间，认为是开放的
          return true
        }
      }
    }
    
    if (startTime2 && typeof startTime2 === 'string') {
      const start2Lower = startTime2.toLowerCase().trim()
      if (start2Lower.includes('开放申请') || start2Lower.includes('开放中')) {
        hasOpenStatus2 = true
        // 如果有截止时间，需要检查是否已过期
        if (end2) {
          if (now <= end2) return true
          // 截止时间已过，继续检查其他条件
        } else {
          // 没有截止时间，认为是开放的
          return true
        }
      }
    }
    
    // 检查"每年X月"格式 - 当前月份匹配则认为开放
    if (startTime1 && typeof startTime1 === 'string' && startTime1.includes('每年')) {
      const month = parseMonth(startTime1)
      if (month !== null && now.getMonth() === month) return true
    }
    if (startTime2 && typeof startTime2 === 'string' && startTime2.includes('每年')) {
      const month2 = parseMonth(startTime2)
      if (month2 !== null && now.getMonth() === month2) return true
    }
    
    // 检查具体日期范围
    const start1 = startTime1 ? parseDate(startTime1) : null
    const start2 = startTime2 ? parseDate(startTime2) : null
    
    // 只有开始时间，没有截止时间的情况
    // 只在开始时间后的合理范围内（90天）认为是开放
    if (start1 && !end1) {
      const daysSinceStart = (now.getTime() - start1.getTime()) / (1000 * 60 * 60 * 24)
      if (daysSinceStart >= 0 && daysSinceStart <= 90) return true
    }
    if (start2 && !end2) {
      const daysSinceStart = (now.getTime() - start2.getTime()) / (1000 * 60 * 60 * 24)
      if (daysSinceStart >= 0 && daysSinceStart <= 90) return true
    }
    
    // 有开始和截止时间，检查是否在范围内
    if (start1 && end1 && now >= start1 && now <= end1) return true
    if (start2 && end2 && now >= start2 && now <= end2) return true
    
    return false
  } else {
    // S1/小一申请
    const startTime = info.入学申请开始时间 || info.小一入学申请开始时间
    const end = info.入学申请截至时间 || info.小一入学申请截至时间 ? parseDate(info.入学申请截至时间 || info.小一入学申请截至时间) : null
    
    // 检查是否为"开放申请"或"开放中"
    if (startTime && typeof startTime === 'string') {
      const startLower = startTime.toLowerCase().trim()
      if (startLower.includes('开放申请') || startLower.includes('开放中')) {
        // 如果有截止时间，需要检查是否已过期
        if (end) {
          return now <= end
        } else {
          // 没有截止时间，认为是开放的
          return true
        }
      }
    }
    
    const start = startTime ? parseDate(startTime) : null
    
    // 有开始和截止时间，检查是否在范围内
    if (start && end && now >= start && now <= end) return true
    
    // 只有开始时间，没有截止时间的情况
    // 只在开始时间后的合理范围内（90天）认为是开放
    if (start && !end) {
      const daysSinceStart = (now.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)
      if (daysSinceStart >= 0 && daysSinceStart <= 90) return true
    }
    
    return false
  }
}

/**
 * 检查是否明确标记为"未开放"
 */
export const isMarkedAsClosed = (info: any, isTransfer = false): boolean => {
  if (!info) return false
  
  if (isTransfer) {
    const startTime1 = info.插班申请开始时间1
    const startTime2 = info.插班申请开始时间2
    const endTime1 = info.插班申请截止时间1
    
    // 检查是否包含"未开放"或"暂未开放"字样
    const checkClosed = (str: any) => {
      if (str && typeof str === 'string') {
        const lower = str.toLowerCase().trim()
        return lower.includes('未开放') || lower.includes('暂未开放')
      }
      return false
    }
    
    return checkClosed(startTime1) || checkClosed(startTime2) || checkClosed(endTime1)
  }
  
  return false
}

/**
 * 格式化日期范围
 * 如果无法解析为日期（如"开放申请"），则直接返回原始文本
 */
export const formatDateRange = (start?: string, end?: string): string => {
  if (!start) return '-'
  if (!end) return start // 只有开始时间，直接返回
  
  const formatDateStr = (dateStr: string): string => {
    const date = parseDate(dateStr)
    if (!date) return dateStr // 无法解析，返回原始文本
    return `${date.getFullYear()}.${date.getMonth() + 1}.${date.getDate()}`
  }
  
  const formattedStart = formatDateStr(start)
  const formattedEnd = formatDateStr(end)
  
  // 如果都无法解析为日期，只返回开始时间文本
  if (formattedStart === start && formattedEnd === end && parseDate(start) === null) {
    return start
  }
  
  return `${formattedStart}-${formattedEnd}`
}

