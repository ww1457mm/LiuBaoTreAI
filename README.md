# 六堡茶智能识别与知识问答系统

基于微信小程序 + FastAPI + YOLOv8 + 通义千问 + BGE/FAISS RAG 的六堡茶智能服务平台。

## 功能模块

- **首页**：轮播、简介、功能入口
- **AI 识别**：拍照/相册上传，品种/等级/病害识别
- **智能问答**：RAG 增强 + 大模型回答，参考来源溯源
- **知识库**：分类浏览与向量检索
- **个人中心**：用户信息、历史记录、收藏

## 快速启动

### 1. 后端

```bash
cd backend
pip install -r requirements.txt
copy .env.example .env   # 按需填写 API Key
cd ..
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

默认使用 SQLite（`backend/liubao_tea.db`）。生产环境在 `.env` 中设置：

```env
USE_SQLITE=false
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/liubao_tea?charset=utf8mb4
```

API 文档：http://127.0.0.1:8000/docs

### 2. 微信小程序

1. 用微信开发者工具打开 `miniapp` 目录
2. 修改 `miniapp/utils/config.js` 中 `BASE_URL` 为电脑局域网 IP（真机调试不能用 `127.0.0.1`）
3. 开发者工具 → 详情 → 本地设置 → 勾选「不校验合法域名」

### 3. AI 配置（可选）

| 变量 | 说明 |
|------|------|
| `DASHSCOPE_API_KEY` | 阿里云百炼，启用通义千问 |
| `SILICONFLOW_API_KEY` | 硅基流动 BGE 向量 |
| `ai_models/yolo/best.pt` | YOLOv8 权重，无则演示模式 |

首次启动会自动构建 FAISS 索引并导入知识库到数据库。

## 项目结构

```
LiuBaoTeaAI/
├── miniapp/          # 微信小程序
├── backend/          # FastAPI 后端
├── ai_models/        # YOLO / LLM / RAG
├── knowledge_base/   # 知识库原文
└── docs/             # 课程设计文档
```

## 主要 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/recognition | 图像识别 |
| POST | /api/chat | 智能问答 |
| GET | /api/knowledge | 知识库列表 |
| GET | /api/history | 历史记录 |
| POST | /api/user/login | 用户登录 |

## 训练 YOLO

将数据集放入 `ai_models/yolo/dataset/` 后执行：

```bash
python ai_models/yolo/train.py
```

将生成的 `best.pt` 复制到 `ai_models/yolo/best.pt`。
