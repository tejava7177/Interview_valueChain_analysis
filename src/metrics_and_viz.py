# 지수 산출 & 시각화
# 필요 패키지: pandas, matplotlib, networkx
import pandas as pd, numpy as np, matplotlib.pyplot as plt, networkx as nx
from pathlib import Path
from unidecode import unidecode

import os
# ----- Font & label language settings -----
# macOS 기본 폰트 우선, 그 외 Nanum/DejaVu로 폴백
plt.rcParams['font.family'] = ['AppleGothic', 'NanumGothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# LABEL_LANG: 'ko' or 'en' (환경변수로 전환 가능)
LABEL_LANG = os.getenv("LABEL_LANG", "ko")

stage_name_map_ko = {
    'inbound_logistics': '조달/수급',
    'operations': '가공/제조',
    'outbound_logistics': '출고/물류',
    'marketing_sales': '마케팅/판매',
    'service': '서비스',
    'tech_dev': '기술개발',
    'hr_mgmt': '인력관리',
    'procurement': '구매',
    'infrastructure': '인프라/정책',
}
stage_name_map_en = {
    'inbound_logistics': 'Inbound',
    'operations': 'Operations',
    'outbound_logistics': 'Outbound',
    'marketing_sales': 'Marketing/Sales',
    'service': 'Service',
    'tech_dev': 'Tech Dev',
    'hr_mgmt': 'HR Mgmt',
    'procurement': 'Procurement',
    'infrastructure': 'Infrastructure',
}
col_name_map_ko = {
    'issue_index': '문제지수',
    'opportunity_index': '기회지수',
    'intensity_index': '강도지수',
}
col_name_map_en = {
    'issue_index': 'Issue Index',
    'opportunity_index': 'Opportunity Index',
    'intensity_index': 'Intensity',
}

def stage_label(s: str) -> str:
    return (stage_name_map_ko if LABEL_LANG == 'ko' else stage_name_map_en).get(s, s)

def col_label(c: str) -> str:
    return (col_name_map_ko if LABEL_LANG == 'ko' else col_name_map_en).get(c, c)

# 코드 라벨(네트워크 그래프용)
label_map_ko = {
    '자동화_부족': '자동화 부족',
    '온라인_브랜딩_역량': '온라인·브랜딩',
    '기술개발_RnD': '기술개발 R&D',
    '정책_표준_인증': '정책·표준/인증',
    '유통_출고_물류': '유통/출고·물류',
    '서비스_AS_유지보수': '서비스/AS',
}
label_map_en = {
    '자동화_부족': 'Automation deficit',
    '온라인_브랜딩_역량': 'Online branding',
    '기술개발_RnD': 'Tech dev (R&D)',
    '정책_표준_인증': 'Policy/Std/Cert',
    '유통_출고_물류': 'Outbound logistics',
    '서비스_AS_유지보수': 'Service/Aftercare',
}

def code_label(code: str) -> str:
    m = label_map_ko if LABEL_LANG == 'ko' else label_map_en
    lbl = m.get(code, code)
    if LABEL_LANG == 'en' and any(ord(ch) > 127 for ch in lbl):
        lbl = unidecode(lbl)  # 한글이면 로마자(ASCII)로 자동 변환
    return lbl

CODED = Path(__file__).resolve().parents[1] / "data" / "processed" / "coded_segments.parquet"
VC_TABLE = Path(__file__).resolve().parents[1] / "outputs" / "tables" / "value_chain_counts.csv"
INDICES_TABLE = Path(__file__).resolve().parents[1] / "outputs" / "tables" / "value_chain_indices.csv"  # 지수표는 별도 파일로 저장하여 counts를 덮어쓰지 않음
FIG_DIR = Path(__file__).resolve().parents[1] / "outputs" / "figures"

def compute_indices(df):
    # 단계별 문제 지수(음수 폴라리티 비중), 기회 지수(양수 폴라리티 비중), 강도 지수(빈도 정규화)
    stage_freq = df.groupby("vc_stage")["code"].count().rename("n").reset_index()
    pol = df.groupby(["vc_stage"])["polarity"].agg(["sum","mean"]).reset_index()
    out = stage_freq.merge(pol, on="vc_stage", how="left")
    out["issue_index"] = df.assign(is_issue=(df["polarity"]<0)).groupby("vc_stage")["is_issue"].mean().values
    out["opportunity_index"] = df.assign(is_opp=(df["polarity"]>0)).groupby("vc_stage")["is_opp"].mean().values
    out["intensity_index"] = out["n"] / out["n"].sum()
    return out

def heatmap_stage_indices(idx):
    fig = plt.figure(figsize=(8,4), dpi=150)
    mat = idx.set_index("vc_stage")[['issue_index','opportunity_index','intensity_index']]
    # 라벨을 선택 언어로 변환
    mat.columns = [col_label(c) for c in mat.columns]
    mat.index = [stage_label(s) for s in mat.index]
    im = plt.imshow(mat.values, aspect="auto")
    plt.xticks(range(mat.shape[1]), mat.columns, rotation=0)
    plt.yticks(range(mat.shape[0]), mat.index)
    plt.colorbar(im, fraction=0.046, pad=0.04)
    plt.title("가치사슬 지표 히트맵" if LABEL_LANG=='ko' else "Value Chain Indices Heatmap")
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / "heatmap_indices.png"
    plt.tight_layout(); plt.savefig(path, dpi=150); plt.close()
    print(f"[ok] {path}")

def cooccurrence_network(df):
    # 같은 세그먼트에서 함께 등장한 코드 쌍
    pairs = (df.groupby(["doc_id","seg_id"])["code"].apply(lambda s: sorted(set(s))).tolist())
    from itertools import combinations
    edges = {}
    for codes in pairs:
        for a,b in combinations(codes, 2):
            key = tuple(sorted((a,b)))
            edges[key] = edges.get(key, 0) + 1
    G = nx.Graph()
    for (a,b), w in edges.items():
        G.add_edge(a,b,weight=w)

    # 레이아웃 및 렌더링(라벨 가독화)
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(9,7), dpi=150)
    nx.draw_networkx_nodes(G, pos, node_size=700)
    weights = [G[u][v]['weight'] for u,v in G.edges()]
    nx.draw_networkx_edges(G, pos, width=[0.5 + w*0.3 for w in weights])
    labels = {n: code_label(n) for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / "cooccurrence_network.png"
    plt.tight_layout(); plt.savefig(path, dpi=150); plt.close()
    print(f"[ok] {path}")

def main():
    df = pd.read_parquet(CODED)
    idx = compute_indices(df)
    idx.to_csv(INDICES_TABLE, index=False)
    heatmap_stage_indices(idx)
    cooccurrence_network(df)

if __name__ == "__main__":
    main()
