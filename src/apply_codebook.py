
# 코드북을 이용해 세그먼트에 코드 부여(룰 기반)
# 필요 패키지: pandas, pyyaml, regex
import pandas as pd, yaml, regex as re
from pathlib import Path

SEG_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "segments.parquet"
CODEBOOK = Path(__file__).resolve().parents[1] / "src" / "codebook.yaml"
OUT_CODES = Path(__file__).resolve().parents[1] / "data" / "processed" / "coded_segments.parquet"

def compile_patterns(synonyms):
    pats = []
    for s in synonyms:
        # 단순 키워드는 부분일치, 정규식이면 그대로 사용
        if s.startswith("(") and s.endswith(")"):
            pats.append(re.compile(s, flags=re.IGNORECASE))
        else:
            pats.append(re.compile(re.escape(s), flags=re.IGNORECASE))
    return pats

def main():
    df = pd.read_parquet(SEG_PATH)
    codebook = yaml.safe_load(open(CODEBOOK, "r", encoding="utf-8"))
    compiled = []
    for item in codebook:
        compiled.append({
            "code": item["code"],
            "vc_stage": item["vc_stage"],
            "polarity": item.get("polarity", 0),
            "weight": item.get("weight", 1.0),
            "patterns": compile_patterns(item.get("synonyms", []))
        })

    rows = []
    for _, r in df.iterrows():
        hits = []
        for c in compiled:
            if any(p.search(r["text"]) for p in c["patterns"]):
                hits.append((c["code"], c["vc_stage"], c["polarity"], c["weight"]))
        if hits:
            for h in hits:
                rows.append({
                    "doc_id": r["doc_id"],
                    "seg_id": r["seg_id"],
                    "text": r["text"],
                    "code": h[0],
                    "vc_stage": h[1],
                    "polarity": h[2],
                    "weight": h[3]
                })
    out = pd.DataFrame(rows)
    OUT_CODES.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT_CODES, index=False)
    print(f"[ok] coded_segments → {OUT_CODES} (rows={len(out)})")

if __name__ == "__main__":
    main()
