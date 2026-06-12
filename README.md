# 六堡茶智能识别与知识问答系统

基于微信小程序 + FastAPI + YOLOv8 + 通义千问 + BGE/FAISS RAG 的六堡茶智能服务平台。

## 功能模块

| 模块 | 说明 |
|------|------|
| 首页 | 轮播横幅、六堡茶知识卡片、快速提问、季节推荐 |
| AI 病害识别 | 拍照/相册上传，YOLOv8 检测 8 类茶叶病害，自动压缩图片 |
| 智能问答 | RAG 增强 + 通义千问，支持多轮对话，参考来源溯源 |
| 产区地图 | 7 大产区展示、用户定位、地点搜索、路线规划 |
| 知识库 | 7 大分类（14+ 篇文档），向量检索 + 关键词搜索 |
| 品茶日记 | 冲泡记录、5 维评分、风味标签、图片上传 |
| 知识问答 | 65 道题库，随机组卷，实时判分，评级（茶圣/茶师/茶友/茶小白） |
| 茶叶估价 | AI 分析品质、等级与参考价格区间 |
| 茶叶推荐 | 根据口味/预算/目的/健康需求，AI 个性化推荐 |
| 个人中心 | 用户信息编辑、历史记录、收藏管理 |

## 快速启动

### 1. 后端

```bash
pip install -r requirements.txt
copy backend\.env.example backend\.env   # 按需填写 API Key
python run.py
```

后端默认运行在 `http://0.0.0.0:8001`，启动时自动：
- 初始化 SQLite 数据库
- 导入知识库到数据库
- 构建 FAISS 向量索引

默认使用 SQLite（`backend/liubao_tea.db`）。生产环境在 `.env` 中设置：

```env
USE_SQLITE=false
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/liubao_tea?charset=utf8mb4
```

**API 文档**：http://127.0.0.1:8001/docs
**健康检查**：http://127.0.0.1:8001/health

### 2. 微信小程序

1. 用微信开发者工具打开 `miniapp` 目录
2. 修改 `miniapp/utils/config.js` 中 `BASE_URL` 为电脑局域网 IP（真机调试必须使用内网穿透地址）
3. 开发者工具 → 详情 → 本地设置 → 勾选「不校验合法域名」

```js
// miniapp/utils/config.js
const BASE_URL = 'http://127.0.0.1:8001'   // 开发者工具调试
// const BASE_URL = 'http://你的内网穿透地址'  // 真机调试
```

### 3. AI 配置（可选）

| 变量 | 说明 |
|------|------|
| `DASHSCOPE_API_KEY` | 阿里云百炼，启用通义千问（推荐 qwen-plus） |
| `SILICONFLOW_API_KEY` | 硅基流动 BGE 向量嵌入，无则用本地伪向量 |
| `WECHAT_APP_ID` / `WECHAT_APP_SECRET` | 微信小程序登录（无配置时降级为开发模式） |
| `ai_models/yolo/best.pt` | YOLOv8 权重，无则演示模式 |

## 项目结构

```
LiuBaoTreAI/
├── run.py                       # 后端启动脚本
├── requirements.txt
│
├── miniapp/                     # 微信小程序前端（19个页面）
│   ├── pages/
│   │   ├── index/             # 首页
│   │   ├── identify/           # AI 病害识别
│   │   ├── chat/              # 智能问答
│   │   ├── map/               # 产区地图
│   │   ├── profile/           # 个人中心
│   │   ├── knowledge/         # 知识库（列表 + 详情）
│   │   ├── history/           # 历史记录
│   │   ├── favorites/         # 我的收藏
│   │   ├── process/          # 工艺流程
│   │   ├── brew/              # 冲泡指南
│   │   ├── journal/           # 品茶日记（列表 + 编辑）
│   │   ├── quiz/              # 知识问答
│   │   ├── valuation/         # 茶叶估价
│   │   └── recommend/         # 茶叶推荐
│   ├── utils/
│   │   ├── config.js          # API 地址配置
│   │   ├── request.js         # 请求封装
│   │   └── mapService.js      # 腾讯地图 SDK 封装
│   └── app.js / app.json / app.wxss
│
├── backend/                     # FastAPI 后端
│   ├── main.py                # 入口：路由注册、中间件配置、生命周期
│   ├── api/                   # API 路由（12个）
│   │   ├── user.py            # 用户登录/资料
│   │   ├── recognition.py     # 图像识别
│   │   ├── chat.py            # 智能问答
│   │   ├── knowledge.py       # 知识库检索
│   │   ├── history.py         # 历史记录/收藏
│   │   ├── region.py          # 产区信息
│   │   ├── process.py         # 工艺流程
│   │   ├── journal.py         # 品茶日记
│   │   ├── quiz.py            # 知识问答
│   │   ├── valuation.py       # 茶叶估价
│   │   └── recommend.py       # 茶叶推荐
│   ├── models/                # 数据模型（6个 ORM 模型）
│   ├── services/              # 业务逻辑（识别/聊天/知识库）
│   ├── middleware/             # 中间件（限流/日志/异常）
│   ├── database/              # 数据库配置（SQLite/MySQL）
│   └── utils/                 # 工具函数
│
├── ai_models/                  # AI 模型
│   ├── yolo/                  # YOLOv8 识别模型
│   ├── llm/                   # 通义千问客户端
│   └── rag/                   # RAG（向量存储/检索/生成）
│
└── knowledge_base/            # 知识库原文（7大分类）
    ├── history/              # 历史文化
    ├── process/              # 制作工艺
    ├── culture/              # 品鉴文化
    ├── health/               # 健康功效
    ├── brew/                 # 冲泡存储
    ├── grade/                # 等级品鉴
    └── origin/               # 产地分布
```

## 主要 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/user/login | 开发模式登录（直接传 openid） |
| POST | /api/user/login/wechat | 微信登录（传 code 换真实 openid） |
| GET | /api/user/profile | 获取用户资料 |
| PUT | /api/user/profile | 更新用户资料 |
| POST | /api/recognition | 图像病害识别（multipart/form-data） |
| POST | /api/chat | 智能问答（RAG + LLM，支持多轮） |
| GET | /api/knowledge | 知识库列表（支持分类/分页） |
| GET | /api/knowledge/search/query | 搜索知识库（向量 + 模糊降级） |
| GET | /api/knowledge/{id} | 知识详情 |
| GET | /api/history | 历史记录（识别/问答，支持分页） |
| POST | /api/favorite | 添加收藏 |
| GET | /api/favorite | 收藏列表 |
| DELETE | /api/favorite/{id} | 删除收藏 |
| GET | /api/regions | 产区列表（含坐标） |
| GET | /api/process | 工艺流程 |
| POST | /api/journal/upload | 日记图片上传 |
| POST | /api/journal | 创建品茶日记 |
| GET | /api/journal | 日记列表 |
| DELETE | /api/journal/{id} | 删除日记 |
| GET | /api/quiz/questions | 获取随机题目 |
| POST | /api/quiz/judge | 单题判分 |
| POST | /api/quiz/submit | 提交答卷 |
| GET | /api/quiz/history | 答题历史 |
| POST | /api/valuation | AI 茶叶估价 |
| POST | /api/recommend | AI 个性化推荐 |
| GET | /health | 健康检查（含数据库状态） |

## 后端增强特性

- **请求限流**：每用户每分钟 60 次，防止滥用
- **统一日志**：记录路径、方法、耗时、状态码，含请求 ID 追踪
- **全局异常处理**：统一捕获并返回规范错误响应
- **输入验证**：所有参数经过严格验证和 XSS 防护
- **分页支持**：历史/收藏/知识库均支持分页，含 `has_more` 标识
- **知识库缓存**：列表和详情 5 分钟内存缓存
- **AI 重试机制**：LLM 和向量接口均支持指数退避重试（2-3 次）
- **图片压缩**：上传图片自动压缩至 1024px
- **多环境配置**：`.env` 管理所有配置，支持 SQLite/MySQL 切换
- **微信登录校验**：通过微信接口换取真实 openid
- **RAG 降级**：向量搜索失效时自动切换为 SQL 模糊搜索
- **FastAPI Lifespan**：生命周期管理，启动时自动初始化 DB 和 RAG 索引

## 训练 YOLO（病害识别）

当前模型支持检测以下 8 类：
- 茶黑腐病 / 茶褐斑病 / 茶落叶病
- 红蜘蛛危害 / 茶小绿叶蝉危害
- 正常茶叶 / 茶白星病 / 茶叶病害

将数据集放入 `ai_models/yolo/dataset/` 后执行：

```bash
python ai_models/yolo/train.py
```

## 环境变量说明

`.env.example` 中所有配置项：

```env
# 数据库（开发默认 SQLite，生产用 MySQL）
USE_SQLITE=true
SQLITE_URL=sqlite:///./backend/liubao_tea.db

# 阿里云百炼 LLM
DASHSCOPE_API_KEY=your_key_here
QWEN_MODEL=qwen-plus

# 硅基流动向量嵌入
SILICONFLOW_API_KEY=your_key_here
EMBED_MODEL=BAAI/bge-large-zh-v1.5

# 微信小程序登录
WECHAT_APP_ID=wx_your_appid
WECHAT_APP_SECRET=your_secret_here

# 服务配置
HOST=0.0.0.0
PORT=8001
LOG_LEVEL=INFO
```
