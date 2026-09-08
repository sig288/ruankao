import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash, create_access_token

sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

def run_tests():
    db = SessionLocal()
    # Ensure test student and admin
    student = db.query(User).filter(User.username == "student_test_e2e").first()
    if not student:
        student = User(username="student_test_e2e", hashed_password=get_password_hash("Pass123!"), role="student")
        db.add(student)
        db.commit()
        db.refresh(student)

    admin = db.query(User).filter(User.username == "admin_test_e2e").first()
    if not admin:
        admin = User(username="admin_test_e2e", hashed_password=get_password_hash("AdminPass123!"), role="admin")
        db.add(admin)
        db.commit()
        db.refresh(admin)

    student_token = create_access_token(student.id)
    admin_token = create_access_token(admin.id)
    db.close()

    client = TestClient(app)
    student_headers = {"Authorization": f"Bearer {student_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    print(">>> 1. Testing GET /api/v1/learn/chapters...")
    r = client.get("/api/v1/learn/chapters", headers=student_headers)
    assert r.status_code == 200, f"Failed chapters: {r.text}"
    chapters = r.json()
    assert len(chapters) == 17, f"Expected 17 chapters, got {len(chapters)}"
    print(f"  [PASS] 17 Chapters loaded. First chapter: {chapters[0]['title']}")

    print("\n>>> 2. Testing GET /api/v1/learn/points...")
    r = client.get("/api/v1/learn/points", headers=student_headers)
    assert r.status_code == 200, f"Failed points: {r.text}"
    points_data = r.json()
    assert points_data["total"] >= 14, f"Expected >=14 points, got {points_data['total']}"
    target_pid = points_data["items"][0]["id"]
    print(f"  [PASS] Points total: {points_data['total']}. Sample: {target_pid}")

    print("\n>>> 3. Testing GET /api/v1/learn/points/{id}...")
    r = client.get(f"/api/v1/learn/points/{target_pid}", headers=student_headers)
    assert r.status_code == 200, f"Failed point detail: {r.text}"
    p_detail = r.json()
    assert p_detail["title"]
    assert "summary_md" in p_detail
    print(f"  [PASS] Point title: '{p_detail['title']}', linked glossary: {len(p_detail['glossary_terms'])}")

    print("\n>>> 4. Testing POST /api/v1/learn/points/{id}/status...")
    r = client.post(f"/api/v1/learn/points/{target_pid}/status", json={"status": "mastered"}, headers=student_headers)
    assert r.status_code == 200, f"Failed status update: {r.text}"
    assert r.json()["status"] == "mastered"
    print("  [PASS] Updated point status to 'mastered'.")

    print("\n>>> 5. Testing GET /api/v1/learn/progress...")
    r = client.get("/api/v1/learn/progress", headers=student_headers)
    assert r.status_code == 200, f"Failed progress: {r.text}"
    prog = r.json()
    assert prog["mastered_points"] >= 1
    assert len(prog["recent_studied"]) >= 1
    print(f"  [PASS] Global progress: {prog['mastered_points']}/{prog['total_points']}, recent: {prog['recent_studied'][0]['title']}")

    print("\n>>> 6. Testing GET /api/v1/learn/points/{id}/practice...")
    r = client.get("/api/v1/learn/points/kp_evm_cpi/practice", headers=student_headers)
    assert r.status_code == 200, f"Failed practice: {r.text}"
    prac = r.json()
    print(f"  [PASS] Retrieved {prac['total']} practice questions for EVM point.")

    print("\n>>> 7. Testing GET /api/v1/learn/glossary...")
    r = client.get("/api/v1/learn/glossary", headers=student_headers)
    assert r.status_code == 200, f"Failed glossary: {r.text}"
    gloss = r.json()
    assert gloss["total"] >= 80, f"PRD requirement: >=80 terms, found {gloss['total']}"
    print(f"  [PASS] Total glossary terms: {gloss['total']} (meets >= 80 PRD requirement).")

    print("\n>>> 8. Testing Glossary Search & Tags...")
    r_search = client.get("/api/v1/learn/glossary?q=EVM", headers=student_headers)
    assert r_search.status_code == 200
    assert r_search.json()["total"] >= 1
    target_gid = r_search.json()["items"][0]["id"]
    print(f"  [PASS] Search 'EVM' matched: {r_search.json()['items'][0]['term_en']}")

    print("\n>>> 9. Testing GET /api/v1/learn/glossary/{id}...")
    r_gdetail = client.get(f"/api/v1/learn/glossary/{target_gid}", headers=student_headers)
    assert r_gdetail.status_code == 200
    gd = r_gdetail.json()
    print(f"  [PASS] Glossary detail: '{gd['term_en']}', tip: '{gd['tip']}'")

    print("\n>>> 10. Testing POST /api/v1/learn/glossary/{id}/status...")
    r_gstatus = client.post(f"/api/v1/learn/glossary/{target_gid}/status", json={"known": "know", "favorited": True}, headers=student_headers)
    assert r_gstatus.status_code == 200
    assert r_gstatus.json()["known"] == "know"
    assert r_gstatus.json()["favorited"] is True
    print("  [PASS] Updated glossary status: known=know, favorited=True.")

    print("\n>>> 11. Testing POST /api/v1/learn/glossary/quiz (10-word generation)...")
    r_quiz = client.post("/api/v1/learn/glossary/quiz", headers=student_headers)
    assert r_quiz.status_code == 200
    quiz_qs = r_quiz.json()
    assert len(quiz_qs) == 10, f"Expected 10 quiz questions, got {len(quiz_qs)}"
    print(f"  [PASS] Generated 10 quiz questions. Q1: {quiz_qs[0]['term_en']} with {len(quiz_qs[0]['options'])} choices.")

    print("\n>>> 12. Testing POST /api/v1/learn/glossary/quiz/submit...")
    quiz_answers = [{"term_id": q["term_id"], "selected_option": q["options"][0]["text"]} for q in quiz_qs]
    r_submit = client.post("/api/v1/learn/glossary/quiz/submit", json={"answers": quiz_answers}, headers=student_headers)
    assert r_submit.status_code == 200
    sub_res = r_submit.json()
    assert "score" in sub_res
    assert len(sub_res["results"]) == 10
    print(f"  [PASS] Quiz submit evaluated. Score: {sub_res['score']}分, Correct count: {sub_res['correct_count']}/10.")

    print("\n>>> 13. Testing Admin Batch Import (Upsert)...")
    sample_import_kp = [{
        "id": "kp_test_import",
        "chapter_id": "CH01",
        "title": "测试导入知识点",
        "frequency": "low",
        "est_minutes": 5,
        "summary_md": "测试导入内容",
        "formula_md": "测试口诀",
        "domain_tags": ["测试"],
        "glossary_ids": [],
        "question_ids": []
    }]
    r_imp_kp = client.post("/api/v1/admin/learn/points/import", json=sample_import_kp, headers=admin_headers)
    assert r_imp_kp.status_code == 200
    print(f"  [PASS] Admin points import: {r_imp_kp.json()['message']}")

    print("\n>>> 14. Testing Wrong Questions Knowledge Filter...")
    r_wq = client.get("/api/v1/wrong-book/wrong-questions", headers=student_headers)
    assert r_wq.status_code == 200
    assert "available_knowledges" in r_wq.json()
    print(f"  [PASS] Wrong questions retrieved with available_knowledges list.")

    print("\n========================================================")
    print("ALL 14 END-TO-END AUTOMATED VERIFICATION TESTS PASSED!")
    print("========================================================")

if __name__ == "__main__":
    run_tests()
