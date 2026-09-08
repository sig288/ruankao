# 软考中项刷题助手 · 知识点学习 & 英语术语词表 PRD

| 项 | 内容 |
|----|------|
| 产品 | 软考中项智能刷题助手（已部署 https://122.51.95.218/ruankao/） |
| 文档 | PRD-LEARN-GLOSSARY v1.0 |
| 日期 | 2026-09-07 |
| 大纲 | 系统集成项目管理工程师 第3版 |
| 终端 | 手机优先（vivo X300 Pro / 430px 验证） |
| 内容原则 | 讲义与词表**自编**；不粘贴受版权教材原文 / 真题全文 |
| 关联 | 对齐现网 v3.0 MVP（掌握度/错题/AI/资料等）；本需求为增量 |

---

## 1. 问题 / 目标用户 / 成功指标

### 1.1 问题
1. 学员只会刷题，缺少「章→知识点」结构化学习路径，错题后不知道回哪一节巩固。
2. 基础知识卷末约 5 道英语术语题（约 5 分）长期被忽略，词表若放后续迭代会丢分。

### 1.2 目标用户
备考中项的在职 IT 学员；碎片化手机学习；已有刷题/模考/错题习惯。

### 1.3 目标
- **功能 A（MVP）**：可浏览知识树与知识点详情，记录学习状态，与解析页/错题本双向打通，后台可 JSON 导入。
- **功能 B（本期 P1，紧随 MVP）**：高频英语术语词表可刷、可标记、可从英语题解析跳转；种子 ≥80 词。

### 1.4 成功指标（上线 2 周内看）
| 指标 | 目标（建议） |
|------|----------------|
| 知识点详情 UV / 活跃学员 | ≥ 40% 活跃学员点开过 |
| 「去巩固」点击后完成练习 | ≥ 50% 有后续作答 |
| 词表有标记（会/不会/收藏）的学员 | ≥ 25% 活跃学员 |
| 英语相关错题 → 词表跳转可用率 | 100%（有关联的题） |

### 1.5 明确暂缓
AI 小课、闪卡间隔重复（SRS）、音视频、打卡日历（词表 10 词小测除外）。

---

## 2. 用户故事与验收标准

### 2.1 功能 A：知识点学习（MVP）

| ID | 用户故事 | 验收标准 |
|----|----------|----------|
| A-US1 | 作为学员，我能按「章→知识点卡片」浏览知识树，看到考频与预计时长 | 手机可展开 17 章；卡片含标题、考频高/中/低、预计时长；空章有占位文案 |
| A-US2 | 作为学员，我能打开知识点详情看要点、公式/口诀，并进入相关例题 | 详情 Markdown 渲染正常；有公式/口诀区块（可空）；「相关例题」默认拉 5 题可练 |
| A-US3 | 作为学员，我能把状态设为未学/学习中/已掌握 | 三态切换即时保存；刷新后保持；列表可用状态筛选或角标 |
| A-US4 | 作为学员，我能看到章节完成度与最近学习 | 章节完成度 = 已掌握数/该章知识点数；「最近学习」至少 5 条，按时间倒序 |
| A-US5 | 作为学员，我从题目解析可跳到关联知识点 | 解析页有知识点入口（有关联才显示）；点击进入对应详情 |
| A-US6 | 作为学员，我能在错题本按知识点筛选，并「去巩固」 | 错题本支持按知识点筛选；「去巩固」进入该知识点例题练习（或薄弱组卷含该点） |
| A-US7 | 作为运营/管理员，我能 JSON 导入/编辑知识点，种子覆盖核心域 | 后台或管理 API 导入后，学员端列表可见；种子至少覆盖：挣值、进度、变更、招投标、十大领域等 |

### 2.2 功能 B：英语术语词表（P1）

| ID | 用户故事 | 验收标准 |
|----|----------|----------|
| B-US1 | 作为学员，我能浏览词表（英/中/领域标签/考频） | 列表可搜、可按标签筛；字段齐全；手机滑动流畅 |
| B-US2 | 作为学员，我能看词卡详情（释义、考点提示、易混词） | 详情页完整；无易混词时不报错 |
| B-US3 | 作为学员，我能收藏、标记已会/不会 | 状态持久化；列表可筛「不会」「收藏」 |
| B-US4 | 作为学员，我能进行「看英文选中文」小测（10 词一组） | 一组 10 题；交卷出对错与释义回顾；不影响正式模考分 |
| B-US5 | 作为学员，我从英语题解析可跳到对应词条 | 有关联的英语练习/解析显示词表入口并可跳转 |
| B-US6 | 作为学员，我在知识点详情能看到相关术语 | 知识点可挂 term_id 列表；无则隐藏区块 |
| B-US7 | 作为运营，我能 CSV/JSON 导入词表，且至少 80 个高频种子词可查 | 导入字段见 §4；线上可查词条 ≥80 |

---

## 3. 信息架构与关键页面

### 3.1 信息架构（增量）
```
首页
 └─ 学习（新一级入口，或「备考」下）
     ├─ 知识点（知识树）
     │    └─ 知识点详情
     │         ├─ 要点 / 公式口诀
     │         ├─ 相关术语（B）
     │         └─ 相关例题（默认5）
     └─ 英语词表（B）
          ├─ 词表列表
          ├─ 词卡详情
          └─ 小测（10词）

刷题/解析页 ──跳转──► 知识点详情 / 词卡详情
错题本 ──筛选/去巩固──► 知识点例题
掌握度（已有）──可后续链到知识点（本期可选，非必须）
```

### 3.2 关键页面
| 页面 | 路径建议 | 说明 |
|------|----------|------|
| 知识树 | `/learn/points` | 章手风琴 + 卡片列表 |
| 知识点详情 | `/learn/points/:id` | Markdown + 状态 + 例题 + 术语 |
| 词表列表 | `/learn/glossary` | 搜索/标签/掌握筛选 |
| 词卡详情 | `/learn/glossary/:id` | 释义/提示/易混/收藏 |
| 词表小测 | `/learn/glossary/quiz` | 10 词一组 |
| 管理导入 | 管理端或脚本 | JSON/CSV；可先 API + 文档 |

### 3.3 打通点（必须）
1. `QuestionExplain`：`knowledge_point_ids[]`、`glossary_ids[]`（英语题）  
2. 错题本：知识点筛选 + CTA「去巩固」  
3. 知识点详情：相关例题 `GET .../practice`；相关术语  

---

## 4. 数据模型字段表

### 4.1 knowledge_chapters（可复用现有章节表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | str/int | PK |
| code | str | 章编码，如 CH07 |
| title | str | 章名 |
| sort_order | int | 排序 |

### 4.2 knowledge_points
| 字段 | 类型 | 说明 |
|------|------|------|
| id | str | PK，如 `kp_evm_cpi` |
| chapter_id | FK | 所属章 |
| title | str | 知识点标题 |
| frequency | enum | `high` / `mid` / `low` |
| est_minutes | int | 预计学习时长（分钟） |
| summary_md | text | 要点 Markdown（自编） |
| formula_md | text | 公式/口诀 Markdown，可空 |
| domain_tags | json | 十大领域等标签 |
| glossary_ids | json | 关联词条 id 列表 |
| question_ids | json | 关联例题 id（或用关系表） |
| sort_order | int | 章内排序 |
| updated_at | datetime | |

### 4.3 user_knowledge_point_status
| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | FK | |
| point_id | FK | |
| status | enum | `unlearned` / `learning` / `mastered` |
| last_studied_at | datetime | |
| updated_at | datetime | |

### 4.4 glossary_terms
| 字段 | 类型 | 说明 |
|------|------|------|
| id | str | PK |
| term_en | str | 英文术语 |
| term_zh | str | 中文释义 |
| tags | json | 领域标签 |
| tip | text | 一句考点提示/例句（自编） |
| frequency | enum | `high` / `mid` / `low` |
| confuse_with | json | 易混词 id 或英文列表 |
| knowledge_point_ids | json | 反向关联，可空 |
| updated_at | datetime | |

### 4.5 user_glossary_status
| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | FK | |
| term_id | FK | |
| known | enum | `unknown` / `know` / `dont_know`（或 bool+枚举） |
| favorited | bool | 默认 false |
| updated_at | datetime | |

### 4.6 题目扩展（最小）
| 字段 | 说明 |
|------|------|
| knowledge_point_ids | 解析跳转用 |
| glossary_ids | 英语题跳转用 |
| is_english_term | 可选标记，便于筛英语题 |

### 4.7 导入约定
**知识点 JSON 示例字段**：`id, chapter_id, title, frequency, est_minutes, summary_md, formula_md, domain_tags, glossary_ids, question_ids, sort_order`  
**词表 CSV/JSON**：`term_en, term_zh, tags, tip, frequency`（可选 `id, confuse_with, knowledge_point_ids`）

---

## 5. API 列表

> 前缀：`/api/v1`；鉴权：学员 Bearer；管理导入可 admin 或独立 script + admin token。

### 5.1 知识点（MVP）
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/learn/chapters` | 章列表 + 每章点数/完成度（可选嵌套） |
| GET | `/learn/points` | 知识点列表；query: `chapter_id`, `status` |
| GET | `/learn/points/{id}` | 详情（含用户状态、关联术语摘要） |
| POST | `/learn/points/{id}/status` | body: `{ "status": "learning\|mastered\|unlearned" }` |
| GET | `/learn/points/{id}/practice` | 相关例题，默认 `limit=5` |
| GET | `/learn/progress` | 章节完成度 + 最近学习 |
| POST | `/admin/learn/points/import` | JSON 批量导入/更新（upsert） |
| GET | `/agent/weak-points` | **可选**；结合错题+未掌握知识点给外部 Agent |

### 5.2 词表（P1）
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/learn/glossary` | 列表；query: `q`, `tag`, `known`, `favorited` |
| GET | `/learn/glossary/{id}` | 详情 |
| POST | `/learn/glossary/{id}/status` | `{ "known": "...", "favorited": true }` |
| POST | `/learn/glossary/quiz` | 抽 10 词（可指定 tag） |
| POST | `/learn/glossary/quiz/submit` | 提交选项，返回对错与解析 |
| POST | `/admin/learn/glossary/import` | CSV/JSON 导入 |

### 5.3 响应约定（节选）
- 列表统一分页：`items`, `total`, `page`, `page_size`  
- 状态类 POST 返回更新后实体  
- 404/403 明确；导入返回 `{ inserted, updated, errors[] }`

---

## 6. MVP vs P1 排期建议

| 批次 | 范围 | 影响面 | 成本感 | 理由 |
|------|------|--------|--------|------|
| **MVP（先做）** | 知识树、详情、状态、进度、解析/错题打通、JSON 种子导入、例题 practice | 中：新 IA + 错题/解析改动 | 中（3～5 人日量级，视种子量） | 巩固闭环直接提分；承接错题本 |
| **P1（紧随）** | 词表 CRUD 展示、状态/收藏、小测、英语解析跳转、知识点挂术语、≥80 词种子 | 中低：相对独立模块 + 解析挂链 | 低～中（2～4 人日） | 卷末约 5 分；与知识点并行设计、串行上线即可 |
| **暂缓** | AI 小课、SRS 闪卡、音视频、打卡日历 | — | — | 用户明确不做 |

**建议序**  
1. 数据模型 + 知识点 API + 种子（挣值/进度/变更/招投标/十大领域）  
2. 前端知识树/详情/进度 + 解析/错题打通  
3. 词表模型 + 导入 80～150 词 + 列表/详情/状态  
4. 小测 + 英语题/知识点挂链  

**依赖**  
- 例题关联依赖现有题库 id；无题时详情仍可学，例题区显示「暂无例题」。  
- 不阻塞 Android 壳；H5/PWA 先验收，Capacitor 同步即可。

---

## 7. 给研发的一页实现备注（可贴 Antigravity）

```text
【增量需求】知识点学习(MVP) + 英语词表(P1) @ ruankao (122.51.95.218)
对齐：手机优先；内容自编讲义/词表，禁止粘贴版权教材原文与真题全文。

MVP 必达
1) 知识树 章→卡片(title/frequency/est_minutes)
2) 详情：summary_md + formula_md + 状态三态 + practice 默认5题
3) GET progress：章节完成度 + 最近学习
4) 解析页知识点跳转；错题本按知识点筛选 +「去巩固」
5) Admin JSON upsert 导入；种子覆盖挣值/进度/变更/招投标/十大领域
API：GET /api/v1/learn/chapters|points|points/{id}|points/{id}/practice|progress
     POST /api/v1/learn/points/{id}/status
     POST /api/v1/admin/learn/points/import
可选：GET /api/v1/agent/weak-points

P1 紧随
1) 词表列表/详情（term_en/zh/tags/tip/frequency/confuse）
2) 收藏 + 已会/不会；可选 10 词「看英文选中文」小测
3) 英语题解析→词条；知识点详情挂相关术语
4) CSV/JSON 导入；种子 ≥80（目标 80～150）
API：GET /api/v1/learn/glossary|glossary/{id}
     POST .../status 、.../quiz 、.../quiz/submit
     POST /api/v1/admin/learn/glossary/import

暂缓：AI小课、SRS闪卡、音视频、打卡日历

实现注意
- Vue3 现有路由下新增 /learn/*；复用 Tailwind 与 44pt 热区规范
- Markdown 用现有或轻量渲染器；公式可用 KaTeX 或纯文本口诀
- question 表增 knowledge_point_ids / glossary_ids（JSON）
- 与 mastery 解耦：本期状态独立；后续再映射掌握度
- OpenAPI /api/docs 同步；student_2026 可测全路径
- 种子与导入文件放 repo 的 data/learn/（勿提交版权扫描件）
```

---

## 8. 变更记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-09-07 | v1.0 | 据软考中项助手材料立项；A=MVP，B=P1；暂缓项按用户确认 |

