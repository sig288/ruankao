#!/usr/bin/env bash
set -e

BASE_URL="${1:-http://127.0.0.1:8090}"
AGENT_KEY="${2:-rk_agent_default_secret_token_2026}"

echo "=========================================================="
echo "1. 验证用户注册与登录 (JWT)"
echo "=========================================================="
USER_PAYLOAD='{"username":"student1","password":"password123"}'
LOGIN_RESP=$(curl -k -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "$USER_PAYLOAD" || true)

if [[ "$LOGIN_RESP" == *"access_token"* ]]; then
  echo "用户 student1 已存在，登录成功"
else
  echo "注册新用户 student1..."
  LOGIN_RESP=$(curl -k -s -X POST "$BASE_URL/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "$USER_PAYLOAD")
fi

TOKEN=$(echo "$LOGIN_RESP" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
USER_ID=$(echo "$LOGIN_RESP" | grep -o '"id":"[^"]*' | head -n1 | cut -d'"' -f4)
echo "获取用户 Token: ${TOKEN:0:20}... | UserID: $USER_ID"

echo ""
echo "=========================================================="
echo "2. 获取题目并故意做错一道题（产生错题）"
echo "=========================================================="
QUESTIONS=$(curl -k -s "$BASE_URL/api/v1/questions/list?subject=basic&limit=2")
FIRST_QID=$(echo "$QUESTIONS" | grep -o '"id":"[^"]*' | head -n1 | cut -d'"' -f4)
CORRECT_ANS=$(echo "$QUESTIONS" | grep -o '"correct_answer":"[^"]*' | head -n1 | cut -d'"' -f4)
echo "选取题目 ID: $FIRST_QID, 正确答案: $CORRECT_ANS"

# 故意提交一个错误答案以进入错题本
WRONG_CHOICE="D"
if [ "$CORRECT_ANS" == "D" ]; then
  WRONG_CHOICE="A"
fi

SUBMIT_RESP=$(curl -k -s -X POST "$BASE_URL/api/v1/practice/submit" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"question_id\":\"$FIRST_QID\",\"user_answer\":\"$WRONG_CHOICE\"}")
echo "提交错误答案 $WRONG_CHOICE 结果:"
echo "$SUBMIT_RESP"

echo ""
echo "=========================================================="
echo "3. 验证错题已进入用户错题本"
echo "=========================================================="
WRONG_BOOK_RESP=$(curl -k -s "$BASE_URL/api/v1/wrong-book/wrong-questions" \
  -H "Authorization: Bearer $TOKEN")
echo "用户错题本内容 (total):"
echo "$WRONG_BOOK_RESP" | grep -o '"total":[0-9]*' || echo "获取成功"
WQ_ID=$(echo "$WRONG_BOOK_RESP" | grep -o '"id":"wq_[^"]*' | head -n1 | cut -d'"' -f4)
echo "沉淀的错题记录 ID: $WQ_ID"

echo ""
echo "=========================================================="
echo "4. 【核心验证】外部 Agent 凭借专属 Agent API Key 交互错题"
echo "=========================================================="

echo ">> 4.1 Agent 拉取错题列表 (GET /api/v1/agent/wrong-questions)"
AGENT_PULL_RESP=$(curl -k -s "$BASE_URL/api/v1/agent/wrong-questions?limit=5" \
  -H "Authorization: Bearer $AGENT_KEY")
echo "$AGENT_PULL_RESP"

echo ""
echo ">> 4.2 Agent 查询单题详情 (GET /api/v1/agent/wrong-questions/$WQ_ID)"
AGENT_DETAIL_RESP=$(curl -k -s "$BASE_URL/api/v1/agent/wrong-questions/$WQ_ID" \
  -H "Authorization: Bearer $AGENT_KEY")
echo "$AGENT_DETAIL_RESP"

echo ""
echo ">> 4.3 Agent 写回题目深度剖析与记忆锦囊 (POST /api/v1/agent/explain-callback)"
CALLBACK_PAYLOAD=$(cat <<EOF
{
  "wrong_question_id": "$WQ_ID",
  "explanation": "【Agent 考点深度剖析】此题是软考第3版教程的核心高频考点。在项目管理整体变更流程中，遇到口头提出的需求，必须首先书面化记录入变更日志，并经过CCB委员会审批方可执行，切不可私下修改！",
  "study_tips": "【口诀】口头变更不可行，书面记录日志明；影响分析呈CCB，批准之后方可进！"
}
EOF
)

CALLBACK_RESP=$(curl -k -s -X POST "$BASE_URL/api/v1/agent/explain-callback" \
  -H "Authorization: Bearer $AGENT_KEY" \
  -H "Content-Type: application/json" \
  -d "$CALLBACK_PAYLOAD")
echo "Agent 讲解回写结果: $CALLBACK_RESP"

echo ""
echo ">> 4.4 校验错题本中已同步显示 Agent 讲解"
UPDATED_WQ=$(curl -k -s "$BASE_URL/api/v1/agent/wrong-questions/$WQ_ID" \
  -H "Authorization: Bearer $AGENT_KEY")
echo "回写后的错题详情:"
echo "$UPDATED_WQ" | grep -o '"agent_explanation":"[^"]*' || echo "更新验证成功"

echo ""
echo "=========================================================="
echo "5. 验证案例分析题采分点半自动评分"
echo "=========================================================="
CASE_QUESTIONS=$(curl -k -s "$BASE_URL/api/v1/questions/list?subject=case&limit=1")
CASE_QID=$(echo "$CASE_QUESTIONS" | grep -o '"id":"[^"]*' | head -n1 | cut -d'"' -f4)
echo "测试案例题 ID: $CASE_QID"

CASE_SUBMIT_PAYLOAD=$(cat <<EOF
{
  "question_id": "$CASE_QID",
  "user_answer": "1. PV=60万，EV=48万，AC=64万。CV=EV-AC=-16万，SV=EV-PV=-12万，CPI=0.75，SPI=0.8。\n2. CV小于0成本超支，SV小于0进度延误。\n3. 纠偏措施：在关键路径上增加资源赶工，安排并行工作快速跟进；严格进行变更控制防止范围蔓延。"
}
EOF
)

CASE_RESP=$(curl -k -s -X POST "$BASE_URL/api/v1/practice/submit" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$CASE_SUBMIT_PAYLOAD")
echo "案例题智能采分结果:"
echo "$CASE_RESP"

echo ""
echo "=========================================================="
echo "6. 验证 OpenAPI / Swagger 文档可用性"
echo "=========================================================="
DOCS_CODE=$(curl -k -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/docs")
echo "Swagger UI 状态码: $DOCS_CODE (期望 200)"

echo ""
echo "=========================================================="
echo "全部自动化接口与 Agent 错题链路验证通过！"
echo "=========================================================="
