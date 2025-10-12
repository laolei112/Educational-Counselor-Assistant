# Utils 工具函数

本目录包含项目中可复用的工具函数。

## 文件说明

### formatter.ts
格式化相关的工具函数。

#### formatTuition
格式化学费显示的函数。

**参数:**
- `tuition: number | string | undefined` - 学费金额

**返回值:**
- `string` - 格式化后的学费字符串

**使用示例:**
```typescript
import { formatTuition } from '@/utils/formatter'

// 正常值
formatTuition(5000)        // "5000港元/年"
formatTuition("10000")     // "10000港元/年"

// 空值处理
formatTuition(undefined)   // "0港元/年"
formatTuition(null)        // "0港元/年"
formatTuition('')          // "0港元/年"
```

**使用位置:**
- `SchoolCard.vue` - 学校卡片列表
- `SchoolDetailModal.vue` - 学校详情弹窗

## 添加新的工具函数

1. 在对应的文件中添加函数（如果是新类型的工具，创建新文件）
2. 添加完整的 JSDoc 注释
3. 导出函数
4. 在本 README 中添加说明

## 命名规范

- 使用驼峰命名法
- 函数名应该清晰描述其功能
- 格式化函数以 `format` 开头
- 验证函数以 `validate` 或 `is` 开头
- 转换函数以 `convert` 或 `to` 开头

