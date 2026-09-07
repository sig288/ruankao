# 软考中项（系统集成项目管理工程师 第3版）刷题助手

面向**系统集成项目管理工程师（软考中级·第3版新大纲）**打造的移动端优先全栈刷题系统。
支持手机浏览器 PWA 安装至主屏（针对 vivo X300 Pro 等现代机型优化），支持 Capacitor 一键打包 Android APK，并内置**外部 AI 智能体错题协同 API**。

---

## 一、核心功能特性

1. **两科学员全覆盖**：
   - **科目一：基础知识**（75道单选题，涵盖十大知识领域、法律法规、信息化基础）
   - **科目二：应用技术**（案例分析大题，含挣值计算、关键路径计算、问答半自动关键词采分）
2. **移动优先交互体验**：
   - 适配手机单手操作布局与底部导航栏，答题卡快速跳转
   - PWA 支持：可在手机 Chrome / vivo 浏览器中点击「添加到主屏幕」，秒变原生级独立 App
   - 随身离线题库模式与即时考点解析
3. **全流程备考闭环**：
   - **章节专项练**：按十大领域分步突破
   - **全真机考模拟**：带倒计时与答题卡，提交即出成绩单
   - **案例智能采分**：结合官方得分点与采分关键词半自动评分并给出参考要点
   - **错题本与掌握度统计**：错题自动沉淀、按掌握状态攻坚、雷达图维度诊断
4. **【核心】外部 AI 智能体错题开放生态**：
   - 独立 Agent API Key 认证（与用户会话隔离）
   - 支持 Agent 批量拉取错题、查询单题、回写 AI 深度剖析与记忆锦囊
   - 提供标准 OpenAPI 交互文档：`/api/docs`

---

## 二、生产部署指南

### 2.1 服务器环境要求
- 系统：Ubuntu 20.04 / 22.04 LTS 或任何支持 Docker 的 Linux 发行版
- 工具：Docker & Docker Compose

### 2.2 配置与启动
1. 复制环境变量模板并设置强密码：
   ```bash
   cp .env.example .env
   # 编辑 .env 修改 SECRET_KEY、INITIAL_ADMIN_PASSWORD 与 DEFAULT_AGENT_KEY
   ```

2. 一键启动容器集群：
   ```bash
   docker compose up -d --build
   ```

系统将自动构建并启动以下容器：
- `ruankao-backend`: Python FastAPI 核心服务（内置 SQLite 持久化与题库种子自动加载）
- `ruankao-frontend`: Nginx 高性能 Web 服务器（静态托管 + API 反代，对外映射 **8090** 端口）

启动后，访问地址：
- **Web 访问地址**：`http://<YOUR_SERVER_IP>:8090` 或配置反代域名
- **OpenAPI / Swagger 接口文档**：`http://<YOUR_SERVER_IP>:8090/api/docs`

---

## 三、快速开始与操作指引

### 3.1 首次登录与管理员账号
- 系统在首次启动时会自动根据 `.env` 中的配置创建初始管理员账号；
- 也可在登录页面直接注册新账号，首位注册用户将获得管理员角色；
- 登录后可在个人中心随时修改密码。

### 3.2 生成与管理 Agent API Key
1. 使用管理员账号登录，点击右上角「管理后台」；
2. 在「外部 Agent 错题 API Key 管理」区域，输入标识名称（例如：`软考助手Agent`），点击「生成新 Key」；
3. 复制生成的专属密钥（形如 `rk_agent_xxxxxx`）。

### 3.3 外部 Agent 错题接口调用示例

#### 1) Agent 拉取用户错题列表
```bash
curl -H "Authorization: Bearer <YOUR_AGENT_KEY>" \
  "http://<YOUR_SERVER_IP>:8090/api/v1/agent/wrong-questions?limit=10"
```

#### 2) Agent 查询单题详情
```bash
curl -H "Authorization: Bearer <YOUR_AGENT_KEY>" \
  "http://<YOUR_SERVER_IP>:8090/api/v1/agent/wrong-questions/wq_xxx"
```

#### 3) Agent 批量推送错题
```bash
curl -X POST \
  -H "Authorization: Bearer <YOUR_AGENT_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "user_id": "u_test",
        "question_id": "q_test",
        "subject": "basic",
        "knowledge": "挣值分析EVM",
        "stem": "某项目EV=80万，AC=100万，求CV指标？",
        "options": ["A. -20万", "B. 20万", "C. 0.8", "D. 1.25"],
        "correct_answer": "A",
        "user_answer": "B",
        "analysis": "CV=EV-AC=80-100=-20万元",
        "source": "ai-generated"
      }
    ]
  }' \
  "http://<YOUR_SERVER_IP>:8090/api/v1/agent/wrong-questions"
```

#### 4) Agent 写回深度讲解与答题锦囊（在错题本中高亮展示）
```bash
curl -X POST \
  -H "Authorization: Bearer <YOUR_AGENT_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "wrong_question_id": "wq_xxx",
    "explanation": "此题考查挣值管理基本指标。CV=EV-AC，当EV小于AC时差值为负，代表成本超支。",
    "study_tips": "【记忆口诀】EV始终在前面，减负超支减正节约；除大于1效率高。"
  }' \
  "http://<YOUR_SERVER_IP>:8090/api/v1/agent/explain-callback"
```

---

## 四、AI 出题流水线与题库导入

1. 查阅 `prompts/question_generation_prompt.md`；
2. 将提示词发给大模型，按章节批量输出符合 Schema 的纯自编 JSON 题库；
3. 进入系统「管理后台」->「批量导入题库」，直接粘贴 JSON 数组，点击执行导入。

---

## 五、打包 Android APK（Capacitor 方案）

本项目前端基于标准 Web 响应式架构，已完整配置 Capacitor 配置 `capacitor.config.json`。
如需打包在 vivo X300 Pro 等 Android 手机上安装：

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖并构建最新前端产物
npm install
npm run build:fast

# 3. 安装 Capacitor CLI 与 Android 平台支持
npm install @capacitor/core @capacitor/cli @capacitor/android

# 4. 初始化与同步 Android 项目
npx cap add android
npx cap sync

# 5. 打开 Android Studio 并构建 APK
npx cap open android
```
在打开的 Android Studio 中，点击 `Build` -> `Build Bundle(s) / APK(s)` -> `Build APK(s)`，即可在 `android/app/build/outputs/apk/debug/` 目录下获取可直接安装的 `app-debug.apk`。

> **免打包提示**：在手机 Chrome 或自带浏览器直接访问部署地址，点击浏览器菜单「添加到主屏幕」，即可获得与原生 APK 几无差异的无边框独立应用体验！
