# 软考中项智能刷题助手 (v3.0 MVP) 项目交接文档

## 📌 一、项目概况与线上地址

- **交付版本**：`v3.0.0-MVP`（对齐第3版新大纲系统集成项目管理工程师 & ruankao-full-prd-v3.md）
- **代码仓库**：[GitHub - sig288/ruankao](https://github.com/sig288/ruankao)
  - **最新 Commit**：`2639456`
  - **主干分支**：`main`
- **线上生产运行环境**：
  - **服务器公网 IP**：`122.51.95.218` (腾讯云 Ubuntu 22.04 LTS)
  - **学员端 H5 / Web 入口**：`https://122.51.95.218/ruankao/`
  - **后端 OpenAPI 接口文档**：`https://122.51.95.218/api/docs`
  - **运行容器**：
    - `ruankao-frontend`：Vue 3 + Vite + TailwindCSS (宿主端口 8090，反向代理至 443 `/ruankao/`)
    - `ruankao-backend`：FastAPI + SQLAlchemy + SQLite (宿主端口 8000，反向代理至 443 `/api/`)
- **内置测试账号**：
  - 学员账号：`student_2026` / `Password123!`
  - 管理员账号：`admin` / `Admin123!`
  - 外部 Agent 测试密钥：`rk-live-agent-key-2026`

---

## 🚀 二、核心功能交付清单

### 1. P0 核心能力 (全部上线通过验证)
- **M4 考点掌握度画像与诊断 (`GET /api/v1/mastery/me`)**：
  - 支持 **17 章教材章节** 与 **十大管理领域** 双重视角自由切换。
  - 动态计算备考就绪度综合分（0~100）、近 30 天做题正确率、全书考点覆盖率、7 日刷题趋势。
  - 自动标定低于 60% 正确率或存在未消灭错题的知识点为 `weak`（薄弱标红）。
- **M5 薄弱点精准靶向突击 (`POST /api/v1/mastery/weak-drill`)**：
  - 算法靶向组卷：自动提取未掌握错题（占比 <=40%）与弱势章节真题（占比 >=60%）。
  - 支持在首页、错题本、掌握度看板一键唤起专项练习。
- **A1~A3 DeepSeek AI 伴学助教 (`POST /api/v1/ai/jobs`)**：
  - **A1 白话精讲**：大白话拆解难懂的考点概念（如 EVM、CCB、配置基线）。
  - **A2 速记口诀**：输出押韵口诀与考场秒杀技巧。
  - **A3 案例拆解**：针对案例计算大题逐步剖析公式、踩分点与陷阱。
  - **安全与降级**：客户端免配 Key，每日 30 次防刷额度；无网络或接口超时时自动触发高质量预置离线模板。
- **M7 移动端触控优化与触感反馈**：
  - 专为 vivo X300 Pro (430px) 进行全屏适配。
  - 44pt 最小手指触控热区、左右滑动手势切题 (`touchstart`/`touchend`)。
  - 基于 HTML5 Web Vibration API 实现做题触感反馈（轻微触击、答对微震、答错双震、过关震动）。
- **M6 Android APK 壳工程准备**：
  - 已初始化 Capacitor 6 原生 Android 工程 (`frontend/android/`)。
  - 集成 Gradle 8.14.3 与 Java 17，可随时通过 Android Studio 打包离线 APK。

### 2. P1 扩展能力 (已完成)
- **M1 私有学习资料库 (`POST /api/v1/materials`)**：
  - 支持上传教材、讲义、口诀、案例及题库表（PDF、Word、Markdown、CSV、TXT）。
  - 分类归档检索，服务器挂载卷物理隔离存储。
- **M2 自有题库一键转换桥接 (`POST /api/v1/materials/{id}/convert-questions`)**：
  - 支持上传的 CSV/JSON 格式私有题目批量解析入库，直接转换为可刷题目。
- **M3 14天倒计时备考计划 (`GET /api/v1/plan/me`)**：
  - 自动倒计时展示、每日打卡清单动态分配、自定义每日备考时长。

### 3. B1~B8 基线能力 (稳定运行)
- 题库规模扩充至 **138 道第3版官方教程与机考真题**（134 道单选 + 4 道案例大题）。
- 75 题全卷模拟考、倒计时、交卷即时判分与防窥视答案保护。
- 案例分析题自动计算关键词踩分（甘特图、关键路径、EVM 挣值分析）。
- 外部 Agent 错题互联 OpenAPI（支持批量读取错题与写入解析）。

---

## 🛠️ 三、技术架构与目录指引

```
ruankao/
├── backend/                  # 后端 FastAPI 源码
│   ├── app/
│   │   ├── api/v1/          # API 路由层 (mastery, ai, materials, study_plan, auth, exam...)
│   │   ├── core/            # 核心配置 (config.py, security.py)
│   │   ├── models/          # ORM 数据模型 (ai_job, material, study_plan, wrong_question...)
│   │   ├── schemas/         # Pydantic 数据验证契约
│   │   └── services/        # 题目种子加载与转换逻辑
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # 前端 Vue 3 + Vite 源码
│   ├── android/             # Capacitor Android 原生壳工程
│   ├── src/
│   │   ├── api/             # 前端 Axios 接口统一封装 (masteryApi, aiApi, materialsApi, planApi)
│   │   ├── components/      # 组件库 (AiAssistPanel.vue)
│   │   ├── utils/           # 工具库 (haptics.ts 震动反馈)
│   │   ├── views/           # 视图页面 (Home, Statistics, MaterialsView, StudyPlanView, WrongQuestions...)
│   │   └── router/          # 路由表
│   ├── capacitor.config.json
│   └── package.json
├── docker-compose.yml        # 生产编排文件
└── HANDOVER.md              # 本交接文档
```

---

## 💻 四、常用运维与开发操作

### 1. 本地启动开发
```powershell
# 1. 启动后端
cd E:\code\ruankao\backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 2. 启动前端
cd E:\code\ruankao\frontend
npm install
npm run dev
```

### 2. 生产环境更新部署 (腾讯云 VPS)
```bash
# 登录 VPS
ssh -i C:\Users\sig28.SIG289\.ssh\id_ed25519 ubuntu@122.51.95.218

# 进入部署目录并拉取/更新
cd /home/ubuntu/ruankao
sudo docker compose build ruankao-backend ruankao-frontend
sudo docker compose up -d

# 查看运行日志
sudo docker logs -f ruankao-backend
```

### 3. 构建 Android APK
```powershell
cd E:\code\ruankao\frontend
npm run build
npx cap sync android
# 打开 Android Studio，打开 frontend/android 目录，点击 Build -> Build Bundle(s) / APK(s) -> Build APK(s)
```

---

## 🔒 五、安全及合规承诺

1. **零密钥泄露**：Git 仓库未提交任何生产服务器密码、私钥、云鉴权密匙或第三方 API 密钥。
2. **版权与资料保护**：本地 `学习资料/` 原始教材持续受 `.gitignore` 规则严密过滤，绝不进入版本库。
3. **同机服务共存**：完全不干扰同 VPS 运行的 `debate-agents` 与 `energy-ledger` 等已有服务的端口与证书。
