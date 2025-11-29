/**
 * 前端防复制机制
 * 限制普通用户的复制操作
 */

export function initAntiCopy() {
  if (import.meta.env.DEV) {
    // 开发环境不启用，方便调试
    return;
  }

  // 1. CSS 禁用选择 (动态注入)
  const style = document.createElement('style');
  style.innerHTML = `
    .no-copy {
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      user-select: none;
    }
    
    /* 保护关键数据区域 */
    .school-data, .detail-content {
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      user-select: none;
    }
  `;
  document.head.appendChild(style);

  // 2. JS 禁用右键菜单
  document.addEventListener('contextmenu', (e) => {
    // 允许在输入框中使用右键
    if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
      return;
    }
    e.preventDefault();
  }, false);

  // 3. 监听复制事件并干扰
  document.addEventListener('copy', (e) => {
    const selection = window.getSelection();
    // 如果复制内容包含敏感数据，阻止复制或添加版权信息
    if (selection && selection.toString().length > 0) {
       // 可选：直接阻止
       // e.preventDefault();
       
       // 或者：添加版权后缀
       const clipboardData = e.clipboardData;
       if (clipboardData) {
         e.preventDefault();
         const text = selection.toString();
         clipboardData.setData('text/plain', text);
       }
    }
  });
}

