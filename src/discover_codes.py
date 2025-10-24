# discover_codes.py (개선판)
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
import regex as re

SEG_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "segments.parquet"
OUT_PHRASES = Path(__file__).resolve().parents[1] / "outputs" / "tables" / "candidate_phrases.csv"
OUT_TOPICS  = Path(__file__).resolve().parents[1] / "outputs" / "tables" / "topics.csv"

# 1) 한국어/대화 불용어 + 도메인 불용어(초안) — 필요시 자유롭게 추가/삭제
STOPWORDS = set("""
이제 그러면 근데 그런 이렇게 하고 이게 지금 그래서 그냥 그리고 그런데 그러니까 네 음 어 아 예
거든요 거죠 거에요 거예요 그게 저희 저기 여기 거나 뭐냐 뭐가 뭐든 뭐라고 뭐든지 어떤 어떤가
입니다 입니다만 거고 거고요 거면 그렇게 그런가요 또한 또한요 또한은 또한으로
대나무 제품 사람 부분 상황 경우 사실 좀 그냥 많이 혹시 거의 또는 그리고 그러나 또한 또는
""".split())

# 자질구레한 한 글자/숫자/영문과 섞인 토큰 제거를 위한 전처리(라이트)
def clean_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = re.sub(r"[^\p{Hangul}A-Za-z0-9\s\-/&+]", " ", s)     # 한글 외 기호 제거(라이트)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def filter_stopwords(tokens):
    return [t for t in tokens if t and t not in STOPWORDS and len(t) > 1]

def korean_tokenizer(text):
    text = clean_text(text)
    # 한글 2자 이상 토큰만
    toks = re.findall(r"(?:\p{Hangul}{2,}|[A-Za-z]{2,}|\d{2,})", text)
    return filter_stopwords(toks)

def tfidf_top_phrases(texts, ngram=(2,3), min_df=3, max_df=0.7, topn=3000):
    vec = TfidfVectorizer(
        tokenizer=korean_tokenizer,
        ngram_range=ngram,
        min_df=min_df,
        max_df=max_df,
        max_features=topn,
        lowercase=False,
        token_pattern=None # 커스텀 tokenizer 사용
    )
    X = vec.fit_transform(texts)
    feat = vec.get_feature_names_out()
    import numpy as np
    avg = X.mean(axis=0).A1
    order = np.argsort(-avg)
    return [(feat[i], float(avg[i])) for i in order]

def run_nmf(texts, n_topics=8, n_terms=12, ngram=(2,3), min_df=3, max_df=0.7):
    vec = TfidfVectorizer(
        tokenizer=korean_tokenizer,
        ngram_range=ngram,
        min_df=min_df,
        max_df=max_df,
        lowercase=False,
        token_pattern=None
    )
    X = vec.fit_transform(texts)
    feat = vec.get_feature_names_out()
    nmf = NMF(n_components=n_topics, random_state=42, init="nndsvd")
    W = nmf.fit_transform(X)
    H = nmf.components_
    import numpy as np
    topics = []
    for t in range(n_topics):
        top_idx = np.argsort(-H[t])[:n_terms]
        terms = [feat[i] for i in top_idx]
        topics.append({"topic": t, "terms": ", ".join(terms)})
    return topics

def main():
    df = pd.read_parquet(SEG_PATH)

    # 2) 전문가 발화만 대상으로 후보 추출
    if "speaker" in df.columns:
        df = df[df["speaker"] == "expert"].copy()

    texts = df["text"].astype(str).tolist()

    # 3) 우선 bigram/trigram 기반 후보
    phrases = tfidf_top_phrases(texts, ngram=(2,3), min_df=3, max_df=0.7, topn=3000)
    pd.DataFrame(phrases, columns=["phrase","score"]).to_csv(OUT_PHRASES, index=False)

    # 4) NMF 토픽도 동일 규격으로 산출
    topics = run_nmf(texts, n_topics=8, n_terms=12, ngram=(2,3), min_df=3, max_df=0.7)
    pd.DataFrame(topics).to_csv(OUT_TOPICS, index=False)

    print("[ok] candidate_phrases.csv / topics.csv (정제 버전) 생성")

if __name__ == "__main__":
    main()