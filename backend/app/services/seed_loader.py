import json
import os
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User
from app.models.agent_key import AgentApiKey
from app.models.question import Question

logger = logging.getLogger(__name__)

def ensure_schema_migrations(db: Session):
    try:
        result = db.execute(text("PRAGMA table_info(questions)")).fetchall()
        existing_cols = {row[1] for row in result}
        if existing_cols:
            if "knowledge_point_ids" not in existing_cols:
                db.execute(text("ALTER TABLE questions ADD COLUMN knowledge_point_ids JSON"))
                logger.info("Migrated questions table: added knowledge_point_ids")
            if "glossary_ids" not in existing_cols:
                db.execute(text("ALTER TABLE questions ADD COLUMN glossary_ids JSON"))
                logger.info("Migrated questions table: added glossary_ids")
            if "is_english_term" not in existing_cols:
                db.execute(text("ALTER TABLE questions ADD COLUMN is_english_term BOOLEAN DEFAULT 0"))
                logger.info("Migrated questions table: added is_english_term")
            db.commit()

        # Migrate materials table
        res_mat = db.execute(text("PRAGMA table_info(materials)")).fetchall()
        mat_cols = {row[1] for row in res_mat}
        if mat_cols:
            if "is_public" not in mat_cols:
                db.execute(text("ALTER TABLE materials ADD COLUMN is_public BOOLEAN DEFAULT 0"))
                logger.info("Migrated materials table: added is_public")
            if "is_recommended" not in mat_cols:
                db.execute(text("ALTER TABLE materials ADD COLUMN is_recommended BOOLEAN DEFAULT 0"))
                logger.info("Migrated materials table: added is_recommended")
            if "sort_order" not in mat_cols:
                db.execute(text("ALTER TABLE materials ADD COLUMN sort_order INTEGER DEFAULT 0"))
                logger.info("Migrated materials table: added sort_order")
            if "description" not in mat_cols:
                db.execute(text("ALTER TABLE materials ADD COLUMN description TEXT"))
                logger.info("Migrated materials table: added description")
            if "year" not in mat_cols:
                db.execute(text("ALTER TABLE materials ADD COLUMN year VARCHAR(32)"))
                logger.info("Migrated materials table: added year")
            if "download_url" not in mat_cols:
                db.execute(text("ALTER TABLE materials ADD COLUMN download_url VARCHAR(512)"))
                logger.info("Migrated materials table: added download_url")
            db.commit()

        # Migrate users table
        res_u = db.execute(text("PRAGMA table_info(users)")).fetchall()
        user_cols = {row[1] for row in res_u}
        if user_cols:
            if "ai_quota" not in user_cols:
                db.execute(text("ALTER TABLE users ADD COLUMN ai_quota INTEGER"))
                logger.info("Migrated users table: added ai_quota")
            if "is_active" not in user_cols:
                db.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1"))
                logger.info("Migrated users table: added is_active")
            if "ai_enabled" not in user_cols:
                db.execute(text("ALTER TABLE users ADD COLUMN ai_enabled BOOLEAN DEFAULT 1"))
                logger.info("Migrated users table: added ai_enabled")
            db.commit()
    except Exception as e:
        logger.warning(f"Schema migration note: {e}")
        db.rollback()


def load_question_banks(db: Session):
    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    files = [
        os.path.join(data_dir, "seed_questions.json"),
        os.path.join(data_dir, "extracted_materials_questions.json"),
        os.path.join(data_dir, "extra_generated_questions.json"),
    ]
    existing = {
        (row[0] or "")[:80]
        for row in db.query(Question.stem).all()
    }
    inserted = 0
    for path in files:
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                items = json.load(f)
            if not isinstance(items, list):
                continue
            for item in items:
                stem = (item.get("stem") or "").strip()
                if not stem:
                    continue
                key = stem[:80]
                if key in existing:
                    continue
                db.add(Question(
                    subject=item.get("subject", "basic"),
                    chapter=item.get("chapter", "综合知识"),
                    knowledge=item.get("knowledge", "核心考点"),
                    stem=stem,
                    options=item.get("options"),
                    correct_answer=item.get("correct_answer") or "",
                    analysis=item.get("analysis"),
                    rubrics=item.get("rubrics"),
                    knowledge_point_ids=item.get("knowledge_point_ids"),
                    glossary_ids=item.get("glossary_ids"),
                    is_english_term=bool(item.get("is_english_term", False)),
                    source=item.get("source", "ai-generated"),
                    difficulty=item.get("difficulty", "medium"),
                ))
                existing.add(key)
                inserted += 1
            db.commit()
            logger.info(f"Question bank {os.path.basename(path)} processed.")
        except Exception as e:
            logger.error(f"Failed to load question bank {path}: {e}")
            db.rollback()
    if inserted:
        logger.info(f"Inserted {inserted} new questions from seed banks.")
    else:
        logger.info("Question banks up to date, no new stems inserted.")


def init_seed_data(db: Session):
    # 0. Ensure schema migrations
    ensure_schema_migrations(db)
    # 1. Initialize Admin user if password provided in environment
    if settings.INITIAL_ADMIN_PASSWORD:
        admin_user = db.query(User).filter(User.username == settings.INITIAL_ADMIN_USERNAME).first()
        if not admin_user:
            admin_user = User(
                username=settings.INITIAL_ADMIN_USERNAME,
                hashed_password=get_password_hash(settings.INITIAL_ADMIN_PASSWORD),
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            logger.info(f"Initialized admin user: {settings.INITIAL_ADMIN_USERNAME}")

    # 1.1 Ensure user wwr (mko0nji9, ai_quota=50000)
    wwr_user = db.query(User).filter(User.username == "wwr").first()
    if not wwr_user:
        wwr_user = User(
            username="wwr",
            hashed_password=get_password_hash("mko0nji9"),
            role="user",
            ai_quota=50000,
            is_active=True,
            ai_enabled=True
        )
        db.add(wwr_user)
        db.commit()
        logger.info("Initialized user wwr with 50000 AI quota.")
    else:
        wwr_user.hashed_password = get_password_hash("mko0nji9")
        wwr_user.ai_quota = 50000
        wwr_user.is_active = True
        wwr_user.ai_enabled = True
        db.commit()
        logger.info("Updated user wwr credentials and set AI quota to 50000.")

    # 1.2 Ensure user sig288 (ai_quota=5000)
    sig288_user = db.query(User).filter(User.username == "sig288").first()
    if sig288_user:
        sig288_user.ai_quota = 5000
        sig288_user.ai_enabled = True
        sig288_user.is_active = True
        db.commit()
        logger.info("Updated user sig288 AI quota to 5000.")
    else:
        sig288_user = User(
            username="sig288",
            hashed_password=get_password_hash("Password123!"),
            role="user",
            ai_quota=5000,
            is_active=True,
            ai_enabled=True
        )
        db.add(sig288_user)
        db.commit()
        logger.info("Initialized user sig288 with 5000 AI quota.")

    # 2. Initialize default Agent API Key if provided in environment
    if settings.DEFAULT_AGENT_KEY:
        default_key = db.query(AgentApiKey).filter(AgentApiKey.key == settings.DEFAULT_AGENT_KEY).first()
        if not default_key:
            default_key = AgentApiKey(
                key=settings.DEFAULT_AGENT_KEY,
                name="Default Server Agent Key",
                is_active=True
            )
            db.add(default_key)
            db.commit()
        logger.info(f"Initialized default agent key: {settings.DEFAULT_AGENT_KEY}")

    # 3. Load / upsert question banks (seed + 资料库抽取 + 自编)
    load_question_banks(db)

    # 4. Load knowledge chapters and points seed
    from app.models.learn import KnowledgeChapter, KnowledgePoint, GlossaryTerm

    learn_data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "learn")
    points_seed_file = os.path.join(learn_data_dir, "points_seed.json")
    if os.path.exists(points_seed_file):
        try:
            with open(points_seed_file, "r", encoding="utf-8") as f:
                points_data = json.load(f)

            chapters = points_data.get("chapters", [])
            for ch in chapters:
                exist_ch = db.query(KnowledgeChapter).filter(KnowledgeChapter.id == ch["id"]).first()
                if not exist_ch:
                    db.add(KnowledgeChapter(
                        id=ch["id"],
                        code=ch["code"],
                        title=ch["title"],
                        sort_order=ch.get("sort_order", 0)
                    ))
                else:
                    exist_ch.code = ch["code"]
                    exist_ch.title = ch["title"]
                    exist_ch.sort_order = ch.get("sort_order", 0)

            points = points_data.get("points", [])
            for p in points:
                exist_p = db.query(KnowledgePoint).filter(KnowledgePoint.id == p["id"]).first()
                if not exist_p:
                    db.add(KnowledgePoint(
                        id=p["id"],
                        chapter_id=p["chapter_id"],
                        title=p["title"],
                        frequency=p.get("frequency", "mid"),
                        est_minutes=p.get("est_minutes", 10),
                        summary_md=p["summary_md"],
                        formula_md=p.get("formula_md"),
                        domain_tags=p.get("domain_tags"),
                        glossary_ids=p.get("glossary_ids"),
                        question_ids=p.get("question_ids", []),
                        sort_order=p.get("sort_order", 0)
                    ))
                else:
                    exist_p.chapter_id = p["chapter_id"]
                    exist_p.title = p["title"]
                    exist_p.frequency = p.get("frequency", "mid")
                    exist_p.est_minutes = p.get("est_minutes", 10)
                    exist_p.summary_md = p["summary_md"]
                    exist_p.formula_md = p.get("formula_md")
                    exist_p.domain_tags = p.get("domain_tags")
                    exist_p.glossary_ids = p.get("glossary_ids")
                    exist_p.sort_order = p.get("sort_order", 0)
            db.commit()
            logger.info(f"Initialized/Updated {len(chapters)} chapters and {len(points)} knowledge points.")
        except Exception as e:
            logger.error(f"Failed to load points seed data: {e}")
            db.rollback()

    # 5. Load glossary terms seed
    glossary_seed_file = os.path.join(learn_data_dir, "glossary_seed.json")
    if os.path.exists(glossary_seed_file):
        try:
            with open(glossary_seed_file, "r", encoding="utf-8") as f:
                glossary_data = json.load(f)

            terms_count = db.query(GlossaryTerm).count()
            if terms_count == 0:
                for t in glossary_data:
                    db.add(GlossaryTerm(
                        id=t["id"],
                        term_en=t["term_en"],
                        term_zh=t["term_zh"],
                        tags=t.get("tags"),
                        tip=t.get("tip"),
                        frequency=t.get("frequency", "mid"),
                        confuse_with=t.get("confuse_with"),
                        knowledge_point_ids=t.get("knowledge_point_ids", [])
                    ))
                db.commit()
                logger.info(f"Initialized {len(glossary_data)} glossary terms.")
        except Exception as e:
            logger.error(f"Failed to load glossary seed data: {e}")
            db.rollback()

    # 6. Relink questions to knowledge points and glossary terms
    try:
        point_kw_map = {
            "kp_ch01_info_concept": ["香农", "消除不确定性", "精确性", "完整性", "依附性", "信息传输模型"],
            "kp_ch01_digital_china": ["数字中国", "2522", "数据要素", "数据资产", "两化融合"],
            "kp_ch01_new_infra": ["新基建", "信息基础设施", "融合基础设施", "创新基础设施", "算力"],
            "kp_ch01_sys_lifecycle": ["系统生命周期", "系统规划", "系统分析", "系统设计", "系统实施", "逻辑模型", "物理模型"],
            "kp_cloud_computing": ["云计算", "IaaS", "PaaS", "SaaS", "公有云", "私有云", "混合云"],
            "kp_ch02_iot_tech": ["物联网", "RFID", "感知层", "射频识别", "ZigBee", "传感网"],
            "kp_ch02_bigdata_ai": ["大数据", "5V", "Volume", "Velocity", "人工智能", "机器学习", "大模型", "Transformer"],
            "kp_ch02_blockchain": ["区块链", "分布式账本", "智能合约", "PoW", "PoS", "去中心化"],
            "kp_ch03_integration_levels": ["系统集成", "数据集成", "应用集成", "业务集成", "信息孤岛"],
            "kp_ch03_itss_pptr": ["ITSS", "PPTR", "人员、过程、技术、资源", "服务交付", "持续改进"],
            "kp_ch03_itil_itsm": ["ITIL", "ITSM", "事件管理", "问题管理", "CMDB", "配置管理数据库"],
            "kp_ch03_supervision": ["工程监理", "三控四管一协调", "监理人", "监理单位"],
            "kp_sec_baseline": ["信息安全", "机密性", "完整性", "可用性", "等保2.0", "等级保护", "第三级"],
            "kp_ch04_osi_tcpmtcp": ["OSI", "TCP/IP", "TCP", "UDP", "三次握手", "ARP", "ICMP"],
            "kp_ch04_pki_crypto": ["对称加密", "非对称加密", "数字签名", "CA认证", "RSA", "AES", "SM2", "SM4"],
            "kp_ch04_firewall_ids": ["防火墙", "IDS", "IPS", "入侵检测", "入侵防御", "VPN", "蜜罐"],
            "kp_ch05_sdlc_models": ["瀑布模型", "原型模型", "增量模型", "螺旋模型", "敏捷开发", "Scrum", "Sprint"],
            "kp_ch05_uml_diagrams": ["UML", "用例图", "类图", "时序图", "顺序图", "活动图", "状态机图"],
            "kp_ch05_software_testing": ["单元测试", "集成测试", "黑盒测试", "白盒测试", "等价类", "边界值", "语句覆盖", "路径覆盖"],
            "kp_ch05_architecture_patterns": ["微服务", "SOA", "分层架构", "设计模式", "单例模式", "工厂模式", "观察者模式"],
            "kp_ch06_project_initiation": ["项目建议书", "可行性研究", "初可", "详可", "立项申请", "评估与决策"],
            "kp_ch06_bidding_timeline": ["招投标", "截标", "招标文件", "投标文件", "开标", "20日", "15日", "30日"],
            "kp_ch06_bidding_eval": ["评标委员会", "综合评估法", "最低投标价法", "废标", "2/3", "五人以上单数"],
            "kp_ch06_procurement_mode": ["政府采购", "公开招标", "邀请招标", "竞争性谈判", "单一来源", "询价"],
            "kp_charter_pm": ["项目章程", "项目发起人", "Sponsor", "项目经理授权", "启动过程组"],
            "kp_ccb_change": ["CCB", "变更控制", "变更申请", "基准更新", "变更日志"],
            "kp_ch07_mgmt_plan": ["项目管理计划", "三大基准", "子计划", "指导与管理项目工作"],
            "kp_ch07_project_closing": ["行政收尾", "合同收尾", "经验教训", "组织过程资产", "移交"],
            "kp_wbs_decomp": ["WBS", "工作分解结构", "工作包", "范围基准", "100%规则", "WBS词典"],
            "kp_ch08_collect_req": ["需求收集", "需求跟踪矩阵", "RTM", "德尔菲", "头脑风暴", "焦点小组"],
            "kp_ch08_validate_scope": ["确认范围", "范围确认", "范围蔓延", "镀金", "核实的可交付成果", "验收"],
            "kp_ch08_define_scope": ["定义范围", "范围说明书", "除外责任", "制约因素", "假设条件"],
            "kp_cpm_float": ["关键路径", "总时差", "自由时差", "双代号", "单代号", "早始", "迟始", "CPM"],
            "kp_schedule_compress": ["赶工", "快速跟进", "进度压缩", "Crashing", "Fast Tracking"],
            "kp_ch09_pert_estimate": ["三点估算", "PERT", "最乐观", "最悲观", "最可能", "贝塔分布", "标准差"],
            "kp_ch09_dependencies": ["FS", "FF", "SS", "SF", "提前量", "滞后量", "紧前活动", "紧后活动"],
            "kp_evm_cpi": ["挣值", "EVM", "CPI", "SPI", "完工预测", "BAC", "成本偏差", "CV", "SV", "PV", "EV", "AC", "EAC"],
            "kp_ch10_cost_types": ["直接成本", "间接成本", "固定成本", "可变成本", "沉没成本", "机会成本"],
            "kp_ch10_budget_reserves": ["应急储备", "管理储备", "成本基准", "成本预算", "已知未知", "未知未知"],
            "kp_ch10_estimate_techniques": ["类比估算", "参数估算", "自下而上估算"],
            "kp_qa_vs_qc": ["质量保证", "质量控制", "QA", "QC", "质量审计", "PDCA"],
            "kp_ch11_seven_tools": ["老七种", "因果图", "鱼骨图", "帕累托图", "控制图", "直方图", "散点图", "核查表"],
            "kp_ch11_cost_of_quality": ["质量成本", "COQ", "一致性成本", "非一致性成本", "预防成本", "评估成本", "内部失败", "外部失败"],
            "kp_ch11_quality_audit": ["质量审计", "过程改进", "最佳实践"],
            "kp_conflict_mgmt": ["冲突解决", "合作", "妥协", "强迫", "包容", "回避", "双赢"],
            "kp_ch12_tuckman_model": ["塔克曼", "形成阶段", "震荡阶段", "规范阶段", "发挥阶段", "解散阶段"],
            "kp_ch12_motivation_theories": ["马斯洛", "双因素", "保健因素", "激励因素", "X理论", "Y理论", "期望理论"],
            "kp_ch12_raci_matrix": ["RACI", "责任分配矩阵", "团队章程", "Accountable"],
            "kp_comm_channel": ["沟通渠道", "沟通方式", "交互式", "推式", "拉式", "N*(N-1)/2"],
            "kp_ch13_comm_model": ["沟通模型", "编码", "解码", "噪声", "5C原则"],
            "kp_ch13_plan_comm": ["沟通管理计划", "沟通需求", "信息发布", "问题升级"],
            "kp_ch13_manage_monitor_comm": ["管理沟通", "监督沟通", "工作绩效报告"],
            "kp_risk_strategies": ["消极风险", "积极风险", "规避", "转移", "减轻", "接受", "开拓", "分享", "提高"],
            "kp_ch14_risk_process": ["风险登记册", "风险责任人", "次生风险", "残余风险", "监督风险"],
            "kp_ch14_emv_decision_tree": ["EMV", "预期货币价值", "决策树", "净收益"],
            "kp_ch14_qualitative_matrix": ["定性风险分析", "概率影响矩阵", "观察清单"],
            "kp_contract_types": ["总价合同", "成本补偿", "工料合同", "FFP", "CPFF", "CPIF", "T&M"],
            "kp_ch15_sow_make_buy": ["自制或外购", "SOW", "采购工作说明书", "Make-or-Buy"],
            "kp_ch15_cpif_calc": ["CPIF", "成本加激励费用", "目标成本", "目标利润", "实际成本分担"],
            "kp_ch15_claims_disputes": ["合同索赔", "28天", "索赔意向", "争议解决", "仲裁", "诉讼"],
            "kp_stakeholder_matrix": ["干系人", "权力利益方格", "重点管理", "令其满意", "随时告知", "监督"],
            "kp_ch16_engagement_matrix": ["干系人参与度", "不知晓", "抵制", "中立", "支持", "领导", "C状态", "D状态"],
            "kp_ch16_register_plan": ["干系人登记册", "识别干系人", "干系人分析"],
            "kp_ch16_manage_engagement": ["管理干系人参与", "监督干系人参与"],
            "kp_ch17_ip_copyright": ["著作权法", "软件保护条例", "署名权", "保护期", "50年", "职务作品"],
            "kp_ch17_civil_code_contract": ["民法典", "合同编", "要约", "要约邀请", "承诺", "中标通知书", "不可抗力"],
            "kp_ch17_standards_classification": ["标准化法", "国家标准", "GB", "GB/T", "强制性标准", "推荐性标准"],
            "kp_ch17_cyber_security_law": ["网络安全法", "数据安全法", "个人信息保护", "日志留存", "六个月", "180天"]
        }

        questions = db.query(Question).all()
        updated_q = 0
        for q in questions:
            matched_pids = list(q.knowledge_point_ids or [])
            combined_text = f"{q.knowledge} {q.stem} {q.analysis or ''}"
            for pid, kws in point_kw_map.items():
                if any(kw in combined_text for kw in kws):
                    if pid not in matched_pids:
                        matched_pids.append(pid)

            # Check if english term
            matched_gids = list(q.glossary_ids or [])
            is_eng = q.is_english_term or False
            if "which of the following" in q.stem.lower() or "refer to" in q.stem.lower() or "defined as" in q.stem.lower():
                is_eng = True

            if matched_pids != (q.knowledge_point_ids or []) or is_eng != q.is_english_term:
                q.knowledge_point_ids = matched_pids
                q.is_english_term = is_eng
                updated_q += 1

        if updated_q > 0:
            db.commit()
            logger.info(f"Linked {updated_q} questions to knowledge points.")
    except Exception as e:
        logger.error(f"Error mapping questions to points: {e}")
        db.rollback()

    # 7. Initialize curated public study materials
    try:
        from app.models.material import Material
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = os.path.dirname(current_file_dir)
        backend_dir = os.path.dirname(app_dir)
        data_candidates = [
            os.path.join(backend_dir, "data", "materials", "curated_manifest.json"),
            os.path.join(app_dir, "data", "materials", "curated_manifest.json"),
            "/app/data/materials/curated_manifest.json",
            "backend/data/materials/curated_manifest.json"
        ]
        manifest_path = None
        for p in data_candidates:
            if os.path.exists(p):
                manifest_path = p
                break


        if manifest_path:
            with open(manifest_path, "r", encoding="utf-8") as f:
                curated_items = json.load(f)

            pub_dir = os.path.join(os.path.dirname(manifest_path), "public")
            count_mat = 0
            for item in curated_items:
                mat = db.query(Material).filter(Material.id == item["id"]).first()
                local_fpath = os.path.join(pub_dir, item["filename"])
                if not mat:
                    mat = Material(
                        id=item["id"],
                        user_id="system",
                        title=item["title"],
                        file_type=item["file_type"],
                        category=item["category"],
                        chapter=item.get("chapter"),
                        file_path=local_fpath,
                        file_size=item.get("file_size", 0),
                        is_public=True,
                        is_recommended=item.get("is_recommended", True),
                        sort_order=item.get("sort_order", 0),
                        description=item.get("description"),
                        year=item.get("year", "2026")
                    )
                    db.add(mat)
                    count_mat += 1
                else:
                    mat.title = item["title"]
                    mat.category = item["category"]
                    mat.chapter = item.get("chapter")
                    mat.file_path = local_fpath
                    mat.is_public = True
                    mat.is_recommended = item.get("is_recommended", True)
                    mat.sort_order = item.get("sort_order", 0)
                    mat.description = item.get("description")
                    mat.year = item.get("year", "2026")

            db.commit()
            if count_mat > 0:
                logger.info(f"Initialized {count_mat} curated public study materials.")
    except Exception as e:
        logger.error(f"Failed to load curated materials: {e}")
        db.rollback()


