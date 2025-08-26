# API 接口文档

## 概述

前端应用需要以下API接口来获取学校数据。默认情况下，前端会启用Mock模式使用静态数据，当后端接口可用时可以切换到真实API。

## 基础配置

- **API基础地址**: `http://localhost:8080/api`
- **请求格式**: JSON
- **响应格式**: JSON
- **编码**: UTF-8

## 通用响应格式

所有API接口都应返回以下格式的响应：

```typescript
interface ApiResponse<T> {
  code: number         // 状态码：200=成功，400=客户端错误，500=服务器错误
  message: string      // 响应消息
  data: T             // 响应数据
  success: boolean    // 是否成功
}
```

### 成功响应示例
```json
{
  "code": 200,
  "message": "成功",
  "data": { ... },
  "success": true
}
```

### 错误响应示例
```json
{
  "code": 400,
  "message": "参数错误",
  "data": null,
  "success": false
}
```

## 数据模型

### School（学校信息）
```typescript
interface School {
  id: number                                    // 学校ID
  name: string                                  // 学校名称
  type: 'primary' | 'secondary'                // 学校类型：小学/中学
  category: 'elite' | 'traditional' | 'direct' | 'government'  // 学校分类
  band1Rate: number                            // Band1比例（0-100）
  applicationStatus: 'open' | 'closed' | 'deadline'  // 申请状态
  district: string                             // 地区
  schoolNet: string                            // 校网
  tuition: number                              // 学费（年费，单位：港币）
  gender: 'coed' | 'boys' | 'girls'           // 男女校类型
  feederSchools: string[]                      // 衔接小学列表
  linkedUniversities: string[]                 // 衔接大学列表
  image?: string                               // 学校图片URL（可选）
}
```

### SchoolStats（学校统计）
```typescript
interface SchoolStats {
  totalSchools: number      // 学校总数
  openApplications: number  // 开放申请的学校数量
}
```

### PageData（分页数据）
```typescript
interface PageData<T> {
  list: T[]           // 数据列表
  total: number       // 总记录数
  page: number        // 当前页码
  pageSize: number    // 每页大小
  totalPages: number  // 总页数
}
```

## API 接口

### 1. 获取学校列表

**接口地址**: `GET /api/schools`

**查询参数**:
```typescript
interface PageQuery {
  page?: number                                // 页码，默认1
  pageSize?: number                           // 每页大小，默认20
  type?: 'primary' | 'secondary'             // 学校类型筛选
  category?: 'elite' | 'traditional' | 'direct' | 'government'  // 分类筛选
  district?: string                           // 地区筛选
  applicationStatus?: 'open' | 'closed' | 'deadline'  // 申请状态筛选
  keyword?: string                            // 搜索关键词（学校名称、地区）
}
```

**请求示例**:
```
GET /api/schools?type=secondary&page=1&pageSize=10
```

**响应示例**:
```json
{
  "code": 200,
  "message": "成功",
  "success": true,
  "data": {
    "list": [
      {
        "id": 1,
        "name": "圣保罗男女中学",
        "type": "secondary",
        "category": "elite",
        "band1Rate": 94,
        "applicationStatus": "open",
        "district": "中西区",
        "schoolNet": "校网11",
        "tuition": 36800,
        "gender": "coed",
        "feederSchools": ["圣保罗书院"],
        "linkedUniversities": ["香港大学"]
      }
    ],
    "total": 68,
    "page": 1,
    "pageSize": 10,
    "totalPages": 7
  }
}
```

### 2. 获取学校详情

**接口地址**: `GET /api/schools/{id}`

**路径参数**:
- `id`: 学校ID

**请求示例**:
```
GET /api/schools/1
```

**响应示例**:
```json
{
  "code": 200,
  "message": "成功",
  "success": true,
  "data": {
    "id": 1,
    "name": "圣保罗男女中学",
    "type": "secondary",
    "category": "elite",
    "band1Rate": 94,
    "applicationStatus": "open",
    "district": "中西区",
    "schoolNet": "校网11",
    "tuition": 36800,
    "gender": "coed",
    "feederSchools": ["圣保罗书院"],
    "linkedUniversities": ["香港大学"],
    "image": "https://example.com/school1.jpg"
  }
}
```

### 3. 获取学校统计信息

**接口地址**: `GET /api/schools/stats`

**查询参数**:
- `type?: 'primary' | 'secondary'` - 学校类型，可选

**请求示例**:
```
GET /api/schools/stats?type=secondary
```

**响应示例**:
```json
{
  "code": 200,
  "message": "成功",
  "success": true,
  "data": {
    "totalSchools": 3,
    "openApplications": 2
  }
}
```

## 错误处理

### 常见错误代码

- `400` - 请求参数错误
- `404` - 资源不存在
- `500` - 服务器内部错误
- `503` - 服务不可用

### 错误响应示例

```json
{
  "code": 404,
  "message": "学校不存在",
  "success": false,
  "data": null
}
```

## 开发说明

### 前端Mock模式

前端默认启用Mock模式，使用内置的静态数据。当后端接口可用时：

1. 设置环境变量 `VITE_ENABLE_MOCK=false`
2. 确保后端API地址正确配置在 `VITE_API_BASE_URL`

### 测试数据

建议在后端实现这些测试数据，与前端Mock数据保持一致：

**中学数据**：
- 圣保罗男女中学（名校联盟，94% Band1，开放申请）
- 喇沙书院（传统名校，88% Band1，申请截止）
- 拔萃女书院（直资学校，96% Band1，开放申请）

**小学数据**：
- 拔萃女小学（直资学校，98% Band1，开放申请）
- 圣保罗男女中学附属小学（名校联盟，95% Band1，开放申请）
- 喇沙小学（传统名校，92% Band1，申请截止）

### CORS配置

后端需要配置CORS以允许前端访问：

```javascript
// Express.js 示例
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:5173'],
  credentials: true
}))
```

## 前端使用示例

```typescript
// 获取中学列表
const response = await schoolApi.getByType('secondary')

// 搜索学校
const results = await schoolApi.search('圣保罗')

// 获取统计信息
const stats = await schoolApi.getStats('primary')
``` 