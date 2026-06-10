# 六堡茶智能识别与知识问答系统

基于微信小程序 + FastAPI + YOLOv8 + 通义千问 + BGE/FAISS RAG 的六堡茶智能服务平台。

## 功能模块

- **首页**：轮播横幅、六堡茶简介、核心功能入口
- **AI 病害识别**：拍照/相册上传，智能检测霉变、虫蛀、菌类异常等可见缺陷，支持图片自动压缩
- **智能问答**：RAG 增强 + 大模型回答，参考来源溯源，支持多轮对话
- **知识库**：7 大分类（历史文化/制作工艺/品鉴文化/健康功效/冲泡存储/等级品鉴/产地分布），支持向量检索和关键词搜索
- **个人中心**：用户信息编辑、历史记录、收藏管理

## 快速启动

### 1. 后端

```bash
pip install -r requirements.txt
copy backend\.env.example backend\.env   # 按需填写 API Key
python run.py
```

默认使用 SQLite（`backend/liubao_tea.db`）。生产环境在 `.env` 中设置：

```env
USE_SQLITE=false
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/liubao_tea?charset=utf8mb4
```

API 文档：http://127.0.0.1:8001/docs
健康检查：http://127.0.0.1:8001/health

### 2. 微信小程序

1. 用微信开发者工具打开 `miniapp` 目录
2. 修改 `miniapp/utils/config.js` 中 `BASE_URL` 为电脑局域网 IP（真机调试不能用 `127.0.0.1`）
3. 开发者工具 → 详情 → 本地设置 → 勾选「不校验合法域名」

### 3. AI 配置（可选）

| 变量 | 说明 |
|------|------|
| `DASHSCOPE_API_KEY` | 阿里云百炼，启用通义千问（推荐 qwen-plus） |
| `SILICONFLOW_API_KEY` | 硅基流动 BGE 向量嵌入，无则用本地伪向量 |
| `WECHAT_APP_ID` / `WECHAT_APP_SECRET` | 微信小程序登录（无配置时降级为开发模式） |
| `ai_models/yolo/best.pt` | YOLOv8 权重，无则演示模式 |

首次启动会自动构建 FAISS 索引并导入知识库到数据库。

## 项目结构

```
LiuBaoTreAI/
├── miniapp/                # 微信小程序前端
│   ├── pages/
│   │   ├── index/         # 首页
│   │   ├── identify/      # AI 识别
│   │   ├── chat/          # 智能问答
│   │   ├── knowledge/      # 知识库（列表 + 详情）
│   │   ├── history/       # 历史记录
│   │   └── profile/        # 个人中心
│   └── utils/
│       ├── config.js       # API 地址配置
│       └── request.js      # 请求封装
├── backend/                # FastAPI 后端
│   ├── api/               # API 路由（user/chat/recognition/knowledge/history）
│   ├── middleware/        # 中间件（限流、日志、异常处理）
│   ├── models/            # 数据模型（SQLAlchemy ORM）
│   ├── services/          # 业务逻辑（识别/聊天/知识库服务）
│   ├── utils/             # 工具函数（验证器、日志、微信登录）
│   └── database/          # 数据库配置（SQLite/MySQL）
├── ai_models/              # AI 模型
│   ├── yolo/              # YOLOv8 识别模型
│   ├── llm/               # 通义千问客户端（重试机制）
│   └── rag/               # RAG（向量存储/检索/生成）
├── knowledge_base/          # 知识库原文（按分类组织）
│   ├── history/           # 历史文化
│   ├── process/           # 制作工艺
│   ├── culture/           # 品鉴文化
│   ├── health/           # 健康功效
│   ├── brew/             # 冲泡存储
│   ├── grade/            # 等级品鉴
│   └── origin/           # 产地分布
```

## 主要 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/user/login | 开发模式登录（直接传 openid） |
| POST | /api/user/login/wechat | 微信登录（传 code 换真实 openid） |
| GET | /api/user/profile | 获取用户资料 |
| PUT | /api/user/profile | 更新用户资料（昵称/头像） |
| POST | /api/recognition | 图像病害识别（检测霉变、虫蛀等缺陷） |
| POST | /api/chat | 智能问答（RAG + LLM） |
| GET | /api/knowledge | 知识库列表（支持分类、分页） |
| GET | /api/knowledge/search/query | 向量搜索知识库 |
| GET | /api/knowledge/{id} | 知识详情 |
| GET | /api/history | 历史记录（识别/问答，支持分页） |
| POST | /api/favorite | 添加收藏 |
| GET | /api/favorite | 收藏列表（支持分页） |
| DELETE | /api/favorite/{id} | 删除收藏 |
| GET | /health | 健康检查（含数据库连接状态） |

## 后端增强特性

- **请求限流**：每用户每分钟最多 60 次请求，防止滥用
- **统一日志**：记录所有请求的路径、方法、耗时和状态码，含请求 ID 追踪
- **全局异常处理**：统一捕获并返回规范错误响应，含请求 ID 便于排查
- **输入验证**：所有 API 参数经过严格验证和清理（XSS 防护、类型校验）
- **分页支持**：历史记录、收藏列表、知识库均支持分页，含 has_more 标识
- **知识库缓存**：知识列表和详情 5 分钟内存缓存，加速访问
- **AI 重试机制**：LLM 和向量接口均支持指数退避重试（2-3 次）
- **图片压缩**：上传图片自动压缩至 1024px，节省存储和推理时间
- **多环境配置**：`.env` 管理所有配置项，支持 SQLite/MySQL 切换
- **微信登录校验**：通过微信接口换取真实 openid，防止伪造身份
- **FastAPI Lifespan**：现代化生命周期管理，替代废弃的 on_event

## 训练 YOLO（病害识别）

当前模型支持检测以下病害类别：
- 毛虫危害（maochong）
- 霉变污染（meibian）
- 菌类异常（junlei）
- 茶果混入（chaguo）
- 箬叶残留（ruoye）

将数据集放入 `ai_models/yolo/dataset/` 后执行：

```bash
python ai_models/yolo/train.py
```

## 环境变量说明

`.env.example` 中所有配置项的说明：

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
PORT=8000
LOG_LEVEL=INFO
```
