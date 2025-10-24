
# 가치사슬 매핑(집계)
# 필요 패키지: pandas
import pandas as pd
from pathlib import Path

IN_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "coded_segments.parquet"
OUT_TABLE = Path(__file__).resolve().parents[1] / "outputs" / "tables" / "value_chain_counts.csv"

def main():
    df = pd.read_parquet(IN_PATH)
    # 빈도와 가중 감정점수(폴라리티×가중치) 집계
    agg = df.groupby(["vc_stage", "code"]).agg(
        freq=("code","count"),
        sentiment=("polarity", "sum"),
        weight=("weight","mean")
    ).reset_index()
    # 단계별 합계도 추가
    stage_sum = agg.groupby("vc_stage")["freq"].sum().rename("stage_freq").reset_index()
    out = agg.merge(stage_sum, on="vc_stage", how="left")
    OUT_TABLE.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_TABLE, index=False)
    print(f"[ok] value_chain_counts.csv → {OUT_TABLE}")

if __name__ == "__main__":
    main()
