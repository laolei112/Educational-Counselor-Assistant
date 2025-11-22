/**
 * 节流函数 - 限制函数执行频率
 * @param func 要节流的函数
 * @param delay 延迟时间（毫秒）
 * @returns 节流后的函数
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastCall = 0
  let timeoutId: ReturnType<typeof setTimeout> | null = null

  return function (this: any, ...args: Parameters<T>) {
    const now = Date.now()
    const timeSinceLastCall = now - lastCall

    if (timeSinceLastCall >= delay) {
      lastCall = now
      func.apply(this, args)
    } else {
      // 清除之前的定时器
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
      // 设置新的定时器，确保最后一次调用也会执行
      timeoutId = setTimeout(() => {
        lastCall = Date.now()
        func.apply(this, args)
      }, delay - timeSinceLastCall)
    }
  }
}

/**
 * 使用 requestAnimationFrame 的节流函数
 * 适合用于滚动、resize 等高频事件
 * @param func 要节流的函数
 * @returns 节流后的函数
 */
export function rafThrottle<T extends (...args: any[]) => any>(
  func: T
): (...args: Parameters<T>) => void {
  let rafId: number | null = null
  let lastArgs: Parameters<T> | null = null

  return function (this: any, ...args: Parameters<T>) {
    lastArgs = args

    if (rafId === null) {
      rafId = requestAnimationFrame(() => {
        if (lastArgs) {
          func.apply(this, lastArgs)
        }
        rafId = null
        lastArgs = null
      })
    }
  }
}

