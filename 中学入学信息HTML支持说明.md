# 中学入学信息HTML支持优化说明

## 更新内容

### 1. 样式优化
将入学信息的样式调整为与其他部分保持一致，去除突兀的背景色和边框设计。

**之前的样式（突兀）：**
- ❌ 浅灰色背景
- ❌ 左侧蓝色边框
- ❌ 独立卡片样式

**现在的样式（统一）：**
- ✅ 与其他section保持一致
- ✅ 简洁清爽的排版
- ✅ 更好的视觉连贯性

### 2. HTML文本支持
使用 `v-html` 指令支持HTML格式的入学信息内容。

**修改对比：**
```vue
<!-- 之前：纯文本显示 -->
<div class="admission-content">
  {{ school.admissionInfo }}
</div>

<!-- 现在：支持HTML -->
<div class="admission-content" v-html="school.admissionInfo"></div>
```

## 样式设计

### 基础样式
```css
.admission-content {
  color: #2c3e50;
  font-size: 15px;
  line-height: 1.8;
}
```

### HTML元素支持

#### 段落 (p)
```css
.admission-content p {
  margin: 8px 0;
}
```

#### 列表 (ul, ol)
```css
.admission-content ul,
.admission-content ol {
  margin: 8px 0;
  padding-left: 24px;
}

.admission-content li {
  margin: 4px 0;
  line-height: 1.6;
}
```

#### 强调文本 (strong, b)
```css
.admission-content strong,
.admission-content b {
  font-weight: 600;
  color: #2c3e50;
}
```

#### 换行 (br)
```css
.admission-content br {
  line-height: 2;
}
```

## 支持的HTML标签

入学信息可以使用以下HTML标签：

### 文本格式化
- `<p>` - 段落
- `<br>` - 换行
- `<strong>` / `<b>` - 加粗
- `<em>` / `<i>` - 斜体

### 列表
- `<ul>` - 无序列表
- `<ol>` - 有序列表
- `<li>` - 列表项

### 标题（不推荐，已有h3标题）
- `<h4>`, `<h5>`, `<h6>` - 小标题

## 数据示例

### 纯文本格式
```
中一入学信息：
自行分配学位中一收生人数：180
统一派位中一收生人数：180
```

### HTML格式
```html
<p><strong>中一入学信息：</strong></p>
<ul>
  <li>自行分配学位中一收生人数：<strong>180</strong></li>
  <li>统一派位中一收生人数：<strong>180</strong></li>
</ul>
<p><strong>收生准则：</strong></p>
<ol>
  <li>学业成绩（40%）</li>
  <li>面试表现（30%）</li>
  <li>操行及品德（20%）</li>
  <li>课外活动及服务（10%）</li>
</ol>
```

### 显示效果对比

**纯文本：**
```
中一入学信息：
自行分配学位中一收生人数：180
统一派位中一收生人数：180
收生准则：
1. 学业成绩（40%）
2. 面试表现（30%）
```

**HTML格式：**
```
中一入学信息：
• 自行分配学位中一收生人数：180
• 统一派位中一收生人数：180

收生准则：
1. 学业成绩（40%）
2. 面试表现（30%）
3. 操行及品德（20%）
```

## 页面结构

```
学校详情页
├─ 📋 基本信息
│   └─ 学校规模、教学语言、学费等
├─ ❤️ 学校特色（如有）
│   └─ • 特色1
│       • 特色2
├─ 📝 中一入学信息（仅中学，如有）
│   └─ HTML格式的入学信息内容     ← 优化后
└─ 📞 联络信息
    └─ 地址、电话、邮箱、网站
```

所有section保持统一的样式风格。

## 安全考虑

### XSS防护
虽然使用了 `v-html`，但数据来自：
1. **可信数据源**：数据库中的内容
2. **后端控制**：由管理员维护
3. **不接受用户输入**：非用户生成内容

### 建议的安全措施
如果未来需要接受用户输入的HTML，建议：
1. 后端进行HTML清洗（使用bleach等库）
2. 只允许白名单标签
3. 移除危险属性（onclick, onerror等）
4. 使用DOMPurify等前端库进行二次清洗

## 数据库字段

### 表结构
```sql
-- tb_secondary_schools
admission_info TEXT,  -- 入学信息（支持HTML）
```

### 数据示例
```sql
UPDATE tb_secondary_schools 
SET admission_info = '<p><strong>中一入学信息：</strong></p>
<ul>
  <li>自行分配学位中一收生人数：<strong>180</strong></li>
  <li>统一派位中一收生人数：<strong>180</strong></li>
</ul>'
WHERE school_name = '某某中学';
```

## 后端API

无需修改，`admission_info` 字段原样返回：

```python
# backend/backend/api/schools/secondary_views.py
"admissionInfo": school.admission_info,  # 支持HTML文本
```

## 优势

### 之前（纯文本）
- ❌ 排版单调
- ❌ 无法强调重点
- ❌ 难以组织层次结构
- ❌ 可读性一般

### 现在（HTML支持）
- ✅ 丰富的排版选项
- ✅ 可以强调重点信息
- ✅ 清晰的层次结构（列表、段落）
- ✅ 更好的可读性
- ✅ 与其他内容样式统一

## 使用建议

### 适合使用HTML的场景
1. 需要列表展示的信息
2. 需要强调的重点内容
3. 多段落的长文本
4. 有层次结构的内容

### 简单内容可以纯文本
如果入学信息很简单，也可以继续使用纯文本：
```
中一收生人数：180人
申请截止日期：2024年1月15日
```

## 测试建议

### 测试用例
1. **纯文本** - 确保正常显示
2. **HTML列表** - 检查列表样式
3. **混合内容** - 段落+列表+强调
4. **空内容** - 不显示该section
5. **特殊字符** - HTML实体正确转义

### 兼容性测试
- ✅ Chrome/Safari/Firefox
- ✅ 移动端浏览器
- ✅ 不同屏幕尺寸

## 相关文件

**前端：**
- `frontend/src/components/SchoolDetailModal.vue` - 详情组件

**后端：**
- `backend/backend/api/schools/secondary_views.py` - API
- `backend/backend/models/tb_secondary_schools.py` - 模型

**数据：**
- `backend/common/data/香港各中学信息.xlsx` - 源数据

## 总结

此次优化实现了两个目标：
1. **样式统一**：去除突兀的卡片样式，与整体风格保持一致
2. **HTML支持**：支持富文本格式，提升内容展示的灵活性和可读性

通过 `v-html` 和配套的CSS样式，入学信息现在可以以更加美观和结构化的方式呈现给用户。

