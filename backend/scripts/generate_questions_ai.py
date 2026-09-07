"""
AI Question Generation & Batch Importer CLI Tool
"""
import sys
import json
import argparse
import requests

def validate_question(q: dict) -> bool:
    required = ["subject", "chapter", "knowledge", "stem", "correct_answer"]
    for r in required:
        if r not in q:
            print(f"Missing required field: {r}")
            return False
    if q["subject"] == "basic" and (not q.get("options") or len(q["options"]) < 2):
        print("Basic question must have at least 2 options")
        return False
    return True

def import_to_server(api_base: str, admin_token: str, json_file: str):
    with open(json_file, "r", encoding="utf-8") as f:
        questions = json.load(f)

    valid_questions = []
    for q in questions:
        q["source"] = "ai-generated"
        if validate_question(q):
            valid_questions.append(q)

    print(f"Validating {len(valid_questions)} / {len(questions)} questions...")
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }

    url = f"{api_base.rstrip('/')}/api/v1/admin/import-questions"
    resp = requests.post(url, headers=headers, json=valid_questions)
    if resp.status_code == 200:
        print("Import successful!", resp.json())
    else:
        print(f"Import failed ({resp.status_code}):", resp.text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch Import AI Generated Questions")
    parser.add_argument("--file", required=True, help="Path to JSON file containing questions")
    parser.add_argument("--api", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--token", default="", help="Admin JWT Token")
    args = parser.parse_args()

    import_to_server(args.api, args.token, args.file)
