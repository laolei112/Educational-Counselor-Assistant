/**
 * 格式化工具函数
 */

/**
 * 格式化学费显示
 * @param tuition 学费金额（可以是数字、字符串或undefined）
 * @returns 格式化后的学费字符串
 */
export const formatTuition = (tuition: number | string | undefined): string => {
  // 处理空值情况
  if (tuition === undefined || tuition === null || tuition === '') {
    return '0港元/年'
  }

  return `${tuition}`
}

