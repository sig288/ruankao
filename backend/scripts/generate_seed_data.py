# -*- coding: utf-8 -*-
"""
Generator for points_seed.json and glossary_seed.json
Strictly original educational study notes for System Integration Project Management (3rd edition).
"""
import os
import json

CHAPTERS = [
    {"id": "CH01", "code": "CH01", "title": "第1章 信息化发展", "sort_order": 1},
    {"id": "CH02", "code": "CH02", "title": "第2章 信息技术发展", "sort_order": 2},
    {"id": "CH03", "code": "CH03", "title": "第3章 信息系统集成及服务", "sort_order": 3},
    {"id": "CH04", "code": "CH04", "title": "第4章 信息安全与网络", "sort_order": 4},
    {"id": "CH05", "code": "CH05", "title": "第5章 软件工程与系统架构", "sort_order": 5},
    {"id": "CH06", "code": "CH06", "title": "第6章 项目立项与招投标", "sort_order": 6},
    {"id": "CH07", "code": "CH07", "title": "第7章 项目整体管理", "sort_order": 7},
    {"id": "CH08", "code": "CH08", "title": "第8章 项目范围管理", "sort_order": 8},
    {"id": "CH09", "code": "CH09", "title": "第9章 项目进度管理", "sort_order": 9},
    {"id": "CH10", "code": "CH10", "title": "第10章 项目成本管理", "sort_order": 10},
    {"id": "CH11", "code": "CH11", "title": "第11章 项目质量管理", "sort_order": 11},
    {"id": "CH12", "code": "CH12", "title": "第12章 项目资源管理", "sort_order": 12},
    {"id": "CH13", "code": "CH13", "title": "第13章 项目沟通管理", "sort_order": 13},
    {"id": "CH14", "code": "CH14", "title": "第14章 项目风险管理", "sort_order": 14},
    {"id": "CH15", "code": "CH15", "title": "第15章 项目采购管理", "sort_order": 15},
    {"id": "CH16", "code": "CH16", "title": "第16章 项目干系人管理", "sort_order": 16},
    {"id": "CH17", "code": "CH17", "title": "第17章 法律法规与标准化", "sort_order": 17},
]

POINTS = [
    {
        "id": "kp_cloud_computing",
        "chapter_id": "CH02",
        "title": "云计算三大服务模式 (IaaS/PaaS/SaaS)",
        "frequency": "high",
        "est_minutes": 10,
        "summary_md": """### 一、云计算三大服务模式对比
1. **IaaS（基础设施即服务）**：向用户提供计算机能力、存储空间等底层计算资源。典型代表：云服务器 ECS、虚拟磁盘、对象存储 OSS、VPC 网络。
2. **PaaS（平台即服务）**：向用户提供软件研发与运行的平台环境。用户不需管理操作系统，只需关注代码开发与数据。典型代表：容器服务 K8s、数据库服务 RDS、中间件平台。
3. **SaaS（软件即服务）**：直接向终端用户提供完整现成的应用软件。用户通过浏览器或客户端直接使用。典型代表：企业邮箱、Office 365、钉钉、Salesforce。

### 二、云计算四大部署模式
- **公有云**：第三方云提供商拥有并运营，面向公众或大型企业开放。
- **私有云**：专供单一组织使用，安全性高、合规性强。
- **混合云**：结合公有云与私有云优势，敏感数据存私有，弹性算力走公有。
- **社区云/行业云**：由若干利益相关的组织共享（如金融行业云、医疗云）。""",
        "formula_md": "【速记口诀】\n硬机存网是 IaaS，\n运行平台是 PaaS，\n开箱即用是 SaaS；\n按需租赁弹力大，安全合规看私家。",
        "domain_tags": ["新技术", "云计算", "信息化基础"],
        "glossary_ids": ["term_iaas", "term_paas", "term_saas", "term_cloud_computing"],
        "question_ids": [],
        "sort_order": 1
    },
    {
        "id": "kp_sec_baseline",
        "chapter_id": "CH04",
        "title": "网络安全与等保2.0核心要求",
        "frequency": "high",
        "est_minutes": 10,
        "summary_md": """### 一、信息安全五大基本属性 (CIA+A+N)
1. **机密性 (Confidentiality)**：确保信息不泄露给非授权的个人或实体（常用对称/非对称加密）。
2. **完整性 (Integrity)**：确保数据在传输与存储中未经非授权篡改（常用哈希函数 MD5/SHA、数字签名）。
3. **可用性 (Availability)**：确保授权用户在需要时能及时访问并使用资源（防范 DDoS、双机热备）。
4. **真实性/抗抵赖性 (Non-repudiation)**：通信双方均无法否认其发送或接收行为（数字签名技术）。

### 二、网络安全等级保护 2.0 (五级分类)
- **第一级：自主保护级**（对公民/法人合法权益造成损害，对社会公共利益和国家安全无损害）。
- **第二级：指导保护级**（对社会公共利益造成一般损害，不危害国家安全）。
- **第三级：监督保护级**（对社会秩序和公共利益造成严重损害，或对国家安全造成危害，关键信息基础设施门槛）。
- **第四级：强制保护级**（对国家安全造成特别严重损害）。
- **第五级：专控保护级**。""",
        "formula_md": "【速记口诀】\n一自主、二指导、三监督、四强制、五专控；\n系统集成重点盯：三级监督是核心！",
        "domain_tags": ["信息安全", "等保2.0", "网络工程"],
        "glossary_ids": [],
        "question_ids": [],
        "sort_order": 1
    },
    {
        "id": "kp_charter_pm",
        "chapter_id": "CH07",
        "title": "项目章程制定与项目经理正式授权",
        "frequency": "high",
        "est_minutes": 8,
        "summary_md": """### 一、项目章程 (Project Charter)
项目章程是正式批准项目成立并授权项目经理在项目活动中动用组织资源的文件。
- **发布者**：必须由发起人（Sponsor）或高级管理层签发，**项目经理不能签署发布自己的章程**。
- **核心作用**：
  1. 宣告项目正式立项与合法地位；
  2. 正式指派项目经理，明确其职责与权限级别；
  3. 规定总体里程碑、高层级预算与高层级需求。

### 二、常见考场陷阱
- 陷阱1：口头任命项目经理直接开工（错误！必须有书面签署的项目章程或正式授权书）。
- 陷阱2：项目经理签字批准项目章程（错误！项目经理可以参与编写，但审批与发布权属于发起人）。""",
        "formula_md": "【速记口诀】\n发起签字立项目，授权经手动资源；\n高层预算与目标，章程落地才开班！",
        "domain_tags": ["项目整合管理", "整体管理", "立项启动"],
        "glossary_ids": ["term_project_charter", "term_pmbok"],
        "question_ids": [],
        "sort_order": 1
    },
    {
        "id": "kp_ccb_change",
        "chapter_id": "CH07",
        "title": "项目整体变更控制与 CCB 决策流程",
        "frequency": "high",
        "est_minutes": 15,
        "summary_md": """### 一、项目整体变更控制标准 7 步法 (历年必考)
1. **提出变更申请**：任何干系人都可以提出变更，但必须**书面提交**《变更申请单》。
2. **记录变更日志**：项目经理将变更诉求记录入变更日志 (Change Log)。
3. **影响评估与综合分析**：项目经理与团队全面评估该变更对范围、成本、进度、质量、风险的综合影响。
4. **提交变更控制委员会 (CCB) 审批**：重大变更及基准修改必须经 CCB 正式开会评审批准或拒绝。
5. **通知相关干系人**：将 CCB 的评审决定（批准/拒绝/推迟）书面通知申请人与所有相关干系人。
6. **更新项目管理计划与基准**：若批准，必须同步更新基准（范围、进度、成本基准）并更新计划。
7. **组织实施并验证监控**：组织人员实施变更，并对实施结果进行质量验证与收尾跟踪。

### 二、核心黄金原则
- 口头变更一律无效，必须书面化！
- 绝不能私下答应客户做微小改动（防止范围蔓延 Scope Creep）！""",
        "formula_md": "【速记口诀】\n变更提出必书面，影响分析要周全；\nCCB 会审定大局，更新基准再动干；\n通知各方记日志，跟踪验证保闭环！",
        "domain_tags": ["项目整合管理", "变更控制", "配置管理"],
        "glossary_ids": ["term_ccb", "term_baseline", "term_scope_creep"],
        "question_ids": [],
        "sort_order": 2
    },
    {
        "id": "kp_wbs_decomp",
        "chapter_id": "CH08",
        "title": "WBS 分解原则与范围基准 (100% 规则)",
        "frequency": "high",
        "est_minutes": 12,
        "summary_md": """### 一、工作分解结构 (WBS)
WBS（Work Breakdown Structure）是以交付物为导向对项目团队所要完成的工作进行的分层分解。
- **100% 规则**：WBS 必须包含 100% 的项目工作（内部与外部），且不包含任何不属于项目的工作。上一层的工作必须完全等于下一层子工作的总和。
- **工作包 (Work Package)**：WBS 最底层、不可再分解的组成部分。可以对其成本和持续时间进行可靠估算和管理。通常遵循“8/80 小时原则”。
- **WBS 词典**：详细描述 WBS 中各个工作包的交付物、工作范围、验收标准、负责人的支持文件。

### 二、范围基准三要素 (历年考点)
范围基准包括：**项目范围说明书** + **WBS** + **WBS 词典**。""",
        "formula_md": "【速记口诀】\n交付为纲层层分，百分之百不能少；\n底层落入工作包，范围基准三件套：\n说明书配 WBS，再带词典跑不了！",
        "domain_tags": ["项目范围管理", "范围基准", "WBS"],
        "glossary_ids": ["term_wbs", "term_work_package", "term_scope_baseline", "term_scope_creep"],
        "question_ids": [],
        "sort_order": 1
    },
    {
        "id": "kp_cpm_float",
        "chapter_id": "CH09",
        "title": "关键路径法 (CPM) 与总时差/自由时差计算",
        "frequency": "high",
        "est_minutes": 15,
        "summary_md": """### 一、关键路径法 (CPM) 核心概念
- **关键路径 (Critical Path)**：网络图中从起始节点到终止节点耗时最长的一条通路，决定了项目的最短完工工期。
- 关键路径上所有活动的总时差 (Total Float) 通常为 0。
- 一个网络图中可能存在一条或多条关键路径。多条关键路径意味着项目风险增加。

### 二、两大时差计算核心公式
1. **总时差 (TF, Total Float)**：在不延误整个项目总工期的前提下，本活动可以延误的最大时间。
   $$\\text{TF} = \\text{LS} - \\text{ES} = \\text{LF} - \\text{EF}$$
2. **自由时差 (FF, Free Float)**：在不影响紧后活动最早开始时间的前提下，本活动可以延误的时间。
   $$\\text{FF} = \\min(\\text{紧后ES}) - \\text{本活动EF}$$
3. **时差关系定理**：自由时差永远小于或等于总时差（$\\text{FF} \\le \\text{TF}$）。""",
        "formula_md": "【计算口诀】\n正推取大求早完（早始早完取最大），\n逆推取小算迟始（迟始迟完取最小）；\n总时差：迟早相减不误期（LS-ES 或 LF-EF）；\n自由差：紧后早始减本完（min(紧后ES) - EF）！",
        "domain_tags": ["项目进度管理", "关键路径", "双代号网络图"],
        "glossary_ids": ["term_cpm", "term_total_float", "term_free_float", "term_pdm"],
        "question_ids": [],
        "sort_order": 1
    },
    {
        "id": "kp_schedule_compress",
        "chapter_id": "CH09",
        "title": "进度压缩两大技术：赶工 vs 快速跟进",
        "frequency": "high",
        "est_minutes": 8,
        "summary_md": """### 一、进度压缩 (Schedule Compression)
在不缩减项目既定工作范围的前提下缩短项目进度工期的技术。

1. **赶工 (Crashing)**：
   - 做法：在**关键路径**上的活动投入额外资源（如安排人员加班、增派核心技术骨干、外包辅助模块）。
   - 代价与风险：**直接导致项目成本增加**，可能出现人员边际效益递减。

2. **快速跟进 (Fast Tracking)**：
   - 做法：将原本计划按顺序前后串行开展的活动，调整为**并行（部分重叠）开展**。
   - 代价与风险：**极易带来质量返工风险**，并且增加项目沟通协调与管理复杂度。""",
        "formula_md": "【速记口诀】\n花钱加班叫赶工，成本超支需分明；\n串行变行快跟进，返工风险在其中；\n要想压缩提工期，关键路径方起功！",
        "domain_tags": ["项目进度管理", "进度压缩", "案例分析"],
        "glossary_ids": ["term_crashing", "term_fast_tracking"],
        "question_ids": [],
        "sort_order": 2
    },
    {
        "id": "kp_evm_cpi",
        "chapter_id": "CH10",
        "title": "挣值分析 (EVM) 与绩效指数 (CPI/SPI)",
        "frequency": "high",
        "est_minutes": 20,
        "summary_md": """### 一、EVM 三大基础参数
1. **计划值 (PV, Planned Value)**：到某一时间点计划完成工作的预算成本。
2. **挣值 (EV, Earned Value)**：到某一时间点实际已完成工作的预算成本（反映真实工作量贡献）。
3. **实际成本 (AC, Actual Cost)**：到某一时间点完成工作所实际花费的总支出。
4. **完工预算 (BAC, Budget at Completion)**：项目全部工作的总预算成本。

### 二、两大偏差与两大绩效指数
- **成本偏差 (CV)**：$\\text{CV} = \\text{EV} - \\text{AC}$。CV > 0 节支，CV < 0 超支。
- **进度偏差 (SV)**：$\\text{SV} = \\text{EV} - \\text{PV}$。SV > 0 提前，SV < 0 延误。
- **成本绩效指数 (CPI)**：$\\text{CPI} = \\frac{\\text{EV}}{\\text{AC}}$。CPI > 1 资金利用高效，CPI < 1 超支。
- **进度绩效指数 (SPI)**：$\\text{SPI} = \\frac{\\text{EV}}{\\text{PV}}$。SPI > 1 进度超前，SPI < 1 进度落后。

### 三、完工预测 (EAC) 黄金公式
- **典型偏差 (原有偏差趋势将持续)**：
  $$\\text{EAC} = \\frac{\\text{BAC}}{\\text{CPI}}$$
- **非典型偏差 (未来工作将按原计划预算单价执行)**：
  $$\\text{EAC} = \\text{AC} + (\\text{BAC} - \\text{EV})$$""",
        "formula_md": "【挣值秒杀口诀】\nEV 永远在前方，相减大于零为吉（CV>0节约，SV>0超前）；\n除法大于一为佳（CPI>1省钱，SPI>1快速）；\n典型用除法 EAC=BAC/CPI，非典型用加法 EAC=AC+BAC-EV！",
        "domain_tags": ["项目成本管理", "挣值分析", "案例必考大题"],
        "glossary_ids": ["term_evm", "term_bac", "term_pv", "term_ev", "term_ac", "term_cv", "term_sv", "term_cpi", "term_spi", "term_eac", "term_etc"],
        "question_ids": [],
        "sort_order": 1
    },
    {
        "id": "kp_qa_vs_qc",
        "chapter_id": "CH11",
        "title": "质量保证 (QA) vs 质量控制 (QC) 本质区别",
        "frequency": "high",
        "est_minutes": 10,
        "summary_md": """### 一、QA 与 QC 概念辨析 (单选高频混淆考点)
| 对比维度 | 质量保证 (QA - Quality Assurance) | 质量控制 (QC - Quality Control) |
|---|---|---|
| **核心关注点** | 关注**生产过程与管理体系** | 关注**最终交付结果与产品本身** |
| **所属过程组** | 属于**执行过程组** | 属于**监控过程组** |
| **实施目的** | 建立过程信心，持续改进，防患于未然 | 发现具体缺陷，剔除次品，把好交付验收关 |
| **常用工具** | 质量审计 (Quality Audit)、过程分析 | 检查 (Inspection)、测试 (Testing)、统计抽样 |
| **参与主体** | 通常由独立的 QA 部门或质量管理团队主导 | 通常由测试工程师、质检人员或验收方执行 |""",
        "formula_md": "【速记口诀】\nQA 管过程，执行抓审计；\nQC 查产品，监控找次品；\n过程做扎实，结果少返修！",
        "domain_tags": ["项目质量管理", "质量控制", "质量保证"],
        "glossary_ids": ["term_qa", "term_qc", "term_tqm"],
        "question_ids": [],
        "sort_order": 1
    },
    {
        "id": "kp_conflict_mgmt",
        "chapter_id": "CH12",
        "title": "冲突管理的 5 大解决策略与塔克曼模型",
        "frequency": "high",
        "est_minutes": 12,
        "summary_md": """### 一、冲突解决 5 大策略
1. **合作/解决问题 (Collaborate/Problem Solving)**：双赢策略。集思广益深入分析根因，达成各方共识（最佳首选）。
2. **妥协/调解 (Compromise/Reconcile)**：双输策略。各退一步，双方各寻找某种程度上的满意，临时折中。
3. **缓和/包容 (Smooth/Accommodate)**：强调一致弱化差异，维护表面和谐（短时息事宁人）。
4. **撤退/回避 (Withdraw/Avoid)**：从冲突现场退出或推迟处理，把问题搁置。
5. **强迫/命令 (Force/Direct)**：利用职权强推一方意见，赢-输策略（紧急关头或原则性问题可用）。

### 二、塔克曼团队建设发展 5 阶段模型
- **形成阶段 (Forming)**：相互认识，独立谨慎，依赖领导。
- **震荡阶段 (Storming)**：观点碰撞，争夺主导，冲突频发（冲突最高峰期）。
- **规范阶段 (Norming)**：制定规则，形成共识，开始协同。
- **发挥阶段 (Performing)**：高度默契，自主高效，绩优运转。
- **解散阶段 (Adjourning)**：任务完成，团队解散。""",
        "formula_md": "【速记口诀】\n合作双赢找根因，妥协折中各退步；\n缓和求同先保和，回避撤退拖延顾；\n应急拍板靠强迫；\n形成震荡规范发，最后解散功劳述！",
        "domain_tags": ["项目资源管理", "团队建设", "冲突管理"],
        "glossary_ids": ["term_raci", "term_ram"],
        "question_ids": [],
        "sort_order": 1
    },
    {
        "id": "kp_comm_channel",
        "chapter_id": "CH13",
        "title": "沟通渠道数计算与有效沟通方式",
        "frequency": "high",
        "est_minutes": 8,
        "summary_md": """### 一、潜在沟通渠道数计算公式
在有 $n$ 名项目干系人参与的项目中，潜在沟通渠道总数 $C$ 的计算公式为：
$$C = \\frac{n \\times (n - 1)}{2}$$

**典型考题**：
若团队由原先的 5 人增加到 8 人，潜在沟通渠道增加了多少条？
- 原沟通渠道数：$5 \\times 4 / 2 = 10$ 条
- 新沟通渠道数：$8 \\times 7 / 2 = 28$ 条
- 净增加渠道数：$28 - 10 = 18$ 条

### 二、三大基本沟通方式
1. **交互式沟通 (Interactive)**：实时双向沟通（会议、电话、视频会谈）。
2. **推式沟通 (Push)**：发送给特定受众，不确保已被理解（邮件、备忘录、报告）。
3. **拉式沟通 (Pull)**：用于大量受众自主按需访问（内部知识库、Wiki、共享盘）。""",
        "formula_md": "【速记口诀】\n干系人数为 n，渠道相乘再折半：n*(n-1)/2；\n人多渠道翻倍涨，沟通管理抓规范！",
        "domain_tags": ["项目沟通管理", "计算题必拿分", "沟通渠道"],
        "glossary_ids": [],
        "question_ids": [],
        "sort_order": 1
    },
    {
        "id": "kp_risk_strategies",
        "chapter_id": "CH14",
        "title": "消极威胁 vs 积极机会应对策略对比",
        "frequency": "high",
        "est_minutes": 10,
        "summary_md": """### 一、消极风险 (威胁) 应对 4 大策略
1. **规避 (Avoid)**：彻底改变计划消除威胁（如取消高风险特性、更换成熟团队）。
2. **转移 (Transfer)**：将负面影响与应对责任转移给第三方（如购买商业保险、签署固定总价外包合同、质保条款）。
3. **减轻 (Mitigate)**：采取前置措施降低风险发生概率或减少冲击（如增加冗余测试、原型预研、选用更可靠供货商）。
4. **接受 (Accept)**：主动接受（建立应急储备）或被动接受（发生时再应对）。

### 二、积极风险 (机会) 应对 4 大策略
1. **开拓 (Exploit)**：确保机会 100% 出现（如指派组织最优秀顶尖团队、采用最新突破技术）。
2. **提高 (Enhance)**：增加机会出现的概率或正向影响（如提早追加优质资源）。
3. **分享 (Share)**：将机会与第三方共享，组建联合体合作共赢。
4. **接受 (Accept)**：乐见其成，不主动干预。""",
        "formula_md": "【速记口诀】\n消极威胁：规避消除、转移买保、减轻降率、接受备金；\n积极机会：开拓必夺、提高增率、分享合作、接受随缘！",
        "domain_tags": ["项目风险管理", "风险应对策略", "单选必考"],
        "glossary_ids": ["term_risk_mitigation", "term_risk_transference", "term_risk_avoidance", "term_risk_acceptance"],
        "question_ids": [],
        "sort_order": 1
    },
    {
        "id": "kp_contract_types",
        "chapter_id": "CH15",
        "title": "三大采购合同类型与买卖双方风险分担",
        "frequency": "high",
        "est_minutes": 12,
        "summary_md": """### 一、三大采购合同类型
1. **总价合同 (Fixed Price)**：
   - 包含：固定总价合同 (FFP)、总价加激励费用 (FPIP)、总价加经济价格调整 (FP-EPA)。
   - 适用：工作范围极其清晰明确、技术成熟、变更少。
   - 风险分配：**买方风险最小，卖方承担最大成本超支风险**。
2. **成本补偿合同 (Cost-Reimbursable)**：
   - 包含：成本加固定费用 (CPFF)、成本加激励费用 (CPIF)、成本加奖励费用 (CPAF)。
   - 适用：工作范围尚不清晰、前沿探索研发项目、紧急工程。
   - 风险分配：**买方承担最大超支风险，卖方风险较小**。
3. **工料合同 (Time & Material, T&M)**：
   - 具有总价合同与成本补偿合同的双重特征（通常按人/天、工时费率计算）。
   - 适用：无法快速编制详细范围、短期聘请专家外包或紧急增加人手。""",
        "formula_md": "【速记口诀】\n范围明确签总价，卖方担险买方笑；\n范围模糊成本补，买方买单风险高；\n紧急加派用工料，人天算账灵活跑！",
        "domain_tags": ["项目采购管理", "合同管理", "招投标"],
        "glossary_ids": ["term_fixed_price_contract", "term_cost_reimbursable_contract", "term_time_and_material_contract"],
        "question_ids": [],
        "sort_order": 1
    },
    {
        "id": "kp_stakeholder_matrix",
        "chapter_id": "CH16",
        "title": "权力/利益方格与干系人管理策略",
        "frequency": "high",
        "est_minutes": 8,
        "summary_md": """### 一、权力/利益方格 4 大象限策略 (历年单选必考)
1. **高权力、高利益**（右上角象限）：**重点管理 (Manage Closely)**。例如：项目关键发起人、核心业务主管、主要出资客户。
2. **高权力、低利益**（左上角象限）：**令其满意 (Keep Satisfied)**。例如：上级合规与审计部门、外部监管机构、有否决权的高管。
3. **低权力、高利益**（右下角象限）：**随时告知 (Keep Informed)**。例如：最终一线受影响的使用人员、基层团队骨干。
4. **低权力、低利益**（左下角象限）：**花最少精力监督 (Monitor)**。例如：周边辅助服务外围人员。""",
        "formula_md": "【速记口诀】\n双高人物重点管（高权高利），\n权大无欲求满意（高权低利），\n权小利大常告知（低权高利），\n双低群体顺带督（低权低利）！",
        "domain_tags": ["项目干系人管理", "干系人分析", "权力利益方格"],
        "glossary_ids": ["term_stakeholder"],
        "question_ids": [],
        "sort_order": 1
    }
]

GLOSSARY_TERMS = [
    {"term_en": "WBS (Work Breakdown Structure)", "term_zh": "工作分解结构", "tags": ["范围管理", "核心工具"], "tip": "面向交付物的层次化分解，最底层为工作包，遵循100%原则", "frequency": "high", "confuse_with": ["OBS (组织分解结构)", "RBS (资源/风险分解结构)"], "knowledge_point_ids": ["kp_wbs_decomp"]},
    {"term_en": "EVM (Earned Value Management)", "term_zh": "挣值管理", "tags": ["成本管理", "核心算法"], "tip": "综合评估项目范围、进度与成本绩效的黄金分析技术", "frequency": "high", "confuse_with": ["EVA (经济增加值)"], "knowledge_point_ids": ["kp_evm_cpi"]},
    {"term_en": "BAC (Budget at Completion)", "term_zh": "完工预算", "tags": ["成本管理"], "tip": "项目全部既定工作预算总额，等于所有工作包 PV 汇总", "frequency": "high", "confuse_with": ["EAC (完工总估算)"], "knowledge_point_ids": ["kp_evm_cpi"]},
    {"term_en": "PV (Planned Value)", "term_zh": "计划值", "tags": ["成本管理"], "tip": "在规定时间节点计划应完成工作的预算成本（BCWS）", "frequency": "high", "confuse_with": ["EV (挣值)"], "knowledge_point_ids": ["kp_evm_cpi"]},
    {"term_en": "EV (Earned Value)", "term_zh": "挣值", "tags": ["成本管理"], "tip": "在规定时间节点实际已完成工作的预算金额（BCWP）", "frequency": "high", "confuse_with": ["AC (实际成本)"], "knowledge_point_ids": ["kp_evm_cpi"]},
    {"term_en": "AC (Actual Cost)", "term_zh": "实际成本", "tags": ["成本管理"], "tip": "在规定时间节点为完成工作所实际发生的真实支出（ACWP）", "frequency": "high", "confuse_with": ["EV (挣值)"], "knowledge_point_ids": ["kp_evm_cpi"]},
    {"term_en": "CV (Cost Variance)", "term_zh": "成本偏差", "tags": ["成本管理"], "tip": "CV = EV - AC；大于0表示成本结余，小于0表示成本超支", "frequency": "high", "confuse_with": ["SV (进度偏差)"], "knowledge_point_ids": ["kp_evm_cpi"]},
    {"term_en": "SV (Schedule Variance)", "term_zh": "进度偏差", "tags": ["进度管理", "成本管理"], "tip": "SV = EV - PV；大于0表示进度超前，小于0表示进度滞后", "frequency": "high", "confuse_with": ["CV (成本偏差)"], "knowledge_point_ids": ["kp_evm_cpi"]},
    {"term_en": "CPI (Cost Performance Index)", "term_zh": "成本绩效指数", "tags": ["成本管理"], "tip": "CPI = EV / AC；大于1说明资金利用效率高，小于1说明超支", "frequency": "high", "confuse_with": ["SPI (进度绩效指数)"], "knowledge_point_ids": ["kp_evm_cpi"]},
    {"term_en": "SPI (Schedule Performance Index)", "term_zh": "进度绩效指数", "tags": ["进度管理"], "tip": "SPI = EV / PV；大于1说明实际进度超前于计划，小于1说明滞后", "frequency": "high", "confuse_with": ["CPI (成本绩效指数)"], "knowledge_point_ids": ["kp_evm_cpi"]},
    {"term_en": "EAC (Estimate at Completion)", "term_zh": "完工总估算", "tags": ["成本管理"], "tip": "典型情况 EAC = BAC / CPI，非典型 EAC = AC + (BAC - EV)", "frequency": "high", "confuse_with": ["ETC (完工尚需估算)"], "knowledge_point_ids": ["kp_evm_cpi"]},
    {"term_en": "ETC (Estimate to Complete)", "term_zh": "完工尚需估算", "tags": ["成本管理"], "tip": "完成剩余工作还需要的额外成本预测，典型时 ETC = (BAC - EV) / CPI", "frequency": "high", "confuse_with": ["EAC (完工总估算)"], "knowledge_point_ids": ["kp_evm_cpi"]},
    {"term_en": "TCPI (To-Complete Performance Index)", "term_zh": "完工尚需绩效指数", "tags": ["成本管理"], "tip": "为了在指定目标内完工，剩余资源必须达到的成本绩效水平", "frequency": "mid", "confuse_with": ["CPI"], "knowledge_point_ids": ["kp_evm_cpi"]},
    {"term_en": "VAC (Variance at Completion)", "term_zh": "完工偏差", "tags": ["成本管理"], "tip": "VAC = BAC - EAC；预算总额与预测总花费之差", "frequency": "mid", "confuse_with": ["CV"], "knowledge_point_ids": ["kp_evm_cpi"]},
    {"term_en": "CPM (Critical Path Method)", "term_zh": "关键路径法", "tags": ["进度管理", "核心算法"], "tip": "通过顺推与逆推计算网络图中所有活动的时差，找出耗时最长路径", "frequency": "high", "confuse_with": ["CCM (关键链法)"], "knowledge_point_ids": ["kp_cpm_float"]},
    {"term_en": "PDM (Precedence Diagramming Method)", "term_zh": "紧前关系绘图法 (单代号网络图)", "tags": ["进度管理"], "tip": "节点表示活动，箭线表示先后逻辑依赖关系（FS, SS, FF, SF）", "frequency": "high", "confuse_with": ["ADM (双代号网络图)"], "knowledge_point_ids": ["kp_cpm_float"]},
    {"term_en": "ADM (Arrow Diagramming Method)", "term_zh": "箭线绘图法 (双代号网络图)", "tags": ["进度管理"], "tip": "箭线表示活动，节点表示事件，只支持完成到开始 (FS) 关系，需虚活动", "frequency": "mid", "confuse_with": ["PDM (单代号网络图)"], "knowledge_point_ids": ["kp_cpm_float"]},
    {"term_en": "PERT (Program Evaluation and Review Technique)", "term_zh": "计划评审技术 (三点估算)", "tags": ["进度管理"], "tip": "加权均值公式：(最乐观 + 4*最可能 + 最悲观) / 6", "frequency": "high", "confuse_with": ["CPM"], "knowledge_point_ids": ["kp_cpm_float"]},
    {"term_en": "Crashing", "term_zh": "赶工 (压缩工期)", "tags": ["进度管理"], "tip": "在关键路径投入额外资源或加班以缩短工期，代价是直接成本显著增加", "frequency": "high", "confuse_with": ["Fast Tracking (快速跟进)"], "knowledge_point_ids": ["kp_schedule_compress"]},
    {"term_en": "Fast Tracking", "term_zh": "快速跟进 (并行推进)", "tags": ["进度管理"], "tip": "将原本顺序开展的活动改为部分并行重叠开展，代价是带来返工风险", "frequency": "high", "confuse_with": ["Crashing (赶工)"], "knowledge_point_ids": ["kp_schedule_compress"]},
    {"term_en": "CCB (Change Control Board)", "term_zh": "变更控制委员会", "tags": ["整体管理", "核心机构"], "tip": "负责审查、评价、批准或推迟并记录项目重大变更的正式决策群体", "frequency": "high", "confuse_with": ["PMO (项目管理办公室)"], "knowledge_point_ids": ["kp_ccb_change"]},
    {"term_en": "PMBOK (Project Management Body of Knowledge)", "term_zh": "项目管理知识体系指南", "tags": ["通用规范"], "tip": "由 PMI 制定的全球项目管理行业通用知识框架指南", "frequency": "mid", "confuse_with": ["ITIL", "PRINCE2"], "knowledge_point_ids": ["kp_charter_pm"]},
    {"term_en": "PMIS (Project Management Information System)", "term_zh": "项目管理信息系统", "tags": ["整体管理"], "tip": "组织内部用于收集、整合和传播项目管理过程产出物的软硬件自动化工具", "frequency": "mid", "confuse_with": ["ERP"], "knowledge_point_ids": []},
    {"term_en": "OBS (Organizational Breakdown Structure)", "term_zh": "组织分解结构", "tags": ["资源管理"], "tip": "展示项目工作与现有组织内部各部门对应关系的层次分解结构", "frequency": "high", "confuse_with": ["WBS", "RBS"], "knowledge_point_ids": ["kp_wbs_decomp"]},
    {"term_en": "RBS (Resource/Risk Breakdown Structure)", "term_zh": "资源分解结构 / 风险分解结构", "tags": ["资源管理", "风险管理"], "tip": "按类别和类型对资源或风险进行层次化分类与展现的树状图", "frequency": "mid", "confuse_with": ["WBS", "OBS"], "knowledge_point_ids": []},
    {"term_en": "RAM (Responsibility Assignment Matrix)", "term_zh": "责任分配矩阵", "tags": ["资源管理"], "tip": "明确各项工作包与团队成员之间负责、配合关系的矩阵表", "frequency": "high", "confuse_with": ["RACI"], "knowledge_point_ids": ["kp_conflict_mgmt"]},
    {"term_en": "RACI (Responsible, Accountable, Consulted, Informed)", "term_zh": "RACI 职责矩阵", "tags": ["资源管理"], "tip": "每个工作包只能有唯一的 A (问责主管)，确保权责清晰不扯皮", "frequency": "high", "confuse_with": ["RAM"], "knowledge_point_ids": ["kp_conflict_mgmt"]},
    {"term_en": "SOW (Statement of Work)", "term_zh": "工作说明书", "tags": ["采购管理", "范围管理"], "tip": "对所采购产品、服务或成果的详细叙述，采购招标文件的重要输入", "frequency": "high", "confuse_with": ["SLA", "RFP"], "knowledge_point_ids": []},
    {"term_en": "RFP (Request for Proposal)", "term_zh": "方案建议书邀请函", "tags": ["采购管理", "招投标"], "tip": "买方向潜在供应商发出的正式请求，要求对方提供完整的项目解决方案及报价", "frequency": "high", "confuse_with": ["RFQ", "RFI"], "knowledge_point_ids": ["kp_contract_types"]},
    {"term_en": "RFQ (Request for Quotation)", "term_zh": "报价邀请书", "tags": ["采购管理", "招投标"], "tip": "主要针对标准化、现货或明确货品向供应商征求具体价格与交期", "frequency": "high", "confuse_with": ["RFP", "RFI"], "knowledge_point_ids": ["kp_contract_types"]},
    {"term_en": "RFI (Request for Information)", "term_zh": "信息征集书", "tags": ["采购管理"], "tip": "买方在编制正式招标文件前，用于调研市场和了解潜在供应商能力的信息表", "frequency": "mid", "confuse_with": ["RFP"], "knowledge_point_ids": []},
    {"term_en": "SLA (Service Level Agreement)", "term_zh": "服务级别协议", "tags": ["服务管理", "采购管理"], "tip": "服务提供方与客户之间就响应时限、可用性达成共识的法律/业务契约", "frequency": "high", "confuse_with": ["SOW", "OLA"], "knowledge_point_ids": []},
    {"term_en": "KPI (Key Performance Indicator)", "term_zh": "关键绩效指标", "tags": ["组织管理"], "tip": "衡量战略目标达成度与业务过程运转质量的可量化指标", "frequency": "mid", "confuse_with": ["OKR"], "knowledge_point_ids": []},
    {"term_en": "OKR (Objectives and Key Results)", "term_zh": "目标与关键结果", "tags": ["组织管理"], "tip": "强调自驱、目标聚焦与突破性成果的高效敏捷目标管理方法", "frequency": "mid", "confuse_with": ["KPI"], "knowledge_point_ids": []},
    {"term_en": "TQM (Total Quality Management)", "term_zh": "全面质量管理", "tags": ["质量管理"], "tip": "全员参与、全过程控制、以顾客满意为核心的系统质量改进文化", "frequency": "mid", "confuse_with": ["Six Sigma"], "knowledge_point_ids": ["kp_qa_vs_qc"]},
    {"term_en": "QA (Quality Assurance)", "term_zh": "质量保证", "tags": ["质量管理", "核心考点"], "tip": "聚焦过程与管理体系审计，预防缺陷发生，属于执行过程组", "frequency": "high", "confuse_with": ["QC (质量控制)"], "knowledge_point_ids": ["kp_qa_vs_qc"]},
    {"term_en": "QC (Quality Control)", "term_zh": "质量控制", "tags": ["质量管理", "核心考点"], "tip": "聚焦最终产品与具体测试，检验缺陷并剔除次品，属于监控过程组", "frequency": "high", "confuse_with": ["QA (质量保证)"], "knowledge_point_ids": ["kp_qa_vs_qc"]},
    {"term_en": "CMMI (Capability Maturity Model Integration)", "term_zh": "软件能力成熟度模型集成", "tags": ["软件工程", "成熟度"], "tip": "分为5级：初始级、已管理级、已定义级、定量管理级、优化级", "frequency": "high", "confuse_with": ["ITSS"], "knowledge_point_ids": []},
    {"term_en": "ITSS (Information Technology Service Standards)", "term_zh": "信息技术服务标准", "tags": ["IT服务"], "tip": "中国自主制定的 IT 服务标准库体系，包含人员、过程、技术、资源四大要素", "frequency": "high", "confuse_with": ["ITIL"], "knowledge_point_ids": []},
    {"term_en": "ITIL (Information Technology Infrastructure Library)", "term_zh": "IT基础架构库", "tags": ["IT运维"], "tip": "全球事实上的 IT 服务管理与运维最佳实践参考体系指南", "frequency": "mid", "confuse_with": ["ITSS"], "knowledge_point_ids": []},
    {"term_en": "SWOT Analysis", "term_zh": "SWOT 分析法", "tags": ["战略分析", "风险管理"], "tip": "态势分析工具：内部优势 (Strengths)、劣势 (Weaknesses)，外部机会 (Opportunities)、威胁 (Threats)", "frequency": "high", "confuse_with": ["PEST"], "knowledge_point_ids": []},
    {"term_en": "Delphi Technique", "term_zh": "德尔菲法 (专家调查法)", "tags": ["估算技术", "风险识别"], "tip": "采用匿名、多轮背靠背函询方式，消除群体思维倾向，达成专家共识", "frequency": "high", "confuse_with": ["Brainstorming (头脑风暴)"], "knowledge_point_ids": []},
    {"term_en": "Scope Creep", "term_zh": "范围蔓延 (镀金/私自改需求)", "tags": ["范围管理", "风险管理"], "tip": "未经正式变更审批与资源补充而不断扩大项目功能或特性的负面现象", "frequency": "high", "confuse_with": ["Gold Plating (镀金)"], "knowledge_point_ids": ["kp_ccb_change", "kp_wbs_decomp"]},
    {"term_en": "Gold Plating", "term_zh": "镀金 (过度交付)", "tags": ["范围管理", "质量管理"], "tip": "项目团队自发主动向客户提供超出合同与范围要求的额外功能，属负面浪费行为", "frequency": "high", "confuse_with": ["Scope Creep (范围蔓延)"], "knowledge_point_ids": ["kp_wbs_decomp"]},
    {"term_en": "Float / Slack", "term_zh": "浮动时间 / 时差", "tags": ["进度管理"], "tip": "活动可以推迟而不影响后续活动或整个项目工期的宽裕时间量", "frequency": "high", "confuse_with": ["Critical Path"], "knowledge_point_ids": ["kp_cpm_float"]},
    {"term_en": "Total Float", "term_zh": "总时差", "tags": ["进度管理"], "tip": "在不延误项目总完工日期的前提下，该活动可以推迟的最大时间（LS-ES 或 LF-EF）", "frequency": "high", "confuse_with": ["Free Float (自由时差)"], "knowledge_point_ids": ["kp_cpm_float"]},
    {"term_en": "Free Float", "term_zh": "自由时差", "tags": ["进度管理"], "tip": "在不影响紧后活动最早开始时间的前提下，本活动可以延误的时间（min(紧后ES) - 本EF）", "frequency": "high", "confuse_with": ["Total Float (总时差)"], "knowledge_point_ids": ["kp_cpm_float"]},
    {"term_en": "Milestone", "term_zh": "里程碑", "tags": ["进度管理"], "tip": "项目进程中的重要关节点或阶段标志事件，其持续时间为零（工期为0）", "frequency": "high", "confuse_with": ["Work Package"], "knowledge_point_ids": ["kp_charter_pm"]},
    {"term_en": "Baseline", "term_zh": "基准", "tags": ["整体管理"], "tip": "经过正式评审和批准的计划版本，后续只有通过正式变更控制流程才能修改", "frequency": "high", "confuse_with": ["Target"], "knowledge_point_ids": ["kp_ccb_change", "kp_wbs_decomp"]},
    {"term_en": "Scope Baseline", "term_zh": "范围基准", "tags": ["范围管理"], "tip": "由项目范围说明书、WBS、WBS 词典三大部分共同构成的正式基准文件", "frequency": "high", "confuse_with": ["Cost Baseline"], "knowledge_point_ids": ["kp_wbs_decomp"]},
    {"term_en": "Cost Baseline", "term_zh": "成本基准", "tags": ["成本管理"], "tip": "经批准的按时间段分配的项目预算，不包括管理储备，呈典型 S 曲线分布", "frequency": "high", "confuse_with": ["Project Budget (包含管理储备)"], "knowledge_point_ids": ["kp_evm_cpi"]},
    {"term_en": "Schedule Baseline", "term_zh": "进度基准", "tags": ["进度管理"], "tip": "经正式批准的项目网络进度计划版本，用于作为衡量与报告进度绩效的基准", "frequency": "high", "confuse_with": ["Milestone List"], "knowledge_point_ids": ["kp_cpm_float"]},
    {"term_en": "Work Package", "term_zh": "工作包", "tags": ["范围管理"], "tip": "位于 WBS 最底层、可对其进行可靠成本估算与进度控制的最小工作单元", "frequency": "high", "confuse_with": ["Activity (活动)", "Control Account"], "knowledge_point_ids": ["kp_wbs_decomp"]},
    {"term_en": "Control Account", "term_zh": "控制账户", "tags": ["成本管理", "范围管理"], "tip": "高层管理控制点，把范围、预算、实际成本和进度整合在一起，并与挣值挂钩", "frequency": "mid", "confuse_with": ["Work Package"], "knowledge_point_ids": ["kp_wbs_decomp"]},
    {"term_en": "Code of Accounts", "term_zh": "账目编码", "tags": ["范围管理"], "tip": "用于唯一标识 WBS 每个组件的数字或字母编码编排系统", "frequency": "mid", "confuse_with": ["Chart of Accounts"], "knowledge_point_ids": ["kp_wbs_decomp"]},
    {"term_en": "Critical Chain Method (CCM)", "term_zh": "关键链法", "tags": ["进度管理"], "tip": "考虑资源有限性与制约条件，在关键路径基础上引入项目缓冲与接驳缓冲", "frequency": "mid", "confuse_with": ["CPM (关键路径法)"], "knowledge_point_ids": ["kp_cpm_float"]},
    {"term_en": "Buffer Management", "term_zh": "缓冲管理", "tags": ["进度管理"], "tip": "关键链法中的核心技术，通过监控项目缓冲与接驳缓冲的消耗速率预警进度风险", "frequency": "mid", "confuse_with": ["Lag Time"], "knowledge_point_ids": []},
    {"term_en": "Analogous Estimating", "term_zh": "类比估算 (自上而下估算)", "tags": ["估算技术"], "tip": "使用过去类似历史项目的实际参数作为当前估算基础，速度快但准确度较低", "frequency": "high", "confuse_with": ["Parametric Estimating (参数估算)"], "knowledge_point_ids": []},
    {"term_en": "Parametric Estimating", "term_zh": "参数估算", "tags": ["估算技术"], "tip": "利用历史数据与其它变量之间的统计数学关系计算估算值（如单价乘数量）", "frequency": "high", "confuse_with": ["Analogous Estimating (类比估算)"], "knowledge_point_ids": []},
    {"term_en": "Bottom-up Estimating", "term_zh": "自下而上估算", "tags": ["估算技术"], "tip": "对底层工作包逐个进行详尽估算，然后自下而上层层汇总，准确度最高但耗时费力", "frequency": "high", "confuse_with": ["Analogous Estimating"], "knowledge_point_ids": []},
    {"term_en": "Three-Point Estimating", "term_zh": "三点估算", "tags": ["估算技术"], "tip": "考虑不确定性，结合最乐观、最可能、最悲观三个估算值计算期望值与标准差", "frequency": "high", "confuse_with": ["PERT"], "knowledge_point_ids": ["kp_cpm_float"]},
    {"term_en": "Risk Register", "term_zh": "风险登记册", "tags": ["风险管理"], "tip": "记录识别出的所有风险的描述、根因、潜在应对措施、责任人及优先级的档案", "frequency": "high", "confuse_with": ["Risk Management Plan"], "knowledge_point_ids": ["kp_risk_strategies"]},
    {"term_en": "Risk Appetite", "term_zh": "风险偏好", "tags": ["风险管理"], "tip": "实体为了预期的回报，愿意在总体上承受的不确定性程度", "frequency": "mid", "confuse_with": ["Risk Tolerance (风险承受度)"], "knowledge_point_ids": ["kp_risk_strategies"]},
    {"term_en": "Risk Tolerance", "term_zh": "风险承受度", "tags": ["风险管理"], "tip": "组织或个人能够承受的风险偏差最大额度与边界指标", "frequency": "mid", "confuse_with": ["Risk Threshold (风险临界值)"], "knowledge_point_ids": ["kp_risk_strategies"]},
    {"term_en": "Risk Mitigation", "term_zh": "风险减轻", "tags": ["风险管理"], "tip": "采取前置干预措施将风险发生概率或后果影响降低到可接受的限度内", "frequency": "high", "confuse_with": ["Risk Avoidance (风险规避)"], "knowledge_point_ids": ["kp_risk_strategies"]},
    {"term_en": "Risk Transference", "term_zh": "风险转移", "tags": ["风险管理"], "tip": "将风险带来的负面后果和应对管理权利转让给第三方（如买保险、外包）", "frequency": "high", "confuse_with": ["Risk Sharing (风险分享)"], "knowledge_point_ids": ["kp_risk_strategies"]},
    {"term_en": "Risk Avoidance", "term_zh": "风险规避", "tags": ["风险管理"], "tip": "通过改变项目管理计划彻底消除具体威胁或隔离受影响目标", "frequency": "high", "confuse_with": ["Risk Mitigation"], "knowledge_point_ids": ["kp_risk_strategies"]},
    {"term_en": "Risk Acceptance", "term_zh": "风险接受", "tags": ["风险管理"], "tip": "认识到风险存在并决定不采取主动预防措施，通常建立应急储备（主动接受）", "frequency": "high", "confuse_with": ["Risk Avoidance"], "knowledge_point_ids": ["kp_risk_strategies"]},
    {"term_en": "Fixed Price Contract", "term_zh": "固定总价合同 (FFP)", "tags": ["采购管理", "核心分类"], "tip": "对工作范围定义完备的项目设定总价，买方承担最小成本风险，卖方风险最大", "frequency": "high", "confuse_with": ["Cost Reimbursable Contract"], "knowledge_point_ids": ["kp_contract_types"]},
    {"term_en": "Cost Reimbursable Contract", "term_zh": "成本补偿合同", "tags": ["采购管理", "核心分类"], "tip": "向卖方支付实际成本加上一定利润费用，常用于范围模糊探索型项目，买方风险大", "frequency": "high", "confuse_with": ["Fixed Price Contract"], "knowledge_point_ids": ["kp_contract_types"]},
    {"term_en": "Time and Material Contract (T&M)", "term_zh": "工料合同", "tags": ["采购管理", "核心分类"], "tip": "按工时费率与材料成本结算，兼具总价与成本补偿特征，常用于紧急外包支持", "frequency": "high", "confuse_with": ["Cost Plus Fixed Fee"], "knowledge_point_ids": ["kp_contract_types"]},
    {"term_en": "Scrum Framework", "term_zh": "敏捷Scrum框架", "tags": ["敏捷开发", "软件工程"], "tip": "包含 3 种角色 (PO/SM/DevTeam)、3 种工件、5 种核心事件的轻量敏捷框架", "frequency": "high", "confuse_with": ["Kanban", "XP"], "knowledge_point_ids": []},
    {"term_en": "Sprint", "term_zh": "冲刺 (敏捷迭代)", "tags": ["敏捷开发"], "tip": "为期 1~4 周时间盒 (Timebox) 固定的敏捷开发周期，产出潜在可交付增量", "frequency": "high", "confuse_with": ["Iteration"], "knowledge_point_ids": []},
    {"term_en": "Product Backlog", "term_zh": "产品待办列表", "tags": ["敏捷开发"], "tip": "由产品负责人 (PO) 负责梳理并按业务价值严格排序的所有产品需求清单", "frequency": "high", "confuse_with": ["Sprint Backlog"], "knowledge_point_ids": []},
    {"term_en": "Sprint Backlog", "term_zh": "冲刺待办列表", "tags": ["敏捷开发"], "tip": "团队在当前冲刺中承诺完成的工作项及相应技术任务分解清单", "frequency": "high", "confuse_with": ["Product Backlog"], "knowledge_point_ids": []},
    {"term_en": "User Story", "term_zh": "用户故事", "tags": ["敏捷开发", "需求管理"], "tip": "从用户视角描述业务价值的标准句式：作为[角色]，我希望[功能]，以便于[价值]", "frequency": "high", "confuse_with": ["Use Case (用例)"], "knowledge_point_ids": []},
    {"term_en": "Burndown Chart", "term_zh": "燃尽图", "tags": ["敏捷开发", "进度监控"], "tip": "展示随时间推移剩余工作量递减趋势的敏捷监控图表，横轴时间，纵轴剩余点数", "frequency": "high", "confuse_with": ["Burnup Chart (燃起图)"], "knowledge_point_ids": []},
    {"term_en": "IaaS (Infrastructure as a Service)", "term_zh": "基础设施即服务", "tags": ["云计算", "核心模式"], "tip": "提供虚拟化算力、存储和网络等底层基础资源，用户负责配置系统与软件", "frequency": "high", "confuse_with": ["PaaS", "SaaS"], "knowledge_point_ids": ["kp_cloud_computing"]},
    {"term_en": "PaaS (Platform as a Service)", "term_zh": "平台即服务", "tags": ["云计算", "核心模式"], "tip": "提供应用开发、测试与部署的中间件环境，用户只需关注业务代码与数据", "frequency": "high", "confuse_with": ["IaaS", "SaaS"], "knowledge_point_ids": ["kp_cloud_computing"]},
    {"term_en": "SaaS (Software as a Service)", "term_zh": "软件即服务", "tags": ["云计算", "核心模式"], "tip": "通过网络直接提供终端软件应用服务，开箱即用，无需用户维护任何底层架构", "frequency": "high", "confuse_with": ["PaaS", "IaaS"], "knowledge_point_ids": ["kp_cloud_computing"]},
    {"term_en": "Cloud Computing", "term_zh": "云计算", "tags": ["信息技术发展"], "tip": "通过网络按需访问可配置计算资源共享池的弹性服务交付模式", "frequency": "high", "confuse_with": ["Edge Computing (边缘计算)"], "knowledge_point_ids": ["kp_cloud_computing"]},
    {"term_en": "Big Data (5V Characteristics)", "term_zh": "大数据 (5V特征)", "tags": ["信息技术发展"], "tip": "大量 (Volume)、高速 (Velocity)、多样 (Variety)、低价值密度 (Value)、真实性 (Veracity)", "frequency": "high", "confuse_with": ["Data Warehouse"], "knowledge_point_ids": []},
    {"term_en": "IoT (Internet of Things)", "term_zh": "物联网", "tags": ["信息技术发展"], "tip": "感知层 (传感器/RFID)、网络层 (传输通信)、应用层 (智能应用分析) 三层架构", "frequency": "high", "confuse_with": ["CPS (信息物理系统)"], "knowledge_point_ids": []},
    {"term_en": "Artificial Intelligence (AI)", "term_zh": "人工智能", "tags": ["新技术发展"], "tip": "研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统", "frequency": "high", "confuse_with": ["Machine Learning"], "knowledge_point_ids": []},
    {"term_en": "Blockchain", "term_zh": "区块链", "tags": ["新技术发展"], "tip": "分布式数据存储、点对点传输、共识机制、加密算法等计算机技术的新型应用模式", "frequency": "mid", "confuse_with": ["Distributed Ledger"], "knowledge_point_ids": []},
    {"term_en": "Digital Transformation", "term_zh": "数字化转型", "tags": ["信息化发展"], "tip": "利用新一代信息技术驱动业务模式创新、流程再造与组织深刻变革", "frequency": "high", "confuse_with": ["Digitization (数字化)"], "knowledge_point_ids": []},
    {"term_en": "Stakeholder", "term_zh": "干系人", "tags": ["干系人管理", "通用基础"], "tip": "能影响项目决策、活动或结果，或受其影响的个人、群体或组织", "frequency": "high", "confuse_with": ["Shareholder (股东)"], "knowledge_point_ids": ["kp_stakeholder_matrix"]},
    {"term_en": "Lessons Learned Register", "term_zh": "经验教训登记册", "tags": ["知识管理", "整体管理"], "tip": "在项目各阶段持续记录改进得失并在收尾时归档入组织过程资产 (OPA) 的知识文件", "frequency": "high", "confuse_with": ["Issue Log (问题日志)"], "knowledge_point_ids": []},
    {"term_en": "Project Charter", "term_zh": "项目章程", "tags": ["整体管理", "立项文件"], "tip": "由发起人正式签署发布、授权项目经理合法动用组织资源的立项文件", "frequency": "high", "confuse_with": ["Project Management Plan"], "knowledge_point_ids": ["kp_charter_pm"]},
    {"term_en": "Governance", "term_zh": "项目治理", "tags": ["组织环境"], "tip": "符合组织商业模式的监督、控制、决策框架，确保项目战略对齐", "frequency": "mid", "confuse_with": ["Management (管理)"], "knowledge_point_ids": []}
]

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "data", "learn")
    os.makedirs(base_dir, exist_ok=True)

    # 1. points_seed.json
    points_payload = {
        "chapters": CHAPTERS,
        "points": POINTS
    }
    points_file = os.path.join(base_dir, "points_seed.json")
    with open(points_file, "w", encoding="utf-8") as f:
        json.dump(points_payload, f, ensure_ascii=False, indent=2)
    print(f"[OK] Generated {len(CHAPTERS)} chapters and {len(POINTS)} points to: {points_file}")

    # 2. glossary_seed.json
    glossary_file = os.path.join(base_dir, "glossary_seed.json")
    # Enrich glossary with unique id
    glossary_list = []
    for idx, item in enumerate(GLOSSARY_TERMS, start=1):
        clean_en = item["term_en"].split("(")[0].strip().lower().replace(" ", "_").replace("-", "_").replace("/", "_")
        term_id = f"term_{clean_en[:28]}"
        glossary_list.append({
            "id": term_id,
            "term_en": item["term_en"],
            "term_zh": item["term_zh"],
            "tags": item["tags"],
            "tip": item["tip"],
            "frequency": item["frequency"],
            "confuse_with": item["confuse_with"],
            "knowledge_point_ids": item.get("knowledge_point_ids", [])
        })

    with open(glossary_file, "w", encoding="utf-8") as f:
        json.dump(glossary_list, f, ensure_ascii=False, indent=2)
    print(f"[OK] Generated {len(glossary_list)} glossary terms to: {glossary_file}")

if __name__ == "__main__":
    main()
