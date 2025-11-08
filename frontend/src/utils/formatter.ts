/**
 * 格式化工具函数
 */

/**
 * 格式化学费显示
 * @param tuition 学费金额（可以是数字、字符串或undefined）
 * @returns 格式化后的学费字符串，格式：$53,680 / 10 期
 */
export const formatTuition = (tuition: number | string | undefined): string => {
  // 处理空值情况
  if (tuition === undefined || tuition === null || tuition === '') {
    return '—'
  }

  // 如果是字符串，尝试提取数字和期数
  if (typeof tuition === 'string') {
    // 匹配格式：数字（可能包含逗号）和期数信息
    const match = tuition.match(/([\d,]+)(?:\s*[\/／]\s*(\d+)\s*期)?/)
    if (match) {
      const amount = match[1].replace(/,/g, '')
      const periods = match[2]
      
      // 格式化金额：添加千位分隔符
      const formattedAmount = parseInt(amount).toLocaleString('en-US')
      
      if (periods) {
        return `$${formattedAmount} / ${periods} 期`
      }
      return `$${formattedAmount}`
    }
    
    // 如果包含"分十期"等字样，提取期数
    const periodMatch = tuition.match(/(\d+)\s*期/)
    if (periodMatch) {
      const numMatch = tuition.match(/([\d,]+)/)
      if (numMatch) {
        const amount = numMatch[1].replace(/,/g, '')
        const formattedAmount = parseInt(amount).toLocaleString('en-US')
        return `$${formattedAmount} / ${periodMatch[1]} 期`
      }
    }
    
    // 如果只是数字字符串
    const numOnly = tuition.replace(/[^\d,]/g, '')
    if (numOnly) {
      const amount = numOnly.replace(/,/g, '')
      const formattedAmount = parseInt(amount).toLocaleString('en-US')
      return `$${formattedAmount}`
    }
    
    return tuition
  }

  // 如果是数字，直接格式化
  if (typeof tuition === 'number') {
    return `$${tuition.toLocaleString('en-US')}`
  }

  return `${tuition}`
}

