# 简繁体转换工具完善方案

## 现有方案分析

### 1. 转换机制
- **工具位置**: `frontend/src/utils/textConverter.ts`
- **调用方式**: 通过 `language.ts` store 的 `convertText` 方法调用 `convertTextByLanguage`
- **转换逻辑**: 基于字符和词汇映射表的字符串替换

### 2. 现有问题
1. **重复映射**: 原代码中存在重复的键（如多个 '学': '學'）
2. **词库不完整**: 很多常用字符缺失映射
3. **转换顺序**: 原代码没有处理优先级，可能导致词汇被拆分

### 3. 完善方案

#### 3.1 词库结构优化
- **优先处理长词汇**: 先映射多字词汇，再映射单字，避免词汇被拆分
- **分类组织**: 
  - 常用词汇（优先）
  - 基础字符映射（教育、姓名、机构等分类）
  - 常用词汇（单字组合）

#### 3.2 转换函数优化
```typescript
// 按长度降序排列，确保长词汇优先处理
const entries = Object.entries(simplifiedToTraditional)
  .sort(([a], [b]) => b.length - a.length)
```

#### 3.3 词库补充
参考后端词库（`backend/backend/utils/text_converter.py`），补充了：
- 教育相关字符（学、教、师、课、程等）
- 常用汉字（书、国、华、圣、为等）
- 人名常用字（刘、张、陈、杨、黄等）
- 机构相关（会、社、团、联、总等）
- 动词、形容词、数量词
- 香港特有字符（湾、岛、区、道、街等）

## 使用方法

### 基础使用
```typescript
import { convertTextByLanguage } from '@/utils/textConverter'

// 简体转繁体
const traditional = convertTextByLanguage('学校', 'zh-TW')  // '學校'

// 繁体转简体
const simplified = convertTextByLanguage('學校', 'zh-CN')  // '学校'
```

### 在 Store 中使用
```typescript
import { useLanguageStore } from '@/stores/language'

const languageStore = useLanguageStore()
const converted = languageStore.convertText('学校名称')  // 根据当前语言自动转换
```

## 继续完善词库的建议

### 1. 识别未转换的字符
- 在实际使用中收集未转换的字符
- 检查控制台警告（如果有）
- 用户反馈

### 2. 按类别补充
- **地名**: 香港各区、街道名称
- **学校相关**: 学校类型、课程名称、评估方式
- **界面文本**: 所有 UI 显示的文本
- **数据字段**: 后端返回的字段名称

### 3. 测试建议
```typescript
// 测试用例示例
const testCases = [
  ['学校名称', '學校名稱'],
  ['联系中学', '聯繫中學'],
  ['正在加载', '正在加載'],
  // 添加更多测试用例
]

testCases.forEach(([simp, trad]) => {
  const result = convertTextByLanguage(simp, 'zh-TW')
  console.assert(result === trad, `Failed: ${simp} -> ${result} (expected: ${trad})`)
})
```

### 4. 维护建议
1. **定期更新**: 根据实际使用情况补充词库
2. **保持一致性**: 前端和后端词库保持同步
3. **优先级**: 词汇映射优先于字符映射
4. **避免重复**: 确保每个键只出现一次

