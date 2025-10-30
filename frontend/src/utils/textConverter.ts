/**
 * 简繁体转换工具
 * 提供简体中文和繁体中文之间的转换功能
 */

// 简体到繁体映射表（常用字符）
const simplifiedToTraditional: Record<string, string> = {
  // 基础字符
  '学': '學',
  '校': '校',
  '小': '小',
  '中': '中',
  '学': '學',
  '生': '生',
  '教': '教',
  '师': '師',
  '课': '課',
  '程': '程',
  '班': '班',
  '级': '級',
  '年': '年',
  '级': '級',
  '学': '學',
  '校': '校',
  '名': '名',
  '称': '稱',
  '地': '地',
  '区': '區',
  '网': '網',
  '络': '絡',
  '联': '聯',
  '系': '系',
  '直': '直',
  '属': '屬',
  '联': '聯',
  '系': '系',
  '中': '中',
  '学': '學',
  '结': '結',
  '龙': '龍',
  '学': '學',
  '校': '校',
  '联': '聯',
  '系': '系',
  '中': '中',
  '学': '學',
  
  // 常用词汇
  '学校': '學校',
  '小学': '小學',
  '中学': '中學',
  '学生': '學生',
  '教师': '教師',
  '课程': '課程',
  '班级': '班級',
  '年级': '年級',
  '学校名称': '學校名稱',
  '地区': '地區',
  '网络': '網絡',
  '联系': '聯繫',
  '直属': '直屬',
  '联系中学': '聯繫中學',
  '结龙学校': '結龍學校',
  '直属中学': '直屬中學',
  
  // 界面文本
  '搜索': '搜索',
  '学校': '學校',
  '名称': '名稱',
  '地区': '地區',
  '校网': '校網',
  '等': '等',
  '详情': '詳情',
  '学费': '學費',
  '截止': '截止',
  '开放申请': '開放申請',
  '申请截止': '申請截止',
  '即将截止': '即將截止',
  '升Band': '升Band',
  '比例': '比例',
  '详情': '詳情',
  '结龙学校': '結龍學校',
  '直属中学': '直屬中學',
  '联系中学': '聯繫中學',
  '正在加载': '正在加載',
  '学校信息': '學校信息',
  '加载失败': '加載失敗',
  '重试': '重試',
  '已加载全部': '已加載全部',
  '所学校': '所學校',
  '正在加载更多': '正在加載更多',
  '没有更多数据': '沒有更多數據',
  '提示': '提示',
  '已加载全部': '已加載全部',
  '所学校': '所學校',
  
  // 学校类型
  '名校联盟': '名校聯盟',
  '传统名校': '傳統名校',
  '直资学校': '直資學校',
  '官立学校': '官立學校',
  '私立学校': '私立學校',
  '资助学校': '資助學校',
  
  // 性别
  '男女校': '男女校',
  '男校': '男校',
  '女校': '女校',
  
  // 其他常用词
  '信息': '信息',
  '数据': '數據',
  '统计': '統計',
  '报告': '報告',
  '分析': '分析',
  '结果': '結果',
  '成功': '成功',
  '失败': '失敗',
  '错误': '錯誤',
  '警告': '警告',
  '提示': '提示',
  '确认': '確認',
  '取消': '取消',
  '保存': '保存',
  '删除': '刪除',
  '编辑': '編輯',
  '添加': '添加',
  '更新': '更新',
  '刷新': '刷新',
  '返回': '返回',
  '前进': '前進',
  '后退': '後退',
  '首页': '首頁',
  '上一页': '上一頁',
  '下一页': '下一頁',
  '最后一页': '最後一頁',
  '第一页': '第一頁',
  '页': '頁',
  '共': '共',
  '条': '條',
  '记录': '記錄',
  '显示': '顯示',
  '隐藏': '隱藏',
  '展开': '展開',
  '收起': '收起',
  '更多': '更多',
  '全部': '全部',
  '部分': '部分',
  '选择': '選擇',
  '全选': '全選',
  '取消选择': '取消選擇',
  '清空': '清空',
  '重置': '重置',
  '提交': '提交',
  '发送': '發送',
  '接收': '接收',
  '下载': '下載',
  '上传': '上傳',
  '导入': '導入',
  '导出': '導出',
  '打印': '打印',
  '预览': '預覽',
  '查看': '查看',
  '详情': '詳情',
  '设置': '設置',
  '配置': '配置',
  '选项': '選項',
  '参数': '參數',
  '值': '值',
  '名称': '名稱',
  '标题': '標題',
  '内容': '內容',
  '描述': '描述',
  '说明': '說明',
  '备注': '備註',
  '注释': '註釋',
  '标签': '標籤',
  '分类': '分類',
  '类别': '類別',
  '类型': '類型',
  '状态': '狀態',
  '状态': '狀態',
  '进度': '進度',
  '完成': '完成',
  '进行中': '進行中',
  '暂停': '暫停',
  '停止': '停止',
  '开始': '開始',
  '结束': '結束',
  '时间': '時間',
  '日期': '日期',
  '年份': '年份',
  '月份': '月份',
  '星期': '星期',
  '小时': '小時',
  '分钟': '分鐘',
  '秒': '秒',
  '毫秒': '毫秒',
  '今天': '今天',
  '昨天': '昨天',
  '明天': '明天',
  '本周': '本週',
  '上周': '上週',
  '下周': '下週',
  '本月': '本月',
  '上月': '上月',
  '下月': '下月',
  '今年': '今年',
  '去年': '去年',
  '明年': '明年'
}

// 繁体到简体映射表
const traditionalToSimplified: Record<string, string> = Object.fromEntries(
  Object.entries(simplifiedToTraditional).map(([key, value]) => [value, key])
)

/**
 * 简体转繁体
 * @param text 简体中文文本
 * @returns 繁体中文文本
 */
export function simplifiedToTraditionalText(text: string): string {
  if (!text) return text
  
  let result = text
  for (const [simplified, traditional] of Object.entries(simplifiedToTraditional)) {
    result = result.replace(new RegExp(simplified, 'g'), traditional)
  }
  return result
}

/**
 * 繁体转简体
 * @param text 繁体中文文本
 * @returns 简体中文文本
 */
export function traditionalToSimplifiedText(text: string): string {
  if (!text) return text
  
  let result = text
  for (const [traditional, simplified] of Object.entries(traditionalToSimplified)) {
    result = result.replace(new RegExp(traditional, 'g'), simplified)
  }
  return result
}

/**
 * 根据语言类型转换文本
 * @param text 原始文本
 * @param targetLanguage 目标语言
 * @returns 转换后的文本
 */
export function convertTextByLanguage(text: string, targetLanguage: 'zh-CN' | 'zh-TW'): string {
  if (!text) return text
  
  if (targetLanguage === 'zh-TW') {
    return simplifiedToTraditionalText(text)
  } else {
    return traditionalToSimplifiedText(text)
  }
}

/**
 * 检测文本是否为繁体中文
 * @param text 待检测的文本
 * @returns 是否为繁体中文
 */
export function isTraditionalChinese(text: string): boolean {
  if (!text) return false
  
  // 检查是否包含繁体字符
  const traditionalChars = Object.keys(traditionalToSimplified)
  return traditionalChars.some(char => text.includes(char))
}

/**
 * 检测文本是否为简体中文
 * @param text 待检测的文本
 * @returns 是否为简体中文
 */
export function isSimplifiedChinese(text: string): boolean {
  if (!text) return false
  
  // 检查是否包含简体字符
  const simplifiedChars = Object.keys(simplifiedToTraditional)
  return simplifiedChars.some(char => text.includes(char))
}
