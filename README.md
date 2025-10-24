
# Bamboo Value Chain × Open Coding (Python) — Starter Kit

이 저장소는 인터뷰 PDF(9명)를 기반으로 **개방 코딩 → 축 코딩 → 선택 코딩 → 가치사슬 매핑**을 정량화하는 분석 파이프라인의 골격입니다.

## 폴더 구조
```
bamboo_value_chain_starter/
  ├─ data/
  │   ├─ raw/                # 인터뷰 원본 PDF 넣기
  │   └─ processed/          # 추출/세그먼트/라벨링 중간 산출물
  ├─ outputs/
  │   ├─ figures/            # 히트맵/네트워크/샌키 등 그래프
  │   └─ tables/             # 빈도표/지수표/요약표
  ├─ src/
  │   ├─ extract_text.py
  │   ├─ segment_korean.py
  │   ├─ discover_codes.py
  │   ├─ codebook.yaml       # 코드북(사전) — 수동으로 편집
  │   ├─ apply_codebook.py
  │   ├─ map_value_chain.py
  │   ├─ metrics_and_viz.py
  │   └─ generate_report.py
  ├─ config/
  │   └─ metadata.csv        # 인터뷰이 메타데이터(역할/지역/날짜 등)
  └─ notebooks/
      └─ 00_quickstart.md    # 빠른 시작 가이드
```

## 사용 흐름
1) `data/raw` 폴더에 인터뷰 PDF를 넣습니다. 파일명 규칙 예: `I01_제조_2025-08-12.pdf`
2) `config/metadata.csv`에 인터뷰이 역할/지역/날짜 등을 정리합니다.
3) `python src/extract_text.py` → PDF에서 텍스트 추출
4) `python src/segment_korean.py` → 문장/발화 단위로 세그먼트화
5) `python src/discover_codes.py` → 자동 코드 후보(키프레이즈/주제) 탐색
6) `config/codebook.yaml`(사전) 편집 → 코드북 확정
7) `python src/apply_codebook.py` → 코드북을 세그먼트에 적용(빈도/공동출현 계산)
8) `python src/map_value_chain.py` → 가치사슬 카테고리로 매핑
9) `python src/metrics_and_viz.py` → 히트맵/네트워크/지수 산출
10) `python src/generate_report.py` → Markdown 보고서 초안 생성

> 일부 패키지(예: `kss`, `pandas`, `matplotlib`, `scikit-learn`, `networkx`) 설치가 필요할 수 있습니다.
