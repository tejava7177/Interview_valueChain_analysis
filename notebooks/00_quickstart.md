
# 00_quickstart

## 빠른 시작
- `data/raw/`에 PDF 9개 넣기
- `config/metadata.csv` 편집
- 아래 명령을 순서대로 실행

```bash
python src/extract_text.py
python src/segment_korean.py
python src/discover_codes.py
# 코드북 편집: src/codebook.yaml
python src/apply_codebook.py
python src/map_value_chain.py
python src/metrics_and_viz.py
python src/generate_report.py
```
