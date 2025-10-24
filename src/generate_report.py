
# Markdown 보고서 자동 생성(초안)
import pandas as pd, datetime
from pathlib import Path

VC_TABLE = Path(__file__).resolve().parents[1] / "outputs" / "tables" / "value_chain_counts.csv"
FIG_DIR = Path(__file__).resolve().parents[1] / "outputs" / "figures"
OUT_MD = Path(__file__).resolve().parents[1] / "outputs" / "bamboo_value_chain_report.md"

def main():
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    lines.append("# 대나무 산업 이윤 추구: 가치사슬 × 개방 코딩 분석 보고서")
    lines.append("")
    lines.append(f"- 생성 시각: {ts}")
    lines.append("")
    lines.append("## 1) 요약")
    lines.append("- 본 보고서는 인터뷰 텍스트를 코딩하여 가치사슬 단계별 문제/기회/강도를 정량화하였습니다.")
    lines.append("")
    lines.append("## 2) 가치사슬 지표(요약)")
    if VC_TABLE.exists():
        df = pd.read_csv(VC_TABLE)
        stage_summary = df.groupby("vc_stage")["freq"].sum().sort_values(ascending=False)
        lines.append("**빈도 상위 단계**")
        for stage, n in stage_summary.items():
            lines.append(f"- {stage}: {int(n)}")
    else:
        lines.append("- (테이블이 아직 생성되지 않았습니다)")
    lines.append("")
    lines.append("## 3) 시각화")
    for name in ["heatmap_indices.png", "cooccurrence_network.png"]:
        p = FIG_DIR / name
        if p.exists():
            lines.append(f"![{name}](figures/{name})")
    lines.append("")
    lines.append("## 4) 주요 인사이트 후보")
    lines.append("- (예시) Inbound: 수급 불안정, 중국산 의존 → 원료 안정화 전략 필요")
    lines.append("- (예시) Operations: 자동화 설비 부족 → 생산성 개선 투자 포인트")
    lines.append("- (예시) Marketing & Sales: 브랜드 인지도 부족 → 프리미엄 포지셔닝/브랜딩 강화")
    lines.append("")
    lines.append("## 5) 전략적 개입 포인트(초안)")
    lines.append("- (예시) 원자재 공동구매/계약재배, 설비 현대화, 산지-도시 연계 브랜딩, 작가/디자이너 협업 등")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"[ok] report → {{OUT_MD}}")

if __name__ == "__main__":
    main()
