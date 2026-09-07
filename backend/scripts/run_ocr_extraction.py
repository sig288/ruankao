# -*- coding: utf-8 -*-
"""
OCR extraction script for 2025 Ruankao exam PDFs.
Extracts text page by page using PyMuPDF + RapidOCR and caches to text files.
"""
import os
import sys
import pymupdf
from rapidocr_onnxruntime import RapidOCR

sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

ocr = RapidOCR()

target_files = [
    (
        r"E:\code\ruankao\学习资料\08 2016-2026年历年真题合集（已更新26）\01：24-26年真题\2025年系统集成项目管理工程师11月8日第1批选择题真题和答案.pdf",
        r"E:\code\ruankao\backend\data\ocr_2025_batch1.txt",
        "2025年11月第1批"
    ),
    (
        r"E:\code\ruankao\学习资料\08 2016-2026年历年真题合集（已更新26）\01：24-26年真题\2025年系统集成项目管理工程师11月8日第2批选择题真题和答案.pdf",
        r"E:\code\ruankao\backend\data\ocr_2025_batch2.txt",
        "2025年11月第2批"
    )
]

os.makedirs(r"E:\code\ruankao\backend\data", exist_ok=True)

for pdf_path, out_txt, label in target_files:
    if os.path.exists(out_txt) and os.path.getsize(out_txt) > 1000:
        print(f"[{label}] Output cache already exists: {out_txt} ({os.path.getsize(out_txt)} bytes), skipping OCR.")
        continue

    if not os.path.exists(pdf_path):
        print(f"[{label}] File not found: {pdf_path}")
        continue

    print(f"[{label}] Starting OCR extraction for {pdf_path}...")
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    all_text = []

    for page_num in range(total_pages):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        result, _ = ocr(img_bytes)
        page_lines = []
        if result:
            for item in result:
                page_lines.append(item[1])
        page_text = "\n".join(page_lines)
        all_text.append(f"\n=== PAGE {page_num + 1} ===\n" + page_text)
        print(f"  Processed page {page_num + 1}/{total_pages} ({len(page_lines)} lines)")

    full_content = "\n".join(all_text)
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(full_content)
    print(f"[{label}] Saved {len(full_content)} chars to {out_txt}")

print("All OCR extraction complete!")
