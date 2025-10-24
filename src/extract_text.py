
# PDF → 텍스트 추출
# 필요 패키지: PyPDF2 (간단 텍스트 PDF), OCR 필요 시 OCRmyPDF/ Tesseract 사용 권장
import os, json
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "texts.jsonl"

def extract_pdf_text(pdf_path):
    try:
        import PyPDF2
    except ImportError:
        raise SystemExit("PyPDF2 패키지를 설치하세요: pip install PyPDF2")
    text = []
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            t = page.extract_text() or ""
            text.append(t)
    return "\n".join(text)

def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    for name in os.listdir(RAW_DIR):
        if name.lower().endswith(".pdf"):
            pdf_path = RAW_DIR / name
            doc_id = os.path.splitext(name)[0]
            txt = extract_pdf_text(pdf_path)
            rec = {"id": doc_id, "text": txt}
            with open(OUT_PATH, "a", encoding="utf-8") as out:
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(f"[ok] {name} → texts.jsonl")

if __name__ == "__main__":
    main()
