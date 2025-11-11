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
  if (tuition === undefined || tuition === null || tuition === '' || tuition === "-") {
    return 'HKD 0'
  }
  // 如果是数字，直接格式化
  if (typeof tuition === 'number') {
    return `HKD ${tuition.toLocaleString('en-US')}`
  }
  // 如果是字符串，尝试提取数字和期数
  if (typeof tuition === 'string') {
    // 尝试是否能全部转成数字
    const num = parseInt(tuition)
    if (!isNaN(num)) {
      return `HKD ${num.toLocaleString('en-US')}`
    }
    return tuition
  }

  return `HKD ${tuition}`
}

