# -*- coding: utf-8 -*-
"""
Parser and Importer for 2024-2026 Ruankao Study Materials.
Converts OCR extracted text and case studies into structured questions
and imports them into the SQLite database and JSON export.
Uses pure standard library (sqlite3, json, re, uuid) for zero-dependency execution.
"""
import os
import re
import sys
import json
import uuid
import sqlite3
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

def map_page_to_chapter(page_no: int) -> str:
    if page_no <= 40:
        return "第1章 信息化发展"
    elif page_no <= 80:
        return "第2章 信息技术发展"
    elif page_no <= 130:
        return "第3章 信息系统集成及服务"
    elif page_no <= 210:
        return "第4章 信息安全与网络"
    elif page_no <= 300:
        return "第5章 软件工程与系统架构"
    elif page_no <= 350:
        return "第6章 项目立项与招投标"
    elif page_no <= 370:
        return "第7章 项目整体管理"
    elif page_no <= 400:
        return "第8章 项目范围管理"
    elif page_no <= 430:
        return "第9章 项目进度管理"
    elif page_no <= 450:
        return "第10章 项目成本管理"
    elif page_no <= 470:
        return "第11章 项目质量管理"
    elif page_no <= 500:
        return "第12章 项目资源管理"
    elif page_no <= 520:
        return "第13章 项目沟通管理"
    elif page_no <= 550:
        return "第14章 项目风险管理"
    elif page_no <= 570:
        return "第15章 项目采购管理"
    elif page_no <= 585:
        return "第16章 项目干系人管理"
    else:
        return "第17章 法律法规与标准化"

def infer_chapter_by_keywords(text: str) -> str:
    kw_map = [
        (["范围", "WBS", "工作包", "需求跟踪矩阵", "范围基准", "确认范围"], "第8章 项目范围管理"),
        (["关键路径", "总时差", "自由时差", "双代号", "单代号", "甘特图", "紧前", "紧后", "进度偏差", "SPI", "工期"], "第9章 项目进度管理"),
        (["成本", "挣值", "EVM", "PV", "EV", "AC", "CV", "SV", "CPI", "BAC", "ETC", "EAC"], "第10章 项目成本管理"),
        (["质量", "因果图", "鱼骨图", "帕累托", "直方图", "控制图", "质量保证", "质量控制"], "第11章 项目质量管理"),
        (["团队", "马斯洛", "双因素", "X理论", "Y理论", "虚拟团队", "资源日历", "资源直方图", "知识管理", "知识转移"], "第12章 项目资源管理"),
        (["沟通渠道", "沟通方式", "交互式沟通", "推式沟通", "拉式沟通"], "第13章 项目沟通管理"),
        (["风险", "定性风险", "定量风险", "风险应对", "规避", "转移", "减轻", "接受", "开拓", "分享", "提高", "风险登记册"], "第14章 项目风险管理"),
        (["采购", "招标", "投标", "合同", "固定总价", "成本补偿", "工料合同", "索赔"], "第15章 项目采购管理"),
        (["干系人", "相关方", "权力/利益", "参与度评估矩阵", "凸显模型"], "第16章 项目干系人管理"),
        (["变更", "CCB", "变更控制", "基线", "配置项", "配置库", "版本控制"], "第7章 项目整体管理"),
        (["安全", "加密", "解密", "防火墙", "VPDRRC", "数字签名", "木马", "漏洞", "攻击"], "第4章 信息安全与网络"),
        (["架构", "SOA", "微服务", "设计模式", "敏捷", "Scrum", "瀑布", "测试"], "第5章 软件工程与系统架构"),
        (["标准", "国家标准", "行业标准", "团体标准", "知识产权", "著作权", "专利"], "第17章 法律法规与标准化"),
        (["人工智能", "大模型", "大数据", "云计算", "物联网", "区块链", "元宇宙", "数字化转型"], "第1章 信息化发展"),
    ]
    for keywords, ch in kw_map:
        if any(kw in text for kw in keywords):
            return ch
    return "第7章 项目整体管理"

def infer_knowledge(stem: str, analysis: str) -> str:
    candidates = [
        "过程管理", "滚动式规划", "知识转移", "信息安全空间", "WPDRRC安全模型",
        "风险应对开拓策略", "风险分类", "范围管理计划", "团体标准", "操作系统虚拟化",
        "挣值分析EVM", "关键路径法CPM", "总浮动时间", "甘特图分析", "变更控制流程",
        "WBS分解", "质量保证", "三点估算PERT", "招投标流程", "沟通渠道计算",
        "干系人管理", "配置基线管理", "数字签名机制", "大模型与人工智能",
        "数字化转型", "双代号网络图", "项目章程", "合同类型选择"
    ]
    comb = stem + " " + analysis
    for c in candidates:
        if c in comb:
            return c
    m = re.search(r'关于([^\s，。、（）]+)', stem)
    if m and len(m.group(1)) <= 12:
        return m.group(1)
    return "高频核心考点"

def parse_choice_questions_from_text(txt_path: str, source_name: str):
    if not os.path.exists(txt_path):
        print(f"File not found: {txt_path}")
        return []

    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Clean up page markers
    content = re.sub(r'=== PAGE \d+ ===', '', content)
    
    # Split questions by question numbers at line start, e.g., "\n1.", "\n2."
    lines = content.split('\n')
    raw_blocks = []
    current_block = []

    for line in lines:
        line_s = line.strip()
        m = re.match(r'^(\d+)[\.、\s](.+)$', line_s)
        if m and int(m.group(1)) <= 80:
            if current_block:
                raw_blocks.append("\n".join(current_block))
                current_block = []
            current_block.append(line_s)
        elif current_block:
            current_block.append(line_s)

    if current_block:
        raw_blocks.append("\n".join(current_block))

    print(f"[{source_name}] Found {len(raw_blocks)} candidate question blocks.")
    parsed_questions = []

    for block in raw_blocks:
        ans_m = re.search(r'【答案】\s*([A-Da-d]+)', block)
        if not ans_m:
            ans_m = re.search(r'答案[：: ]+([A-Da-d]+)', block)
        if not ans_m:
            continue
        correct_ans = ans_m.group(1).upper()

        ana_m = re.search(r'【解析】\s*(.*)', block, re.DOTALL)
        if not ana_m:
            ana_m = re.search(r'解析[：: ]+(.*)', block, re.DOTALL)
        analysis_text = ana_m.group(1).strip() if ana_m else ""

        ans_pos = ans_m.start()
        q_part = block[:ans_pos].strip()

        # Extract options A, B, C, D
        opt_pattern = r'([A-D])[\.、\s](.+?)(?=(?:[A-D][\.、\s]|\Z))'
        matches = list(re.finditer(opt_pattern, q_part, re.DOTALL))

        options = []
        if len(matches) >= 4:
            first_opt_pos = matches[0].start()
            stem = q_part[:first_opt_pos].strip()
            stem = re.sub(r'^\d+[\.、\s]+', '', stem).strip()

            for m in matches[:4]:
                opt_letter = m.group(1).upper()
                opt_content = m.group(2).strip().replace('\n', ' ')
                options.append(f"{opt_letter}. {opt_content}")
        elif len(matches) >= 2:
            first_opt_pos = matches[0].start()
            stem = q_part[:first_opt_pos].strip()
            stem = re.sub(r'^\d+[\.、\s]+', '', stem).strip()
            for m in matches:
                opt_letter = m.group(1).upper()
                opt_content = m.group(2).strip().replace('\n', ' ')
                options.append(f"{opt_letter}. {opt_content}")
        else:
            continue

        if not stem or len(stem) < 5 or len(options) < 2:
            continue

        if len(options) == 3:
            options.append("D. 以上皆非")

        chapter = None
        p_match = re.search(r'P\s*(\d{1,3})', analysis_text)
        if p_match:
            p_no = int(p_match.group(1))
            if 1 <= p_no <= 620:
                chapter = map_page_to_chapter(p_no)

        if not chapter:
            chapter = infer_chapter_by_keywords(stem + " " + analysis_text)

        knowledge = infer_knowledge(stem, analysis_text)

        parsed_questions.append({
            "subject": "basic",
            "chapter": chapter,
            "knowledge": knowledge,
            "stem": stem,
            "options": options,
            "correct_answer": correct_ans,
            "analysis": analysis_text if analysis_text else "依据第3版官方教程考点解析",
            "source": source_name,
            "difficulty": "medium"
        })

    print(f"[{source_name}] Successfully parsed {len(parsed_questions)} clean questions.")
    return parsed_questions

def get_case_questions():
    cases = [
        {
            "subject": "case",
            "chapter": "第9章 项目进度管理",
            "knowledge": "关键路径法与挣值分析EVM",
            "stem": """【2024年11月机考案例真题】某项目的甘特图与各活动数据如下表所示：
项目执行至第6天末时的数据（单位：万元），此时项目实际花费 AC = 40 万元：
活动 | 计划投资(万元) | 实际完成工作量
A    | 10             | 100%
B    | 8              | 100%
C    | 8              | 50%
D    | 6              | 100%
E    | 20             | 80%
F    | 5              | 0%
G    | 8              | 0%

【问题1】（6分）
活动D的总时差（总浮动时间）是多少天？项目的关键路径有哪些？
【问题2】（8分）
计算项目执行到第6天末的 PV、EV、AC，计算成本绩效指标 CPI 和进度绩效指标 SPI（保留两位小数），并据此判断项目的成本和进度执行绩效。
【问题3】（6分）
项目实际工期比计划工期延长了多少天？哪些活动是关键路径上的活动？""",
            "options": None,
            "correct_answer": """【问题1】（6分）
1. 活动D的总时差为 2天（2分）。
2. 项目的关键路径为：ABCG 和 AEFG（各2分，共4分）。

【问题2】（8分）
1. PV = PV_A + PV_B + 1/2*PV_C + PV_D + PV_E = 10 + 8 + 4 + 6 + 20 = 48 万元（2分）
2. EV = 10*100% + 8*100% + 8*50% + 6*100% + 20*80% = 10 + 8 + 4 + 6 + 16 = 44 万元（2分）
3. AC = 40 万元
4. SPI = EV / PV = 44 / 48 ≈ 0.92（1分）
5. CPI = EV / AC = 44 / 40 = 1.10（1分）
6. 绩效判断：因为 SPI < 1，说明项目进度落后/延误；因为 CPI > 1，说明项目成本节约/结余（2分）。

【问题3】（6分）
1. 项目实际工期比计划工期延长了 1天（3分）。
2. 活动 C 和 E 是关键路径上的活动（3分）。""",
            "analysis": "【核心考点】甘特图分析、时标网络计划总时差计算、挣值分析公式（PV/EV/AC/CPI/SPI）及绩效偏差诊断（SPI<1进度滞后，CPI>1成本节约）。",
            "rubrics": [
                {"point": "活动D总时差2天", "score": 2, "keywords": ["2天", "总时差2", "总时差为2"]},
                {"point": "关键路径ABCG和AEFG", "score": 4, "keywords": ["ABCG", "AEFG"]},
                {"point": "PV=48万元", "score": 2, "keywords": ["48", "PV=48"]},
                {"point": "EV=44万元", "score": 2, "keywords": ["44", "EV=44"]},
                {"point": "SPI=0.92进度滞后", "score": 2, "keywords": ["0.92", "滞后", "延误", "落后"]},
                {"point": "CPI=1.10成本节约", "score": 2, "keywords": ["1.1", "节约", "结余", "低于预算"]},
                {"point": "实际工期延长1天", "score": 3, "keywords": ["1天", "延长1", "延误1"]},
                {"point": "关键路径活动C和E", "score": 3, "keywords": ["C", "E"]}
            ],
            "source": "2024年11月中项案例真题",
            "difficulty": "hard"
        },
        {
            "subject": "case",
            "chapter": "第10章 项目成本管理",
            "knowledge": "挣值分析与完工预测EAC",
            "stem": """【经典母题·挣值预测案例】
某软件研发项目总预算 BAC = 100 万元，计划工期为 10 个月。在项目进行到第 5 个月末时，项目经理对项目进展进行了盘点：
1. 实际已完成工作量为项目总量的 40%；
2. 实际已经累计花费 AC = 50 万元。

【问题1】（6分）
计算项目第5月末时的计划值 PV、挣值 EV、成本偏差 CV 和进度偏差 SV，并说明此时项目的成本和进度执行状态。
【问题2】（8分）
计算此时的成本绩效指数 CPI 和进度绩效指数 SPI。如果目前的偏差是典型的（即现有偏差将按原趋势继续保持），预测项目的完工尚需估算 ETC 和完工总估算 EAC。
【问题3】（6分）
如果经 CCB 评审，后续工作中发现偏差是非典型的（即后续工作将按计划预算单价执行），预测完工总估算 EAC。项目经理可以采取哪些进度压缩和纠偏措施？""",
            "options": None,
            "correct_answer": """【问题1】（6分）
1. 计划按比例线性执行：PV = 100 * (5/10) = 50 万元（1.5分）
2. EV = BAC * 实际完成比例 = 100 * 40% = 40 万元（1.5分）
3. CV = EV - AC = 40 - 50 = -10 万元 < 0，成本超支（1.5分）
4. SV = EV - PV = 40 - 50 = -10 万元 < 0，进度延误（1.5分）

【问题2】（8分）
1. CPI = EV / AC = 40 / 50 = 0.80（2分）
2. SPI = EV / PV = 40 / 50 = 0.80（2分）
3. 典型偏差情况下：
   - ETC = (BAC - EV) / CPI = (100 - 40) / 0.8 = 75 万元（2分）
   - EAC = BAC / CPI = 100 / 0.8 = 125 万元（或 EAC = AC + ETC = 50 + 75 = 125 万元）（2分）

【问题3】（6分）
1. 非典型偏差情况下：
   - EAC = AC + (BAC - EV) = 50 + (100 - 40) = 110 万元（3分）
2. 进度纠偏与压缩措施（3分）：
   - 赶工（投入优质资源、加班、增加人员）；
   - 快速跟进（并行开展原本串行的活动）；
   - 使用高素质员工或经验丰富人员；
   - 减小活动范围或缩减非关键需求（经客户/CCB审批）；
   - 加强质量控制，减少返工。""",
            "analysis": "【核心考点】EVM基础公式（PV/EV/AC/CV/SV/CPI/SPI）及典型与非典型完工估算（EAC = BAC/CPI vs EAC = AC + BAC - EV），进度压缩两大技术（赶工与快速跟进）。",
            "rubrics": [
                {"point": "PV=50万, EV=40万", "score": 3, "keywords": ["PV=50", "EV=40", "50万", "40万"]},
                {"point": "CV=-10超支, SV=-10延误", "score": 3, "keywords": ["-10", "超支", "延误", "落后"]},
                {"point": "CPI=0.8, SPI=0.8", "score": 4, "keywords": ["0.8", "0.80", "CPI=0.8", "SPI=0.8"]},
                {"point": "典型EAC=125万元", "score": 4, "keywords": ["125", "125万", "125万元"]},
                {"point": "非典型EAC=110万元", "score": 3, "keywords": ["110", "110万", "110万元"]},
                {"point": "赶工与快速跟进措施", "score": 3, "keywords": ["赶工", "快速跟进", "并行", "加班", "减少返工"]}
            ],
            "source": "第3版教程十大领域口诀与EVA经典例题",
            "difficulty": "hard"
        }
    ]
    return cases

def import_to_sqlite(db_path, questions_list):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure table exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id VARCHAR(36) PRIMARY KEY,
        subject VARCHAR(16) NOT NULL,
        chapter VARCHAR(64) NOT NULL,
        knowledge VARCHAR(64) NOT NULL,
        stem TEXT NOT NULL,
        options JSON,
        correct_answer TEXT NOT NULL,
        analysis TEXT,
        rubrics JSON,
        source VARCHAR(32) NOT NULL,
        difficulty VARCHAR(16) DEFAULT 'medium',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()

    inserted = 0
    skipped = 0

    for q in questions_list:
        short_stem = q["stem"][:30]
        cursor.execute("SELECT id FROM questions WHERE stem LIKE ? LIMIT 1", (f"{short_stem}%",))
        if cursor.fetchone():
            skipped += 1
            continue

        qid = f"q_{uuid.uuid4().hex[:12]}"
        opts_json = json.dumps(q.get("options"), ensure_ascii=False) if q.get("options") else None
        rubrics_json = json.dumps(q.get("rubrics"), ensure_ascii=False) if q.get("rubrics") else None

        cursor.execute("""
        INSERT INTO questions (id, subject, chapter, knowledge, stem, options, correct_answer, analysis, rubrics, source, difficulty)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            qid,
            q["subject"],
            q["chapter"],
            q["knowledge"],
            q["stem"],
            opts_json,
            q["correct_answer"],
            q.get("analysis", ""),
            rubrics_json,
            q.get("source", "2025年真题"),
            q.get("difficulty", "medium")
        ))
        inserted += 1

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM questions")
    total = cursor.fetchone()[0]
    conn.close()

    print(f"SQLite [{db_path}] updated! Inserted: {inserted}, Skipped: {skipped}, Total in DB: {total}")
    return inserted, skipped, total

if __name__ == "__main__":
    b1_path = r"E:\code\ruankao\backend\data\ocr_2025_batch1.txt"
    b2_path = r"E:\code\ruankao\backend\data\ocr_2025_batch2.txt"

    all_qs = []

    if os.path.exists(b1_path):
        q1 = parse_choice_questions_from_text(b1_path, "2025年11月中项真题第1批")
        all_qs.extend(q1)

    if os.path.exists(b2_path):
        q2 = parse_choice_questions_from_text(b2_path, "2025年11月中项真题第2批")
        all_qs.extend(q2)

    cases = get_case_questions()
    all_qs.extend(cases)
    print(f"\n>>> Total extracted questions ready: {len(all_qs)}")

    # Save to JSON
    out_json = r"E:\code\ruankao\backend\data\extracted_materials_questions.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_qs, f, ensure_ascii=False, indent=2)
    print(f">>> Saved extracted questions JSON to {out_json}")

    # Import to local SQLite DB
    local_db = r"E:\code\ruankao\backend\data\ruankao.db"
    inserted, skipped, total = import_to_sqlite(local_db, all_qs)
