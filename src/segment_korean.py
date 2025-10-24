# segment_korean.py (FAST + tqdm + chunk)
import json, pandas as pd, re, os, warnings
from pathlib import Path
warnings.filterwarnings("ignore", category=RuntimeWarning)

IN_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "texts.jsonl"
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "segments.parquet"

FAST = os.getenv("FAST_SEG", "0") == "1"   # FAST 모드 토글: FAST_SEG=1 python ...
CHUNK_CHAR = 2500                           # 청크 크기(문자 수)

# 진행률 표시: tqdm이 없으면 조용히 패스
def _progress(iterable, desc):
    try:
        from tqdm import tqdm
        return tqdm(iterable, desc=desc)
    except Exception:
        return iterable

def split_sentences(text):
    if FAST:
        # 아주 라이트한 규칙 기반 분할(속도↑, 정확도↓)
        # 마침표/물음표/감탄/…/개행 + 종결어미(다/요) 근처를 기준으로 러프하게 끊음
        return [s.strip() for s in re.split(r'(?<=[\.?!…])\s+|(?<=[다요])\s+', text) if s.strip()]
    else:
        try:
            import kss
            return kss.split_sentences(text)  # pecab 백엔드 사용 중
        except ImportError:
            raise SystemExit("kss가 필요합니다: pip install kss")

S1 = re.compile(r"^\s*(?:1:|질문자\s*:?)[ \t]*")
S2 = re.compile(r"^\s*(?:2:|전문가\s*:?)[ \t]*")

def parse_turns(raw_text):
    turns = []
    cur_speaker, buf = None, []
    for line in raw_text.splitlines():
        line = re.sub(r"\s+", " ", line.strip())
        if not line:
            continue
        if S1.match(line):
            if buf:
                turns.append((cur_speaker, " ".join(buf))); buf=[]
            cur_speaker = "interviewer"; buf.append(S1.sub("", line))
        elif S2.match(line):
            if buf:
                turns.append((cur_speaker, " ".join(buf))); buf=[]
            cur_speaker = "expert"; buf.append(S2.sub("", line))
        else:
            buf.append(line)
    if buf:
        turns.append((cur_speaker, " ".join(buf)))
    # 누락 화자 보정
    fixed=[]
    last="interviewer"
    for spk, txt in turns:
        spk = spk or last
        last = spk
        fixed.append((spk, txt))
    return fixed

def chunk_text(text, size=CHUNK_CHAR):
    # 문단/빈줄 기준 우선 -> 너무 길면 고정 길이 청크
    paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    chunks=[]
    for p in paras:
        if len(p) <= size:
            chunks.append(p)
        else:
            for i in range(0, len(p), size):
                chunks.append(p[i:i+size])
    return chunks if chunks else [text]

def main():
    rows=[]
    with open(IN_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in _progress(lines, "Segmenting"):
        rec = json.loads(line)
        turns = parse_turns(rec["text"])

        for t_id, (speaker, utt) in enumerate(turns):
            for ch in chunk_text(utt):
                sents = split_sentences(ch)
                for i, sent in enumerate(sents):
                    if sent:
                        rows.append({
                            "doc_id": rec["id"],
                            "turn_id": t_id,
                            "speaker": speaker,
                            "seg_id": i,
                            "text": sent
                        })

    df = pd.DataFrame(rows)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PATH, index=False)
    print(f"[ok] segments → {OUT_PATH} (rows={len(df)})")

if __name__ == "__main__":
    main()